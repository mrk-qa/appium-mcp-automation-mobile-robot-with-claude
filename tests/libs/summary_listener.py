"""Listener Robot (API v3): consolida TODAS as execuções em tests/reports/.

A cada teste: prepara (limpa e cria) a pasta de evidências <outputdir>/screenshots/<ID>/,
usada por `Registrar Evidência` (tests/resources/infraestrutura.resource).

A cada execução (configurada em tests/robot.args):
  1. o Robot grava só o resultado da execução atual em tests/reports/.last-run.xml;
  2. este listener mescla esse resultado no consolidado com `rebot --merge`
     (testes novos são adicionados; testes reexecutados substituem o resultado anterior)
     e regenera tests/reports/{output.xml, log.html, report.html};
  3. atualiza tests/reports/summary.{md,json}: o último resultado de cada teste,
     com as evidências em tests/reports/screenshots/<ID>/.

Para começar do zero, apague tests/reports/.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

from robot.api import ExecutionResult
from robot.libraries.BuiltIn import BuiltIn

ROBOT_LISTENER_API_VERSION = 3
ROOT = Path(__file__).resolve().parents[2]


def _test_id(name: str) -> str:
    """ID do teste = primeira palavra do nome (ex.: "BUY-001 Compra de ..." -> "BUY-001")."""
    return name.split()[0]


def start_test(data, result) -> None:
    """Evidências sempre da última execução do teste: limpa e recria screenshots/<ID>/."""
    shots = Path(BuiltIn().get_variable_value("${OUTPUT DIR}")) / "screenshots" / _test_id(data.name)
    shutil.rmtree(shots, ignore_errors=True)
    shots.mkdir(parents=True, exist_ok=True)


def _rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def output_file(path) -> None:
    """Chamado pelo Robot quando o output da execução atual é gravado."""
    last_run = Path(str(path))
    report_dir = last_run.parent
    consolidate(last_run, report_dir)
    summary = update_summary(last_run, report_dir)
    print(f"Consolidado: {_rel(report_dir / 'log.html')}")
    print(f"Resumo:      {_rel(summary)}")


def consolidate(last_run: Path, report_dir: Path) -> None:
    output = report_dir / "output.xml"
    merged = report_dir / ".merged.xml"
    inputs = [output, last_run] if output.exists() else [last_run]
    cmd = [sys.executable, "-m", "robot.rebot", "--outputdir", str(report_dir),
           "--output", merged.name, "--log", "log.html", "--report", "report.html",
           "--name", "Mobile Tests", "--consolecolors", "off"]
    if len(inputs) > 1:
        cmd.append("--merge")
    subprocess.run(cmd + [str(p) for p in inputs], cwd=ROOT, stdout=subprocess.DEVNULL, check=False)
    if merged.exists():
        merged.replace(output)


def update_summary(last_run: Path, report_dir: Path) -> Path:
    summary_json = report_dir / "summary.json"
    data = json.loads(summary_json.read_text(encoding="utf-8")) if summary_json.exists() else {"tests": {}}
    evidence_dir = report_dir / "screenshots"
    result = ExecutionResult(str(last_run))
    last_ids = []

    def visit(suite):
        for test in suite.tests:
            shots_dir = evidence_dir / _test_id(test.name)
            shots = sorted(shots_dir.glob("*.png")) if shots_dir.exists() else []
            key = f"{suite.name} / {test.name}"
            last_ids.append(key)
            data["tests"][key] = {
                "suite": suite.name,
                "name": test.name,
                "tags": list(test.tags),
                "status": test.status,
                "message": test.message,
                "elapsed_s": round(test.elapsed_time.total_seconds(), 1),
                "executed_at": test.start_time.strftime("%Y-%m-%d %H:%M:%S") if test.start_time else "",
                "evidence": [_rel(p) for p in shots],
            }
        for child in suite.suites:
            visit(child)

    visit(result.suite)
    data["last_run"] = last_ids
    summary_json.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    tests = sorted(data["tests"].values(), key=lambda t: (t["suite"], t["name"]))
    count = {s: sum(t["status"] == s for t in tests) for s in ("PASS", "FAIL", "SKIP")}
    icon = {"PASS": "✅", "FAIL": "❌", "SKIP": "⏭️"}
    row = lambda t: (f"| {icon.get(t['status'], '')} {t['status']} | {t['suite']} | {t['name']} "
                     f"| {t['executed_at']} | {t['elapsed_s']} | {len(t['evidence'])} |")
    header = ["| Status | Suíte | Teste | Executado em | Tempo (s) | Evidências |", "|---|---|---|---|---|---|"]
    lines = [
        "# Resultado consolidado dos testes",
        "",
        f"**Total:** {len(tests)} | **PASS:** {count['PASS']} | **FAIL:** {count['FAIL']} | **SKIP:** {count['SKIP']}",
        f"**Log:** `{_rel(report_dir / 'log.html')}`",
        "",
        "## Última execução",
        "",
        *header,
        *[row(data["tests"][k]) for k in last_ids],
        "",
        "## Todos os testes (último resultado de cada um)",
        "",
        *header,
        *[row(t) for t in tests],
    ]
    for t in tests:
        lines += ["", f"### {t['name']} — {t['status']}"]
        if t["message"]:
            lines.append(f"> {t['message']}")
        lines += [f"- `{e}`" for e in t["evidence"]] or ["- (sem evidências)"]
    out = report_dir / "summary.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out
