"""Robot Framework variable file: expõe as capabilities e as massas de teste como variáveis.

Os dados de cenário (produtos, preços, endereço...) ficam nos próprios arquivos .robot; locators e
mensagens do app ficam no *** Variables *** de tests/pages/<pagina>.resource.

Fontes:
  tests/config/capabilities.json -> &{CAPABILITIES}
  tests/massas/users.yaml        -> &{USUARIOS}  (massas de login: ${USUARIOS}[<massa>][usuario|senha])

${APPIUM_URL} tem padrão http://127.0.0.1:4723; para outro servidor use --variable APPIUM_URL:<url>.

Uso: Variables    ../libs/app_context.py   (em tests/resources/infraestrutura.resource)
"""
from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]  # tests/libs/app_context.py -> raiz
CAPABILITIES_FILE = ROOT / "tests" / "config" / "capabilities.json"
USERS_FILE = ROOT / "tests" / "massas" / "users.yaml"


def load_users(path: Path = USERS_FILE) -> dict:
    users = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    for name, user in users.items():
        missing = [k for k in ("usuario", "senha") if not (user or {}).get(k)]
        if missing:
            raise ValueError(f"Massa '{name}' em {path.name} sem: {', '.join(missing)}")
        user["senha"] = str(user["senha"])
    return users


def get_variables() -> dict:
    caps = json.loads(CAPABILITIES_FILE.read_text(encoding="utf-8"))["android"]
    return {
        "DICT__CAPABILITIES": caps,
        "APPIUM_URL": "http://127.0.0.1:4723",
        "DICT__USUARIOS": load_users(),
    }
