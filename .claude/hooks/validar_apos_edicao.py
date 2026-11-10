"""Hook PostToolUse (Write|Edit|MultiEdit): valida o arquivo logo depois que o agente o altera.

- tests/robot/**/*.robot, tests/pages/*.resource, tests/resources/*.resource
    -> .claude/scripts/lint_robot.py --arquivo <arquivo>   (convenções Robot + Robocop)
- context/cenarios/<func>/*.md, context/regras-negocio/*.md
    -> .claude/scripts/validar_cenarios.py --arquivo <arquivo>   (Definition of Ready estrutural)

Erros: código 2, e o relatório volta ao agente para ele corrigir na hora.
Só avisos: código 0 com o relatório como contexto adicional (não bloqueia).
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LINT = ROOT / ".claude" / "scripts" / "lint_robot.py"
CENARIOS = ROOT / ".claude" / "scripts" / "validar_cenarios.py"


def escolher_validador(caminho: Path) -> Path | None:
    try:
        relativo = caminho.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return None
    if relativo.startswith(("tests/robot/", "tests/pages/", "tests/resources/")) and caminho.suffix in (".robot", ".resource"):
        return LINT
    if relativo.startswith("context/cenarios/") and caminho.suffix == ".md" and caminho.name != "_modelo.md":
        return CENARIOS
    if relativo.startswith("context/regras-negocio/") and caminho.suffix == ".md" and caminho.name != "conduta-testes.md":
        return CENARIOS
    return None


def main() -> int:
    for fluxo in (sys.stdout, sys.stderr):
        if hasattr(fluxo, "reconfigure"):
            fluxo.reconfigure(encoding="utf-8")
    try:
        evento = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0
    destino = (evento.get("tool_input", {}) or {}).get("file_path")
    if not destino:
        return 0
    caminho = Path(destino)
    validador = escolher_validador(caminho)
    if validador is None or not caminho.exists():
        return 0
    proc = subprocess.run(
        [sys.executable, str(validador), "--arquivo", str(caminho)],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120,
    )
    relatorio = "\n".join(l for l in proc.stdout.splitlines() if not l.startswith("[INFO]")).strip()
    if proc.returncode != 0:
        sys.stderr.write(f"Validação de {caminho.name} encontrou erros ({validador.name}); corrija antes de seguir:\n{relatorio}\n")
        return 2
    if "[AVISO]" in relatorio:
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": f"Avisos de {validador.name} em {caminho.name} (não bloqueiam; resolva ou justifique):\n{relatorio}",
        }}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
