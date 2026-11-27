"""Gera o dicionário de dados (a partir dos .parquet) e o catálogo de medidas DAX em docs/."""
import tomllib
from pathlib import Path

import pandas as pd

from medidas import MEDIDAS

AQUI = Path(__file__).resolve().parent
CFG = tomllib.loads((AQUI / "config.toml").read_text(encoding="utf-8"))
DADOS = (AQUI / CFG["saida"]["parquet"]).resolve()
DOCS = (AQUI / CFG["saida"]["documentacao"]).resolve()
DOCS.mkdir(parents=True, exist_ok=True)

DESCR = {
    "dProduto": "Dimensão de produtos: os 39 softwares desenvolvidos internamente, as 18 licenças e o SEAP, com a ficha de cada laudo.",
    "dInventario": "Inventários de 2023 a 2026, com o preço de referência do PF e a portaria da comissão.",
    "dPrecoPF": "Preços do ponto de função: referência de mercado de cada inventário e preços do Contrato nº 014/2022/SEPLAG.",
    "dDiligencia": "Diligências D01 a D19 da 3ª Nota Técnica Consultiva.",
    "dTipoFuncao": "Tipos de função da análise de pontos de função (ALI, AIE, EE, CE, SE).",
    "fAvaliacao": "Fato principal: avaliação de cada produto em cada inventário (PF, preço, VT, VI e VA).",
    "fModulo": "Pontos de função por módulo, conforme o resultado de cada laudo.",
    "fFuncao": "Quantidade de funções e pontos de função por tipo, conforme o resultado de cada laudo.",
    "fIntegracao": "Integrações declaradas em cada laudo.",
    "fHistoricoLaudo": "Histórico de medições registrado em cada laudo.",
    "fCustoProjeto": "Componentes do custo de projeto pago à fábrica de software (laudos com custo de projeto).",
    "fEconomicidade": "Economicidade por sistema: custo pago, mesmo serviço a preço de mercado do PF, economia e retorno por R$ 1,00.",
    "fAmortizacaoSEAP": "Amortização linear do SEAP em 12 parcelas (Contrato nº 001/2026/SEPLAG, cláusula 4.2).",
    "bProdutoDiligencia": "Ponte produto x diligência.",
}

linhas = ["# Dicionário de dados", "", "Gerado por `gera_documentacao.py` a partir dos arquivos em `3.2. Dados/parquet`.", "",
          "## Modelo em estrela", "", "| Tabela | Tipo | Linhas | Descrição |", "|---|---|---:|---|"]
tabs = sorted(DADOS.glob("*.parquet"))
dfs = {p.stem: pd.read_parquet(p) for p in tabs}
for n, df in dfs.items():
    tipo = {"d": "Dimensão", "f": "Fato", "b": "Ponte"}.get(n[0], "")
    linhas.append(f"| {n} | {tipo} | {len(df)} | {DESCR.get(n, '')} |")
linhas += ["", "Relacionamentos (todos 1:N, da dimensão para o fato): dProduto[ID Produto] filtra fAvaliacao, fModulo, fFuncao, fIntegracao,",
           "fHistoricoLaudo, fCustoProjeto, fEconomicidade e bProdutoDiligencia; dInventario[Ano Inventário] filtra fAvaliacao;",
           "dTipoFuncao[Tipo de Função] filtra fFuncao; dDiligencia[Código] filtra bProdutoDiligencia (filtro em ambas as direções, para a",
           "ficha do produto listar as suas diligências).", ""]
for n, df in dfs.items():
    linhas += [f"## {n}", "", DESCR.get(n, ""), "", "| Coluna | Tipo | Exemplo |", "|---|---|---|"]
    for c in df.columns:
        ex = df[c].dropna()
        ex = str(ex.iloc[0])[:70].replace("|", "/").replace("\n", " ") if len(ex) else ""
        linhas.append(f"| {c} | {df[c].dtype} | {ex} |")
    linhas.append("")
(DOCS / "dicionario-dados.md").write_text("\n".join(linhas), encoding="utf-8")

med = ["# Catálogo de medidas DAX", "", "Gerado por `gera_documentacao.py` a partir de `medidas.py`.", ""]
pasta = None
for nome, expr, fmt, folder, desc in MEDIDAS:
    if folder != pasta:
        med += [f"## {folder}", ""]
        pasta = folder
    med += [f"### {nome}", "", desc or "", "", "```dax", expr, "```", ""]
(DOCS / "catalogo-medidas.md").write_text("\n".join(med), encoding="utf-8")
print(f"  dicionário: {len(dfs)} tabelas · catálogo: {len(MEDIDAS)} medidas -> {DOCS}")
