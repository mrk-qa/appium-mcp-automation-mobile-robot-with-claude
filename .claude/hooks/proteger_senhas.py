"""Hook PreToolUse (Write|Edit|MultiEdit|NotebookEdit|Bash|PowerShell): regra 4 do CLAUDE.md.

Bloqueia qualquer escrita ou comando cujo conteúdo contenha a senha de uma massa de tests/massas/users.yaml,
exceto a edição do próprio users.yaml. A mensagem nunca repete a senha.
Código 2 = bloqueia e devolve o motivo ao agente; 0 = libera.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
USERS_FILE = ROOT / "tests" / "massas" / "users.yaml"


def senhas() -> list[str]:
    if not USERS_FILE.exists():
        return []
    texto = USERS_FILE.read_text(encoding="utf-8")
    valores = [v.strip().strip("\"'") for v in re.findall(r"^\s*senha:\s*(.+)$", texto, re.MULTILINE)]
    return sorted({v for v in valores if len(v) >= 4})


def conteudo(tool_input: dict) -> str:
    partes = [tool_input.get(k, "") for k in ("content", "new_string", "command", "new_source")]
    for edicao in tool_input.get("edits", []) or []:
        partes.append(edicao.get("new_string", ""))
    return "\n".join(p for p in partes if isinstance(p, str))


def main() -> int:
    for fluxo in (sys.stdout, sys.stderr):
        if hasattr(fluxo, "reconfigure"):
            fluxo.reconfigure(encoding="utf-8")
    try:
        evento = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0
    tool_input = evento.get("tool_input", {}) or {}
    destino = tool_input.get("file_path") or tool_input.get("notebook_path") or ""
    if destino and Path(destino).resolve() == USERS_FILE.resolve():
        return 0
    texto = conteudo(tool_input)
    if texto and any(s in texto for s in senhas()):
        sys.stderr.write(
            "Bloqueado pelo hook proteger_senhas (regra 4 do CLAUDE.md): o conteúdo contém a senha de uma massa de "
            "tests/massas/users.yaml. Senhas ficam só nesse arquivo; nos testes use `Iniciar App Autenticado    <massa>` "
            "ou `Preencher Senha    ${USUARIOS}[<massa>][senha]`. Não repita a senha em arquivos, comandos ou respostas.\n"
        )
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
