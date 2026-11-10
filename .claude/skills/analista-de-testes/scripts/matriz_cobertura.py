"""Matriz de rastreabilidade regra de negócio × cenário × teste Robot × último resultado (somente leitura).

Fontes:
  context/regras-negocio/<func>.md   ### RN-<PREFIXO>-NN <Título> + **Status**
  context/cenarios/<func>/*.md       - **ID:** e - **Regras:** (RN cobertas) e - **Status:** (opcional)
  tests/robot/**/*.robot             testes "<ID> <Título>" com [Documentation] Cenário: ... e [Tags]
  tests/reports/summary.json         último resultado de cada teste (se existir)

Uso (na raiz do repositório):
    python .claude/skills/analista-de-testes/scripts/matriz_cobertura.py              # Markdown
    python .claude/skills/analista-de-testes/scripts/matriz_cobertura.py --func carrinho
    python .claude/skills/analista-de-testes/scripts/matriz_cobertura.py --json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
REGRAS = ROOT / "context" / "regras-negocio"
CENARIOS = ROOT / "context" / "cenarios"
ROBOT = ROOT / "tests" / "robot"
SUMMARY = ROOT / "tests" / "reports" / "summary.json"

RE_RN = re.compile(r"\bRN-[A-Z]+-\d{2,}\b")


def campo(texto: str, nome: str) -> str:
    m = re.search(rf"^- \*\*{nome}:\*\*\s*(.*)$", texto, re.MULTILINE)
    return m.group(1).strip() if m else ""


def ler_regras(func: str | None) -> dict[str, dict]:
    regras: dict[str, dict] = {}
    for arq in sorted(REGRAS.glob("*.md")):
        if arq.name == "conduta-testes.md" or (func and arq.stem != func):
            continue
        texto = arq.read_text(encoding="utf-8")
        for bloco in re.split(r"(?=^### RN-)", texto, flags=re.MULTILINE):
            m = re.match(r"^### (RN-[A-Z]+-\d{2,}) (.+)$", bloco, re.MULTILINE)
            if m:
                regras[m.group(1)] = {"titulo": m.group(2).strip(), "status": campo(bloco, "Status").lower(),
                                      "funcionalidade": arq.stem, "cenarios": []}
    return regras


def ler_cenarios(func: str | None) -> dict[str, dict]:
    cenarios: dict[str, dict] = {}
    for arq in sorted(CENARIOS.glob("*/*.md")):
        if func and arq.parent.name != func:
            continue
        texto = arq.read_text(encoding="utf-8")
        id_ = campo(texto, "ID").split()[0] if campo(texto, "ID") else arq.stem
        titulo = texto.splitlines()[0].lstrip("# ").removeprefix(id_).strip() if texto else ""
        cenarios[id_] = {"titulo": titulo, "arquivo": arq.relative_to(ROOT).as_posix(),
                         "regras": RE_RN.findall(campo(texto, "Regras")), "status": campo(texto, "Status").lower(),
                         "funcionalidade": arq.parent.name, "testes": []}
    return cenarios


def ler_testes() -> dict[str, dict]:
    testes: dict[str, dict] = {}
    for arq in sorted(ROBOT.rglob("*.robot")):
        secao = ""
        atual = None
        for bruta in arq.read_text(encoding="utf-8").splitlines():
            if bruta.startswith("***"):
                secao = bruta.strip("* ").lower()
                continue
            if secao != "test cases" or not bruta.strip() or bruta.lstrip().startswith("#"):
                continue
            if not bruta[0].isspace():
                m = re.match(r"^([A-Z]+-\d{3}) ", bruta)
                atual = m.group(1) if m else None
                if atual:
                    testes[atual] = {"nome": bruta.strip(), "arquivo": arq.relative_to(ROOT).as_posix(), "cenario": "", "tags": []}
            elif atual:
                cel = [c for c in re.split(r"\s{2,}|\t", bruta.strip()) if c]
                if cel and cel[0] == "[Tags]":
                    testes[atual]["tags"] = cel[1:]
                m = re.search(r"Cenário:\s*(context/cenarios/\S+\.md)", bruta)
                if m:
                    testes[atual]["cenario"] = m.group(1)
    return testes


def ler_resultados() -> dict[str, dict]:
    if not SUMMARY.exists():
        return {}
    dados = json.loads(SUMMARY.read_text(encoding="utf-8"))
    saida = {}
    for item in dados.get("tests", {}).values():
        m = re.match(r"^([A-Z]+-\d{3}) ", item.get("name", ""))
        if m:
            saida[m.group(1)] = {"status": item.get("status", ""), "executado_em": item.get("executed_at", "")}
    return saida


def montar(func: str | None) -> dict:
    regras, cenarios, testes, resultados = ler_regras(func), ler_cenarios(func), ler_testes(), ler_resultados()
    por_arquivo = {c["arquivo"]: id_ for id_, c in cenarios.items()}
    for id_teste, t in testes.items():
        id_cen = por_arquivo.get(t["cenario"])
        if id_cen:
            cenarios[id_cen]["testes"].append(id_teste)
    for id_cen, c in cenarios.items():
        for rn in c["regras"]:
            if rn in regras:
                regras[rn]["cenarios"].append(id_cen)

    def resultado(id_teste: str) -> str:
        r = resultados.get(id_teste)
        return f"{r['status']} ({r['executado_em'][:10]})" if r else "não executado"

    lacunas = {
        "regras_sem_cenario": [rn for rn, r in regras.items() if not r["cenarios"] and not r["status"].startswith(("obsoleta", "a confirmar"))],
        "regras_a_confirmar": [rn for rn, r in regras.items() if r["status"].startswith("a confirmar")],
        "regras_divergentes": [rn for rn, r in regras.items() if r["status"].startswith("divergente")],
        "cenarios_sem_regra": [c for c, d in cenarios.items() if not d["regras"]],
        "cenarios_com_regra_inexistente": {c: [rn for rn in d["regras"] if rn not in regras] for c, d in cenarios.items()
                                           if any(rn not in regras for rn in d["regras"])},
        "cenarios_sem_teste": [c for c, d in cenarios.items() if not d["testes"]],
        "testes_sem_cenario": [t for t, d in testes.items() if not d["cenario"] or d["cenario"] not in por_arquivo]
        if not func else [],
        "testes_defeito_conhecido": [t for t, d in testes.items() if "defeito-conhecido" in d["tags"] and
                                     (not func or d["arquivo"].startswith(f"tests/robot/{func}/"))],
    }
    linhas = []
    for rn, r in regras.items():
        ids_testes = [t for c in r["cenarios"] for t in cenarios[c]["testes"]]
        linhas.append({"regra": rn, "titulo": r["titulo"], "status_regra": r["status"] or "?",
                       "cenarios": r["cenarios"], "testes": ids_testes,
                       "resultados": {t: resultado(t) for t in ids_testes}})
    return {"matriz": linhas, "lacunas": lacunas,
            "totais": {"regras": len(regras), "cenarios": len(cenarios),
                       "regras_cobertas": sum(bool(r["cenarios"]) for r in regras.values())}}


def imprimir(dados: dict) -> None:
    t = dados["totais"]
    print(f"# Matriz de cobertura\n\n{t['regras_cobertas']}/{t['regras']} regras com cenário · {t['cenarios']} cenários\n")
    print("| Regra | Título | Status | Cenários | Testes · último resultado |")
    print("|---|---|---|---|---|")
    for l in dados["matriz"]:
        testes = "<br>".join(f"{k} · {v}" for k, v in l["resultados"].items()) or "—"
        print(f"| {l['regra']} | {l['titulo']} | {l['status_regra']} | {', '.join(l['cenarios']) or '**sem cenário**'} | {testes} |")
    print("\n## Lacunas\n")
    rotulos = {
        "regras_sem_cenario": "Regras vigentes sem cenário",
        "regras_a_confirmar": "Regras a confirmar (decisão do usuário)",
        "regras_divergentes": "Regras divergentes (defeito/limitação)",
        "cenarios_sem_regra": "Cenários sem regra citada",
        "cenarios_com_regra_inexistente": "Cenários citando regra inexistente",
        "cenarios_sem_teste": "Cenários sem teste Robot",
        "testes_sem_cenario": "Testes sem cenário",
        "testes_defeito_conhecido": "Testes em SKIP por defeito conhecido",
    }
    for chave, rotulo in rotulos.items():
        valor = dados["lacunas"][chave]
        texto = ", ".join(f"{k} ({', '.join(v)})" for k, v in valor.items()) if isinstance(valor, dict) else ", ".join(valor)
        print(f"- **{rotulo}:** {texto or 'nenhum'}")


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--func", help="limita a uma funcionalidade (produtos, carrinho, compra, ...)")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    dados = montar(args.func)
    if args.json:
        print(json.dumps(dados, ensure_ascii=False, indent=2))
    else:
        imprimir(dados)
    return 0


if __name__ == "__main__":
    sys.exit(main())
