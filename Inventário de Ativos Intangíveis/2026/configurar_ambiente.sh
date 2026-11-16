#!/usr/bin/env bash
# Cria o ambiente Python do projeto e instala as bibliotecas (Linux / macOS).
# Uso: bash configurar_ambiente.sh
set -euo pipefail
cd "$(dirname "$0")"
PY=""
for c in python3.13 python3.12 python3.11 python3; do
  if command -v "$c" >/dev/null && "$c" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)'; then PY="$c"; break; fi
done
[ -z "$PY" ] && { echo "Python 3.11+ não encontrado."; exit 1; }
echo "1/4 Usando $PY"
[ -x .venv/bin/python ] || "$PY" -m venv .venv
echo "2/4 Instalando as bibliotecas..."
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
echo "3/4 Instalando o navegador Chromium do Playwright..."
.venv/bin/python -m playwright install chromium
echo "4/4 Registrando o kernel do Jupyter..."
.venv/bin/python -m ipykernel install --user --name inventario-2026 --display-name "Inventario 2026 (.venv)"
echo "Ambiente pronto. Ative com: source .venv/bin/activate   e rode: python executar.py --tudo"
