"""Coleta os fatos da última execução Robot para a avaliação de QA (somente leitura).

Uso (na raiz do repositório):
    python .claude/skills/qa-engineer/scripts/coletar_resultados.py

Saída: JSON com, por teste da última execução, status, mensagem, tags, duração, evidências
geradas x planejadas, link do cenário e se ele existe; além de avisos (WARN), testes das suítes
que não rodaram e seletores ainda marcados "# NÃO VALIDADO".
"""
from __future__ import annotations

import json
import re
import statistics
import sys
from pathlib import Path

from robot.api import ExecutionResult, TestSuiteBuilder

ROOT = Path.cwd()
REPORTS = ROOT / "tests" / "reports"
LAST_RUN = REPORTS / ".last-run.xml"
SUITES = ROOT / "tests" / "robot"
PAGES = ROOT / "tests" / "pages"
EVIDENCE_KW = "Registrar Evidência"


def planned_tests() -> dict:
    """Testes definidos nas suítes: evidências planejadas e link do cenário."""
    plan = {}

    def visit(suite):
        for test in suite.tests:
            calls = [k for k in test.body if getattr(k, "name", "") == EVIDENCE_KW]
            doc = re.search(r"Cenário:\s*(\S+\.md)", test.doc or "")
            plan[test.name] = {"evidencias_planejadas": len(calls), "cenario": doc.group(1) if doc else None}
        for child in suite.suites:
            visit(child)

    visit(TestSuiteBuilder().build(str(SUITES)))
    return plan


def unvalidated_selectors() -> list:
    found = []
    for page in sorted(PAGES.glob("*.resource")):
        for line in page.read_text(encoding="utf-8").splitlines():
            if "NÃO VALIDADO" in line and line.startswith("${"):
                found.append({"pagina": page.name, "variavel": line.split("}")[0] + "}"})
    return found


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    if not LAST_RUN.exists():
        print(json.dumps({"erro": f"{LAST_RUN} não existe: nenhuma execução registrada."}, ensure_ascii=False))
        return 1
    result = ExecutionResult(str(LAST_RUN))
    plan = planned_tests()
    tests = []

    def visit(suite):
        for t in suite.tests:
            tid = t.name.split()[0]
            shots = sorted((REPORTS / "screenshots" / tid).glob("*.png"))
            p = plan.get(t.name, {})
            cenario = p.get("cenario")
            tests.append({
                "id": tid, "nome": t.name, "suite": suite.name, "status": t.status,
                "mensagem": t.message, "tags": list(t.tags),
                "duracao_s": round(t.elapsed_time.total_seconds(), 1),
                "evidencias": [s.relative_to(ROOT).as_posix() for s in shots],
                "evidencias_planejadas": p.get("evidencias_planejadas"),
                "evidencia_falha": any(s.name.endswith("_falha.png") for s in shots),
                "cenario": cenario, "cenario_existe": bool(cenario and (ROOT / cenario).exists()),
            })
        for child in suite.suites:
            visit(child)

    visit(result.suite)
    durations = [t["duracao_s"] for t in tests if t["status"] == "PASS"]
    median = statistics.median(durations) if durations else 0
    executed = {t["nome"] for t in tests}
    out = {
        "execucao": {
            "inicio": result.suite.start_time.strftime("%Y-%m-%d %H:%M:%S") if result.suite.start_time else "",
            "total": len(tests),
            "pass": sum(t["status"] == "PASS" for t in tests),
            "fail": sum(t["status"] == "FAIL" for t in tests),
            "skip": sum(t["status"] == "SKIP" for t in tests),
            "mediana_pass_s": median,
        },
        "testes": tests,
        "lentos": [t["id"] for t in tests if median and t["duracao_s"] > 2 * median],
        "avisos": [m.message for m in result.errors.messages if m.level in ("WARN", "ERROR")],
        "nao_executados": sorted(set(plan) - executed),
        "seletores_nao_validados": unvalidated_selectors(),
    }
    print(json.dumps(out, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
