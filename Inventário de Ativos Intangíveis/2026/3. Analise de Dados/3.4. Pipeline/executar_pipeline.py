"""
Executor único da pipeline do Catálogo de Produtos de Software (Inventário 2026).

Na primeira execução cria o ambiente virtual .venv nesta pasta, instala as dependências de
requirements.txt e reexecuta a si mesmo dentro dele. Depois roda, em ordem:

  1. etl_catalogo.py      fontes oficiais -> ../3.2. Dados/parquet/*.parquet + auditoria_etl.csv
  2. gera_documentacao.py dicionário de dados e catálogo de medidas (docs/)
  3. gera_pbip.py         modelo semântico (TMDL) e relatório (PBIR) do Power BI   [--reconstruir-pbip]

Uso:
  python executar_pipeline.py                     ETL + documentação
  python executar_pipeline.py --reconstruir-pbip  ETL + documentação + recria o projeto Power BI
  python executar_pipeline.py --somente-etl       apenas o ETL
"""
import os
import subprocess
import sys
import venv
from pathlib import Path

AQUI = Path(__file__).resolve().parent
VENV = AQUI / ".venv"
PY = VENV / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def no_venv():
    return Path(sys.prefix).resolve() == VENV.resolve()


def prepara_ambiente():
    if not PY.exists():
        print("Criando o ambiente virtual em", VENV)
        venv.EnvBuilder(with_pip=True).create(VENV)
    marca = VENV / ".requisitos_ok"
    req = (AQUI / "requirements.txt").read_text(encoding="utf-8")
    if not marca.exists() or marca.read_text(encoding="utf-8") != req:
        print("Instalando dependências (requirements.txt)...")
        subprocess.run([str(PY), "-m", "pip", "install", "-q", "--upgrade", "pip"], check=True)
        subprocess.run([str(PY), "-m", "pip", "install", "-q", "-r", str(AQUI / "requirements.txt")], check=True)
        marca.write_text(req, encoding="utf-8")


def etapa(script, *args):
    print(f"\n== {script} ==")
    r = subprocess.run([sys.executable, str(AQUI / script), *args], cwd=AQUI)
    if r.returncode:
        sys.exit(f"Falha em {script} (código {r.returncode}). Veja as mensagens acima.")


if __name__ == "__main__":
    if not no_venv():
        prepara_ambiente()
        sys.exit(subprocess.run([str(PY), str(Path(__file__).resolve()), *sys.argv[1:]]).returncode)
    etapa("etl_catalogo.py")
    if "--somente-etl" not in sys.argv:
        etapa("gera_documentacao.py")
    if "--reconstruir-pbip" in sys.argv:
        etapa("gera_pbip.py")
    print("\nPipeline concluída.")
