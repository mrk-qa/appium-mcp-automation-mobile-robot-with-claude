"""Lint das convenções Robot do projeto (camada determinística do revisor-robot).

Confere as regras invioláveis e as convenções do CLAUDE.md que podem ser verificadas sem device:
locator cru, Sleep, tempo fixo, leitura sem retentativa, rastreabilidade com o cenário, tags,
evidências (📸 × Registrar Evidência), senha fora das massas e defeito-conhecido sem registro.
No modo completo, roda também o Robocop (lint da comunidade) e o dry-run do Robot (keywords e argumentos).

Uso (na raiz do repositório):
    python .claude/scripts/lint_robot.py                     # tudo: regras + Robocop + dry-run
    python .claude/scripts/lint_robot.py --arquivo <path>    # um arquivo, modo rápido (hook PostToolUse)
    python .claude/scripts/lint_robot.py --json              # saída em JSON
    python .claude/scripts/lint_robot.py --aprovar           # roda tudo e, sem erros, grava a aprovação
    python .claude/scripts/lint_robot.py --status            # a aprovação vale para os arquivos atuais?

Saída: código 0 sem erros (avisos não bloqueiam); 1 com erros; 2 em --status sem aprovação válida.
A aprovação (.claude/revisao-robot.local.json) guarda o hash de tests/robot, tests/pages e tests/resources;
qualquer alteração nesses arquivos a invalida. Só o subagente revisor-robot deve usar --aprovar.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ROBOT_DIR = ROOT / "tests" / "robot"
PAGES_DIR = ROOT / "tests" / "pages"
RESOURCES_DIR = ROOT / "tests" / "resources"
USERS_FILE = ROOT / "tests" / "massas" / "users.yaml"
LIMITACOES = ROOT / "context" / "descobertas" / "limitacoes-conhecidas.md"
APROVACAO = ROOT / ".claude" / "revisao-robot.local.json"

SUITE_RESOURCE = "../../resources/suite.resource"
SETUP_PADRAO = "Iniciar App Autenticado"
TEARDOWN_PADRAO = "Encerrar Aplicativo"
TAG_STATUS = "defeito-conhecido"

RE_ID_TESTE = re.compile(r"^([A-Z]+-\d{3}) \S")
RE_LOCATOR_CRU = re.compile(
    r"(?<![\w$])(id|xpath|accessibility_id|android|class|name|-android uiautomator)=|(?<![:\w])//\w"
)
RE_TEMPO_FIXO = re.compile(
    r"(?<![\w$.])\d+(?:\.\d+)?\s?(?:s|sec|secs|second|seconds|m|min|mins|minute|minutes|h|hour|hours)\b",
    re.IGNORECASE,
)
RE_TAG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
RE_DOC_CENARIO = re.compile(r"Cenário:\s*(context/cenarios/\S+\.md)")
RE_EVIDENCIA_MD = re.compile(r"📸\s*([\w-]+)")
RE_CRITERIO_MD = re.compile(r"^\s*- \[[ xX]\]\s+(.*)$")
RE_SECAO = re.compile(r"^\*\*\*\s*(.+?)\s*\*\*\*")
SEP = re.compile(r"\s{2,}|\t")


@dataclass
class Achado:
    regra: str
    severidade: str  # erro | aviso | info
    arquivo: str
    linha: int
    mensagem: str


# --------------------------------------------------------------------------- leitura de arquivos Robot

@dataclass
class Linha:
    numero: int
    texto: str          # linha sem o comentário final
    celulas: list[str]  # separadas por 2+ espaços (a 1ª vazia quando indentada)
    secao: str


def ler_robot(caminho: Path) -> list[Linha]:
    linhas: list[Linha] = []
    secao = ""
    for numero, bruta in enumerate(caminho.read_text(encoding="utf-8").splitlines(), start=1):
        m = RE_SECAO.match(bruta)
        if m:
            secao = m.group(1).lower()
            continue
        sem_comentario = re.split(r"(?:^|\s{2,}|\t)#", bruta, maxsplit=1)[0].rstrip()
        celulas = SEP.split(sem_comentario) if sem_comentario else []
        linhas.append(Linha(numero, sem_comentario, celulas, secao))
    return linhas


def rel(caminho: Path) -> str:
    try:
        return caminho.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return caminho.as_posix()


def e_documentacao(linha: Linha, em_doc: bool) -> bool:
    """Linha de [Documentation]/Documentation ou continuação dela (texto livre, não é chamada)."""
    primeira = next((c for c in linha.celulas if c), "")
    if primeira in ("[Documentation]", "Documentation"):
        return True
    return em_doc and primeira == "..."


@dataclass
class Teste:
    nome: str
    linha: int
    arquivo: Path
    corpo: list[Linha]
    documentacao: str = ""
    tags: tuple[str, ...] = ()


def extrair_testes(caminho: Path, linhas: list[Linha]) -> list[Teste]:
    testes: list[Teste] = []
    atual: Teste | None = None
    for linha in linhas:
        if linha.secao not in ("test cases", "tasks"):
            continue
        if linha.texto and not linha.texto[0].isspace():
            atual = Teste(linha.texto.strip(), linha.numero, caminho, [])
            testes.append(atual)
        elif atual and linha.texto.strip():
            atual.corpo.append(linha)
    for teste in testes:
        doc: list[str] = []
        em_doc = False
        for linha in teste.corpo:
            cel = [c for c in linha.celulas if c]
            if not cel:
                continue
            if cel[0] == "[Documentation]":
                em_doc = True
                doc.extend(cel[1:])
            elif cel[0] == "..." and em_doc:
                doc.extend(cel[1:])
            else:
                em_doc = False
                if cel[0] == "[Tags]":
                    teste.tags = tuple(cel[1:])
        teste.documentacao = " ".join(doc)
    return testes


def chamadas(teste: Teste) -> list[tuple[int, list[str]]]:
    """Linhas executáveis do teste: (número, células sem a indentação)."""
    saida = []
    em_doc = False
    for linha in teste.corpo:
        cel = [c for c in linha.celulas if c]
        if not cel:
            continue
        if cel[0] == "[Documentation]" or (cel[0] == "..." and em_doc):
            em_doc = True
            continue
        em_doc = False
        if cel[0].startswith("["):
            continue
        saida.append((linha.numero, cel))
    return saida


def settings(linhas: list[Linha]) -> dict[str, list[tuple[int, list[str]]]]:
    resultado: dict[str, list[tuple[int, list[str]]]] = {}
    for linha in linhas:
        if linha.secao != "settings" or not linha.celulas or not linha.celulas[0]:
            continue
        resultado.setdefault(linha.celulas[0].lower(), []).append((linha.numero, linha.celulas[1:]))
    return resultado


# --------------------------------------------------------------------------- dados auxiliares

def senhas_das_massas() -> list[str]:
    if not USERS_FILE.exists():
        return []
    texto = USERS_FILE.read_text(encoding="utf-8")
    try:
        import yaml  # noqa: PLC0415

        dados = yaml.safe_load(texto) or {}
        valores = [str((m or {}).get("senha", "")) for m in dados.values() if isinstance(m, dict)]
    except Exception:  # noqa: BLE001 - sem PyYAML: leitura simples
        valores = [v.strip().strip("\"'") for v in re.findall(r"^\s*senha:\s*(.+)$", texto, re.MULTILINE)]
    return sorted({v for v in valores if len(v) >= 4})


def ler_cenario(caminho: Path) -> dict:
    texto = caminho.read_text(encoding="utf-8")
    campo = lambda nome: (re.search(rf"^- \*\*{nome}:\*\*\s*(.+)$", texto, re.MULTILINE) or [None, ""])[1]  # noqa: E731
    secao_esperado = texto.split("## Resultado esperado", 1)[-1].split("\n## ", 1)[0] if "## Resultado esperado" in texto else ""
    return {
        "id": campo("ID").split()[0] if campo("ID") else "",
        "tags": [t.strip() for t in campo("Tags").split(",") if t.strip()],
        "evidencias": RE_EVIDENCIA_MD.findall(texto),
        "criterios": [m.group(1) for m in map(RE_CRITERIO_MD.match, secao_esperado.splitlines()) if m],
    }


# --------------------------------------------------------------------------- regras

def checar_linhas_comuns(caminho: Path, linhas: list[Linha], senhas: list[str], achados: list[Achado]) -> None:
    """Regras que valem para .robot e .resource: Sleep, tempo fixo, leitura sem retentativa, senha."""
    nome = caminho.name
    e_infra = nome == "infraestrutura.resource"
    e_init = nome == "__init__.robot"
    em_doc = False
    for linha in linhas:
        if not linha.celulas:
            continue
        em_doc = e_documentacao(linha, em_doc)
        if em_doc:
            continue
        cel = [c for c in linha.celulas if c]
        texto = " ".join(cel)
        if any(senha in texto for senha in senhas):
            achados.append(Achado("R09", "erro", rel(caminho), linha.numero,
                                  "Senha de massa escrita no arquivo: use ${USUARIOS}[<massa>][senha] e `Preencher Senha` (regra 4)."))
        if linha.secao not in ("keywords", "test cases", "tasks", "settings", "variables"):
            continue
        if any(c.lower() == "sleep" for c in cel):
            achados.append(Achado("R02", "erro", rel(caminho), linha.numero,
                                  "`Sleep` é proibido: espere um estado com `Wait Until ...` e ${TIMEOUT} (regra 2)."))
        if "Element Text Should Be" in cel and not e_infra:
            achados.append(Achado("R04", "erro", rel(caminho), linha.numero,
                                  "Leitura sem retentativa: use `Validar Texto Do Elemento` (ids reutilizados entre telas)."))
        if linha.secao == "variables" and cel[0] == "${TIMEOUT}" and e_infra:
            continue
        if linha.secao == "settings" and cel[0].lower() == "test timeout":
            if not e_init:
                achados.append(Achado("R03", "erro", rel(caminho), linha.numero,
                                      "`Test Timeout` só em tests/robot/__init__.robot (teto único de 5 minutos)."))
            continue
        alvo = cel[1:] if linha.secao in ("variables",) else cel
        for celula in alvo:
            if RE_TEMPO_FIXO.fullmatch(celula.strip()) or (RE_TEMPO_FIXO.search(celula) and "timeout" in celula.lower()):
                achados.append(Achado("R03", "erro", rel(caminho), linha.numero,
                                      f"Tempo fixo `{celula}`: use ${{TIMEOUT}} (para app lento: --variable TIMEOUT:<valor>)."))


def checar_suite(caminho: Path, linhas: list[Linha], ctx: dict, achados: list[Achado]) -> None:
    arq = rel(caminho)
    cfg = settings(linhas)
    funcionalidade = caminho.parent.name

    resources = [c[0] for _, c in cfg.get("resource", []) if c]
    if resources != [SUITE_RESOURCE]:
        achados.append(Achado("R08", "erro", arq, 1, f"A suíte deve importar só `Resource    {SUITE_RESOURCE}` (encontrado: {resources or 'nenhum'})."))
    for numero, _ in cfg.get("library", []) + cfg.get("variables", []):
        achados.append(Achado("R08", "erro", arq, numero, "Suítes não importam Library/Variables: tudo vem de suite.resource."))
    setup = [c for _, c in cfg.get("test setup", [])]
    if not setup or setup[0][:1] != [SETUP_PADRAO]:
        achados.append(Achado("R08", "erro", arq, 1, f"`Test Setup    {SETUP_PADRAO}` é obrigatório."))
    teardown = [c for _, c in cfg.get("test teardown", [])]
    if not teardown or teardown[0][:1] != [TEARDOWN_PADRAO]:
        achados.append(Achado("R08", "erro", arq, 1, f"`Test Teardown    {TEARDOWN_PADRAO}` é obrigatório."))
    test_tags = [t for _, c in cfg.get("test tags", []) for t in c]
    if test_tags != [funcionalidade]:
        achados.append(Achado("R07", "erro", arq, 1, f"`Test Tags` deve ser só a funcionalidade `{funcionalidade}` (encontrado: {test_tags or 'nenhum'})."))

    for teste in extrair_testes(caminho, linhas):
        m = RE_ID_TESTE.match(teste.nome)
        if not m:
            achados.append(Achado("R06", "erro", arq, teste.linha, f"Nome do teste deve ser `<ID> <Título>` (ex.: CART-001 ...): `{teste.nome}`."))
            continue
        id_teste = m.group(1)
        if id_teste in ctx["ids"]:
            achados.append(Achado("R17", "erro", arq, teste.linha, f"ID {id_teste} duplicado (também em {ctx['ids'][id_teste]})."))
        ctx["ids"][id_teste] = arq

        # tags
        for tag in teste.tags:
            if tag == TAG_STATUS:
                continue
            if not RE_TAG.match(tag):
                achados.append(Achado("R07", "erro", arq, teste.linha, f"Tag `{tag}` fora do padrão kebab-case minúsculo."))
            if tag.lower() in ("smoke", id_teste.lower()) or re.fullmatch(r"[a-z]+-\d{3}", tag.lower()):
                achados.append(Achado("R07", "erro", arq, teste.linha, f"Tag `{tag}` proibida: sem `smoke` e sem tag de ID; a tag diz o objetivo."))
        objetivos = [t for t in teste.tags if t != TAG_STATUS]
        if not objetivos:
            achados.append(Achado("R07", "erro", arq, teste.linha, "`[Tags]` precisa do objetivo do teste (ex.: remover-item)."))
        if TAG_STATUS in teste.tags and LIMITACOES.exists() and id_teste not in LIMITACOES.read_text(encoding="utf-8"):
            achados.append(Achado("R16", "erro", arq, teste.linha,
                                  f"`{TAG_STATUS}` sem registro: cite {id_teste} em context/descobertas/limitacoes-conhecidas.md (regra 3)."))

        # locator cru e Setup
        passos = chamadas(teste)
        for numero, cel in passos:
            for c in cel:
                if RE_LOCATOR_CRU.search(c):
                    achados.append(Achado("R01", "erro", arq, numero, f"Locator cru `{c}` no teste: mova para `${{LOC_*}}` em tests/pages/ (regra 2)."))
        for linha in teste.corpo:
            cel = [c for c in linha.celulas if c]
            if cel[:1] == ["[Setup]"] and cel[1:2] != [SETUP_PADRAO]:
                achados.append(Achado("R08", "erro", arq, linha.numero, f"`[Setup]` só para trocar a massa: `[Setup]    {SETUP_PADRAO}    <massa>`."))

        # cenário
        m_doc = RE_DOC_CENARIO.search(teste.documentacao)
        if not m_doc:
            achados.append(Achado("R05", "erro", arq, teste.linha, "`[Documentation]    Cenário: context/cenarios/<func>/<arquivo>.md` é obrigatório (regra 8)."))
            continue
        cenario_path = ROOT / m_doc.group(1)
        if not cenario_path.exists():
            achados.append(Achado("R05", "erro", arq, teste.linha, f"Cenário inexistente: {m_doc.group(1)}."))
            continue
        if cenario_path.parent.name != funcionalidade:
            achados.append(Achado("R05", "aviso", arq, teste.linha, f"Cenário em outra funcionalidade ({cenario_path.parent.name}) que a suíte ({funcionalidade})."))
        cenario = ler_cenario(cenario_path)
        if cenario["id"] and cenario["id"] != id_teste:
            achados.append(Achado("R12", "erro", arq, teste.linha, f"ID do teste ({id_teste}) difere do ID do cenário ({cenario['id']})."))
        esperadas = set(cenario["tags"])
        reais = {funcionalidade, *objetivos}
        if esperadas and esperadas != reais:
            achados.append(Achado("R13", "erro", arq, teste.linha,
                                  f"Tags do cenário ({', '.join(sorted(esperadas))}) diferem das do teste ({', '.join(sorted(reais))})."))

        evid_teste = [c[1] for _, c in passos if c[0] == "Registrar Evidência" and len(c) > 1]
        if cenario["evidencias"] != evid_teste:
            sev = "erro" if set(cenario["evidencias"]) != set(evid_teste) else "aviso"
            achados.append(Achado("R10", sev, arq, teste.linha,
                                  f"Evidências do cenário {cenario['evidencias']} ≠ `Registrar Evidência` do teste {evid_teste}."))
        if not cenario["evidencias"]:
            achados.append(Achado("R10", "aviso", arq, teste.linha, "Cenário sem 📸: o padrão é uma evidência por critério."))
        validacoes = [c for _, c in passos if c[0].startswith("Validar")]
        if len(validacoes) < len(cenario["criterios"]):
            achados.append(Achado("R11", "aviso", arq, teste.linha,
                                  f"{len(cenario['criterios'])} critérios no cenário e {len(validacoes)} chamadas `Validar ...`: "
                                  "confira se cada critério tem asserção (revisão humana/revisor)."))
        if not validacoes:
            achados.append(Achado("R11", "erro", arq, teste.linha, "Teste sem nenhuma asserção `Validar ...` (regra 1)."))


def checar_pagina(caminho: Path, linhas: list[Linha], ctx: dict, achados: list[Achado]) -> None:
    arq = rel(caminho)
    for linha in linhas:
        cel = [c for c in linha.celulas if c]
        if linha.secao == "variables" and cel and cel[0].startswith("${"):
            nome = cel[0].strip("${}= ")
            if caminho.parent == PAGES_DIR and not re.match(r"^(LOC|MSG)_[A-Z0-9_]+$", nome):
                achados.append(Achado("R15", "aviso", arq, linha.numero, f"Variável `{cel[0]}` de página fora do padrão `${{LOC_*}}`/`${{MSG_*}}`."))
            if caminho.parent == PAGES_DIR and nome.startswith("LOC_") and len(cel) > 1 and not RE_LOCATOR_CRU.search(cel[1]):
                achados.append(Achado("R15", "aviso", arq, linha.numero, f"`{cel[0]}` não parece um locator (esperado id=/accessibility_id=/xpath=/android=)."))
        if linha.secao == "keywords" and linha.texto and not linha.texto[0].isspace():
            nome_kw = linha.texto.strip()
            chave = nome_kw.lower()
            if chave in ctx["keywords"]:
                achados.append(Achado("R18", "erro", arq, linha.numero, f"Keyword `{nome_kw}` duplicada (também em {ctx['keywords'][chave]})."))
            ctx["keywords"][chave] = arq
    texto = caminho.read_text(encoding="utf-8")
    for numero, bruta in enumerate(texto.splitlines(), start=1):
        if "# NÃO VALIDADO" in bruta and bruta.startswith("${"):
            achados.append(Achado("R14", "info", arq, numero, f"Seletor ainda `# NÃO VALIDADO`: {bruta.split()[0]}"))


# --------------------------------------------------------------------------- ferramentas externas

def rodar_robocop(alvos: list[Path], achados: list[Achado]) -> None:
    try:
        proc = subprocess.run(
            [sys.executable, "-m", "robocop", "check", "-c", "print_issues.output_format=simple", "--issue-format", "{source}|{line}|{rule_id}|{severity}|{desc}",
             *[str(a) for a in alvos]],
            cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120,
        )
    except (OSError, subprocess.TimeoutExpired) as erro:
        achados.append(Achado("RC00", "aviso", "robocop", 0, f"Robocop não rodou: {erro}"))
        return
    if "No module named robocop" in proc.stderr:
        achados.append(Achado("RC00", "aviso", "robocop", 0, "Robocop não instalado: pip install -r tests/requirements.txt"))
        return
    for bruta in proc.stdout.splitlines():
        partes = bruta.split("|", 4)
        if len(partes) != 5 or not partes[1].isdigit():
            continue
        fonte, linha, regra, sev, desc = partes
        severidade = "erro" if sev.upper().startswith("E") else "aviso"
        achados.append(Achado(f"RC-{regra}", severidade, rel(Path(fonte)), int(linha), desc))


def rodar_dryrun(achados: list[Achado]) -> None:
    proc = subprocess.run(
        [sys.executable, "-m", "robot", "--dryrun", "--output", "NONE", "--report", "NONE", "--log", "NONE",
         "--consolecolors", "off", "--console", "quiet", str(ROBOT_DIR)],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=300,
    )
    if proc.returncode != 0:
        detalhe = (proc.stdout + proc.stderr).strip().splitlines()[-15:]
        achados.append(Achado("DRY", "erro", "tests/robot", 0,
                              "Dry-run do Robot falhou (keyword inexistente, argumentos errados ou erro de sintaxe):\n    "
                              + "\n    ".join(detalhe)))


# --------------------------------------------------------------------------- aprovação

def arquivos_de_automacao() -> list[Path]:
    return sorted([*ROBOT_DIR.rglob("*.robot"), *PAGES_DIR.glob("*.resource"), *RESOURCES_DIR.glob("*.resource")])


def hash_automacao() -> str:
    """Hash do que executa: ignora comentários e espaços finais (tirar `# NÃO VALIDADO` não exige nova revisão)."""
    h = hashlib.sha256()
    for caminho in arquivos_de_automacao():
        h.update(rel(caminho).encode())
        for linha in caminho.read_text(encoding="utf-8").splitlines():
            h.update(re.split(r"(?:^|\s{2,}|\t)#", linha, maxsplit=1)[0].rstrip().encode() + b"\n")
    return h.hexdigest()


def status_aprovacao() -> tuple[bool, str]:
    if not APROVACAO.exists():
        return False, "nenhuma revisão aprovada registrada"
    dados = json.loads(APROVACAO.read_text(encoding="utf-8"))
    if dados.get("hash") != hash_automacao():
        return False, f"os arquivos mudaram desde a última aprovação ({dados.get('aprovado_em', '?')})"
    return True, f"aprovado em {dados.get('aprovado_em')}"


# --------------------------------------------------------------------------- main

def coletar(arquivo: Path | None, completo: bool) -> list[Achado]:
    achados: list[Achado] = []
    senhas = senhas_das_massas()
    ctx = {"ids": {}, "keywords": {}}
    if arquivo:
        alvos = [arquivo.resolve()]
        if arquivo.suffix == ".resource":
            # duplicidade de keyword exige conhecer as outras páginas
            for outro in [*PAGES_DIR.glob("*.resource"), *RESOURCES_DIR.glob("*.resource")]:
                if outro.resolve() != arquivo.resolve():
                    checar_pagina(outro, ler_robot(outro), ctx, [])
        elif arquivo.suffix == ".robot":
            for outro in ROBOT_DIR.rglob("*.robot"):
                if outro.resolve() != arquivo.resolve() and outro.name != "__init__.robot":
                    for t in extrair_testes(outro, ler_robot(outro)):
                        m = RE_ID_TESTE.match(t.nome)
                        if m:
                            ctx["ids"][m.group(1)] = rel(outro)
    else:
        alvos = arquivos_de_automacao()
    for caminho in alvos:
        linhas = ler_robot(caminho)
        checar_linhas_comuns(caminho, linhas, senhas, achados)
        if caminho.suffix == ".robot" and caminho.name != "__init__.robot":
            checar_suite(caminho, linhas, ctx, achados)
        elif caminho.suffix == ".resource":
            checar_pagina(caminho, linhas, ctx, achados)
    rodar_robocop(alvos, achados)
    if completo:
        rodar_dryrun(achados)
    return achados


def imprimir(achados: list[Achado]) -> None:
    ordem = {"erro": 0, "aviso": 1, "info": 2}
    for a in sorted(achados, key=lambda a: (ordem[a.severidade], a.arquivo, a.linha)):
        print(f"[{a.severidade.upper()}] {a.regra} {a.arquivo}:{a.linha} — {a.mensagem}")
    erros = sum(a.severidade == "erro" for a in achados)
    avisos = sum(a.severidade == "aviso" for a in achados)
    print(f"\n{erros} erro(s), {avisos} aviso(s), {sum(a.severidade == 'info' for a in achados)} info.")


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--arquivo", type=Path, help="checa só este arquivo (modo rápido, sem dry-run)")
    parser.add_argument("--json", action="store_true", help="saída em JSON")
    parser.add_argument("--aprovar", action="store_true", help="sem erros, grava a aprovação do revisor-robot")
    parser.add_argument("--status", action="store_true", help="informa se a aprovação vale para os arquivos atuais")
    args = parser.parse_args()

    if args.status:
        ok, motivo = status_aprovacao()
        print(("APROVADO: " if ok else "SEM APROVAÇÃO: ") + motivo)
        return 0 if ok else 2

    arquivo = args.arquivo if args.arquivo is None or args.arquivo.is_absolute() else (Path.cwd() / args.arquivo)
    achados = coletar(arquivo, completo=arquivo is None)
    erros = [a for a in achados if a.severidade == "erro"]

    if args.json:
        print(json.dumps({"erros": len(erros), "achados": [asdict(a) for a in achados]}, ensure_ascii=False, indent=2))
    else:
        imprimir(achados)

    if args.aprovar:
        if erros or arquivo is not None:
            print("\nAprovação NÃO gravada: " + ("há erros." if erros else "use o modo completo (sem --arquivo)."))
            return 1
        APROVACAO.write_text(json.dumps({
            "hash": hash_automacao(),
            "aprovado_em": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "arquivos": [rel(p) for p in arquivos_de_automacao()],
        }, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\nAprovação gravada em {rel(APROVACAO)}.")
    return 1 if erros else 0


if __name__ == "__main__":
    sys.exit(main())
