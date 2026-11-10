"""Hook PreToolUse (Bash|PowerShell): portão de execução do Robot.

Bloqueia `python -m robot ...` (execução real, não --dryrun) quando as suítes, páginas ou resources mudaram
desde a última aprovação do subagente revisor-robot (.claude/revisao-robot.local.json, gravada por
`lint_robot.py --aprovar`). Reexecutar sem alterar nada passa direto.
Vale só para comandos do agente; você continua rodando o Robot no seu terminal normalmente.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LINT = ROOT / ".claude" / "scripts" / "lint_robot.py"
# Só em posição de comando: início de linha ou depois de ; & | ( , com atribuições de ambiente opcionais antes
# (PYTHONUTF8=1 python ... / $env:X=1; python ...). Texto citado em echo, strings ou heredocs não conta.
RE_ROBOT = re.compile(
    r"(?:^|[;&|(]|\n)\s*(?:[A-Za-z_][A-Za-z0-9_]*=\S*\s+)*"
    r"(?:&\s*)?(?:\S*[\\/])?(?:python[0-9.]*(?:\.exe)?\s+-m\s+robot(?![.\w])|robot(?:\.exe)?(?=\s))",
    re.MULTILINE,
)
# Corpos de heredoc (bash) e here-strings (PowerShell) são dados, não comandos.
RE_HEREDOC = re.compile(r"<<-?\s*(['\"]?)(\w+)\1[^\n]*\n.*?^\s*\2\s*$", re.DOTALL | re.MULTILINE)
RE_HERESTRING = re.compile(r"@(['\"])\r?\n.*?^\1@", re.DOTALL | re.MULTILINE)


def e_execucao_robot(comando: str) -> bool:
    limpo = RE_HERESTRING.sub("", RE_HEREDOC.sub("", comando))
    return bool(RE_ROBOT.search(limpo)) and "--dryrun" not in limpo


def main() -> int:
    for fluxo in (sys.stdout, sys.stderr):
        if hasattr(fluxo, "reconfigure"):
            fluxo.reconfigure(encoding="utf-8")
    try:
        evento = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0
    comando = (evento.get("tool_input", {}) or {}).get("command", "") or ""
    if not e_execucao_robot(comando):
        return 0
    proc = subprocess.run([sys.executable, str(LINT), "--status"], cwd=ROOT, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=60)
    if proc.returncode == 0:
        return 0
    sys.stderr.write(
        f"Execução do Robot bloqueada pelo portão de revisão: {proc.stdout.strip()}.\n"
        "Acione o subagente `revisor-robot` (passo 5 do /testar-cenarios) com o cenário e os arquivos alterados; "
        "ele aprova com `python .claude/scripts/lint_robot.py --aprovar`. Não grave a aprovação sem a revisão.\n"
    )
    return 2


if __name__ == "__main__":
    sys.exit(main())
