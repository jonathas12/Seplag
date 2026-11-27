"""Valida os JSON do relatório PBIR contra os esquemas oficiais (microsoft/json-schemas, obtidos pelo GitHub).
Uso opcional: python valida_pbir.py  (requer: pip install jsonschema requests)"""
import json, sys, tomllib
from functools import lru_cache
from pathlib import Path
import requests
from jsonschema import Draft7Validator
from referencing import Registry, Resource

AQUI = Path(__file__).resolve().parent
CFG = tomllib.loads((AQUI / "config.toml").read_text(encoding="utf-8"))
RAIZ = (AQUI / CFG["powerbi"]["pasta"]).resolve()
BASE_MS = "https://developer.microsoft.com/json-schemas/"
BASE_GH = "https://raw.githubusercontent.com/microsoft/json-schemas/main/"


@lru_cache(None)
def baixa(uri):
    r = requests.get(uri.replace(BASE_MS, BASE_GH), timeout=30)
    r.raise_for_status()
    return r.json()


def recupera(uri):
    return Resource.from_contents(baixa(uri.split("#")[0]))


reg = Registry(retrieve=recupera)
erros, n = 0, 0
for arq in sorted(RAIZ.rglob("*.json")) + sorted(RAIZ.rglob("*.pbir")) + sorted(RAIZ.rglob("*.pbip")) + sorted(RAIZ.rglob("*.pbism")):
    d = json.loads(arq.read_text(encoding="utf-8"))
    esq = d.get("$schema") if isinstance(d, dict) else None
    if not esq or "json-schemas/fabric" not in esq:
        continue
    n += 1
    v = Draft7Validator(baixa(esq), registry=reg)
    for e in sorted(v.iter_errors(d), key=lambda e: list(e.path))[:5]:
        erros += 1
        print(f"{arq.relative_to(RAIZ)}: {'/'.join(map(str, e.path))}: {e.message[:200]}")
print(f"{n} arquivos validados; {erros} erros")
sys.exit(1 if erros else 0)
