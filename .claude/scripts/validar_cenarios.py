"""Validação estrutural dos cenários e das regras de negócio (camada determinística da Definition of Ready).

Cenários (context/cenarios/<funcionalidade>/*.md, formato de context/cenarios/_modelo.md):
cabeçalho com ID, tags, suíte e regras cobertas; seções obrigatórias; critérios verificáveis (sem termos
vagos); pontos de evidência 📸; regras citadas existentes; nenhuma senha de massa.

Regras de negócio (context/regras-negocio/<funcionalidade>.md, exceto conduta-testes.md):
`### RN-<PREFIXO>-NN <Título>` com **Regra**, **Fonte** e **Status** (vigente | a confirmar | divergente | obsoleta).

Uso (na raiz do repositório):
    python .claude/scripts/validar_cenarios.py                    # todos os cenários e regras
    python .claude/scripts/validar_cenarios.py --arquivo <path>   # um arquivo (hook PostToolUse)
    python .claude/scripts/validar_cenarios.py --json

Saída: código 0 sem erros (avisos não bloqueiam a DoR, mas o product-owner deve resolvê-los ou justificá-los); 1 com erros.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CENARIOS = ROOT / "context" / "cenarios"
REGRAS = ROOT / "context" / "regras-negocio"
NAO_SAO_REGRAS = {"conduta-testes.md"}
USERS_FILE = ROOT / "tests" / "massas" / "users.yaml"

SECOES = ["## Objetivo", "## Pré-condições", "## Dados", "## Passos", "## Resultado esperado"]
STATUS_CENARIO = ("proposto", "pronto", "automatizado")
STATUS_REGRA = ("vigente", "a confirmar", "divergente", "obsoleta")
# Termos que tornam um critério não verificável: dizem "o que" sem dizer "quanto" ou "qual texto".
TERMOS_VAGOS = [
    "corretamente", "correto", "correta", "corretos", "corretas", "esperado", "esperada", "esperados", "esperadas",
    "adequado", "adequada", "adequadamente", "funciona", "funcionar", "normalmente", "rapidamente", "rápido",
    "devidamente", "apropriado", "apropriada", "etc", "ok", "bem-sucedido", "sem erros",
]
RE_RN = re.compile(r"\bRN-[A-Z]+-\d{2,}\b")
RE_TITULO_RN = re.compile(r"^### (RN-[A-Z]+-\d{2,}) (.+)$", re.MULTILINE)
RE_TAG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


@dataclass
class Achado:
    regra: str
    severidade: str  # erro | aviso
    arquivo: str
    linha: int
    mensagem: str


def rel(p: Path) -> str:
    try:
        return p.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return p.as_posix()


def senhas() -> list[str]:
    if not USERS_FILE.exists():
        return []
    texto = USERS_FILE.read_text(encoding="utf-8")
    valores = [v.strip().strip("\"'") for v in re.findall(r"^\s*senha:\s*(.+)$", texto, re.MULTILINE)]
    return sorted({v for v in valores if len(v) >= 4})


def linha_de(texto: str, trecho: str) -> int:
    pos = texto.find(trecho)
    return texto.count("\n", 0, pos) + 1 if pos >= 0 else 1


def campo(texto: str, nome: str) -> str | None:
    m = re.search(rf"^- \*\*{nome}:\*\*\s*(.*)$", texto, re.MULTILINE)
    return m.group(1).strip() if m else None


# --------------------------------------------------------------------------- regras de negócio

def ler_regras() -> dict[str, dict]:
    regras: dict[str, dict] = {}
    if not REGRAS.exists():
        return regras
    for arq in sorted(REGRAS.glob("*.md")):
        if arq.name in NAO_SAO_REGRAS:
            continue
        texto = arq.read_text(encoding="utf-8")
        blocos = re.split(r"(?=^### RN-)", texto, flags=re.MULTILINE)
        for bloco in blocos:
            m = RE_TITULO_RN.match(bloco)
            if not m:
                continue
            status = (campo(bloco, "Status") or "").lower()
            regras.setdefault(m.group(1), {"titulo": m.group(2), "arquivo": rel(arq), "status": status, "bloco": bloco,
                                           "linha": linha_de(texto, bloco.splitlines()[0])})
    return regras


def checar_arquivo_regras(arq: Path, achados: list[Achado]) -> None:
    texto = arq.read_text(encoding="utf-8")
    vistos: set[str] = set()
    for bloco in re.split(r"(?=^### RN-)", texto, flags=re.MULTILINE):
        m = RE_TITULO_RN.match(bloco)
        if not m:
            if bloco.startswith("### ") and "RN-" in bloco.splitlines()[0]:
                achados.append(Achado("N01", "erro", rel(arq), linha_de(texto, bloco[:40]), "Título de regra fora do padrão `### RN-<PREFIXO>-NN <Título>`."))
            continue
        rn, n = m.group(1), linha_de(texto, bloco.splitlines()[0])
        if rn in vistos:
            achados.append(Achado("N02", "erro", rel(arq), n, f"{rn} duplicada no arquivo."))
        vistos.add(rn)
        for obrigatorio in ("Regra", "Fonte", "Status"):
            if not campo(bloco, obrigatorio):
                achados.append(Achado("N03", "erro", rel(arq), n, f"{rn} sem `- **{obrigatorio}:**`."))
        status = (campo(bloco, "Status") or "").lower()
        if status and not status.startswith(STATUS_REGRA):
            achados.append(Achado("N04", "erro", rel(arq), n, f"{rn}: status `{status}` inválido ({' | '.join(STATUS_REGRA)})."))
        if status.startswith("a confirmar"):
            achados.append(Achado("N05", "aviso", rel(arq), n, f"{rn} ainda `a confirmar`: o usuário precisa decidir antes de virar critério."))
        regra = campo(bloco, "Regra") or ""
        vagos = [t for t in TERMOS_VAGOS if re.search(rf"(?<!\w){re.escape(t)}(?!\w)", regra, re.IGNORECASE)]
        if vagos:
            achados.append(Achado("N06", "aviso", rel(arq), n, f"{rn}: termo vago na regra ({', '.join(vagos)}): diga o valor, o texto ou a condição exata."))


# --------------------------------------------------------------------------- cenários

def checar_cenario(arq: Path, regras: dict[str, dict], ids: dict[str, str], achados: list[Achado]) -> None:
    texto = arq.read_text(encoding="utf-8")
    a = rel(arq)
    func = arq.parent.name

    m_titulo = re.match(r"^# ([A-Z]+-\d{3}) (.+)$", texto.splitlines()[0] if texto else "")
    id_campo = (campo(texto, "ID") or "").split()[0] if campo(texto, "ID") else ""
    if not m_titulo:
        achados.append(Achado("C01", "erro", a, 1, "1ª linha deve ser `# <ID> <Título>` (ex.: `# CART-005 Alterar quantidade`)."))
    elif id_campo != m_titulo.group(1):
        achados.append(Achado("C01", "erro", a, 1, f"`- **ID:**` ({id_campo or 'ausente'}) difere do título ({m_titulo.group(1)})."))
    if id_campo:
        if id_campo in ids and ids[id_campo] != a:
            achados.append(Achado("C13", "erro", a, 1, f"ID {id_campo} duplicado (também em {ids[id_campo]})."))
        ids.setdefault(id_campo, a)

    tags = [t.strip() for t in (campo(texto, "Tags") or "").split(",") if t.strip()]
    if len(tags) != 2:
        achados.append(Achado("C03", "erro", a, linha_de(texto, "**Tags:**"), "`- **Tags:**` deve ter exatamente `<funcionalidade>, <objetivo>`."))
    else:
        if tags[0] != func:
            achados.append(Achado("C03", "erro", a, linha_de(texto, "**Tags:**"), f"1ª tag deve ser a funcionalidade `{func}` (pasta do cenário)."))
        if not RE_TAG.match(tags[1]) or tags[1] in ("smoke",) or re.fullmatch(r"[a-z]+-\d{3}", tags[1]):
            achados.append(Achado("C03", "erro", a, linha_de(texto, "**Tags:**"), f"Tag de objetivo `{tags[1]}` inválida: kebab-case, sem `smoke` e sem ID."))

    suite = campo(texto, "Suíte") or ""
    if f"tests/robot/{func}/" not in suite:
        achados.append(Achado("C04", "erro", a, linha_de(texto, "**Suíte:**"), f"`- **Suíte:**` deve citar `tests/robot/{func}/{func}.robot`."))

    status = (campo(texto, "Status") or "").lower()
    if status and not status.startswith(STATUS_CENARIO):
        achados.append(Achado("C11", "erro", a, linha_de(texto, "**Status:**"), f"Status `{status}` inválido ({' | '.join(STATUS_CENARIO)})."))

    regras_campo = campo(texto, "Regras")
    if regras_campo is None:
        achados.append(Achado("C05", "erro", a, 1, "`- **Regras:**` ausente: cite as RN que o cenário cobre (context/regras-negocio/)."))
    else:
        citadas = RE_RN.findall(regras_campo)
        if not citadas:
            achados.append(Achado("C05", "erro", a, linha_de(texto, "**Regras:**"), "`- **Regras:**` sem nenhum `RN-<PREFIXO>-NN`."))
        for rn in citadas:
            if rn not in regras:
                achados.append(Achado("C05", "erro", a, linha_de(texto, "**Regras:**"), f"{rn} não existe em context/regras-negocio/."))
            elif regras[rn]["status"].startswith(("a confirmar", "obsoleta")):
                achados.append(Achado("C05", "aviso", a, linha_de(texto, "**Regras:**"), f"{rn} está `{regras[rn]['status']}` em {regras[rn]['arquivo']}."))

    for secao in SECOES:
        if not re.search(rf"^{re.escape(secao)}", texto, re.MULTILINE):
            achados.append(Achado("C06", "erro", a, 1, f"Seção `{secao}` ausente (context/cenarios/_modelo.md)."))

    bloco_esperado = texto.split("## Resultado esperado", 1)[-1].split("\n## ", 1)[0] if "## Resultado esperado" in texto else ""
    criterios = re.findall(r"^\s*- \[[ xX]\]\s+(.+)$", bloco_esperado, re.MULTILINE)
    if not criterios:
        achados.append(Achado("C07", "erro", a, linha_de(texto, "## Resultado esperado"), "Nenhum critério `- [ ] ...` em Resultado esperado."))
    for crit in criterios:
        limpo = re.sub(r"📸\s*[\w-]+", "", crit)
        limpo = re.sub(r"\"[^\"]*\"", "", limpo)  # texto entre aspas é conteúdo da tela, não avaliação
        vagos = [t for t in TERMOS_VAGOS if re.search(rf"(?<!\w){re.escape(t)}(?!\w)", limpo, re.IGNORECASE)]
        if vagos:
            achados.append(Achado("C08", "aviso", a, linha_de(texto, crit[:30]),
                                  f"Critério com termo vago ({', '.join(vagos)}): `{crit.strip()[:80]}` — diga o valor ou o texto exato."))

    passos_bloco = texto.split("## Passos", 1)[-1].split("\n## ", 1)[0] if "## Passos" in texto else ""
    if not re.search(r"^\s*1\. ", passos_bloco, re.MULTILINE):
        achados.append(Achado("C15", "erro", a, linha_de(texto, "## Passos"), "Passos devem ser uma lista numerada (`1. ...`)."))

    if "📸" not in texto.split("## Observações", 1)[0]:
        achados.append(Achado("C09", "erro", a, 1, "Nenhum ponto de evidência `📸 <nome>` nos passos ou critérios."))

    if any(s in texto for s in senhas()):
        achados.append(Achado("C10", "erro", a, 1, "Senha de massa escrita no cenário: cite só o nome da massa (regra 4)."))


# --------------------------------------------------------------------------- main

def todos_cenarios() -> list[Path]:
    return sorted(p for p in CENARIOS.glob("*/*.md"))


def coletar(arquivo: Path | None) -> list[Achado]:
    achados: list[Achado] = []
    regras = ler_regras()
    ids: dict[str, str] = {}
    if arquivo is None:
        for arq in sorted(REGRAS.glob("*.md")):
            if arq.name not in NAO_SAO_REGRAS:
                checar_arquivo_regras(arq, achados)
        for arq in todos_cenarios():
            checar_cenario(arq, regras, ids, achados)
        return achados
    arquivo = arquivo.resolve()
    if arquivo.parent == REGRAS.resolve():
        if arquivo.name not in NAO_SAO_REGRAS:
            checar_arquivo_regras(arquivo, achados)
    elif arquivo.parent.parent == CENARIOS.resolve() and arquivo.name != "_modelo.md":
        for outro in todos_cenarios():
            if outro.resolve() != arquivo:
                id_outro = campo(outro.read_text(encoding="utf-8"), "ID")
                if id_outro:
                    ids[id_outro.split()[0]] = rel(outro)
        checar_cenario(arquivo, regras, ids, achados)
    return achados


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--arquivo", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    achados = coletar(args.arquivo)
    erros = sum(a.severidade == "erro" for a in achados)
    if args.json:
        print(json.dumps({"erros": erros, "achados": [asdict(a) for a in achados]}, ensure_ascii=False, indent=2))
    else:
        for a in sorted(achados, key=lambda a: (a.severidade != "erro", a.arquivo, a.linha)):
            print(f"[{a.severidade.upper()}] {a.regra} {a.arquivo}:{a.linha} — {a.mensagem}")
        print(f"\n{erros} erro(s), {len(achados) - erros} aviso(s).")
    return 1 if erros else 0


if __name__ == "__main__":
    sys.exit(main())
