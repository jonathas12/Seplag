# Pipeline do Catálogo de Produtos de Software · Inventário 2026

Reúne em um modelo em estrela (`.parquet`) as fontes oficiais do Inventário de Bens Intangíveis 2026 e gera o
projeto Power BI **"Catalogo de Produtos de Software - Inventario 2026"** (PBIP), para publicação no portal SIDE.
Tudo é reproduzível: a mesma execução sobre as mesmas fontes produz os mesmos arquivos e as mesmas conferências.

## Início rápido

```bash
python executar_pipeline.py                     # ETL + documentação
python executar_pipeline.py --reconstruir-pbip  # ETL + documentação + recria o projeto Power BI
```

No Windows, dê duplo clique em `executar_pipeline.bat`. Na primeira execução o script cria o ambiente virtual
`.venv` nesta pasta e instala `requirements.txt` (pandas, pyarrow, openpyxl, pillow). Requer Python 3.11 ou superior.

Depois, abra `../3.3. Power BI/Catalogo de Produtos de Software - Inventario 2026.pbip` no Power BI Desktop, ajuste o
parâmetro **PastaDados** (Transformar dados › Gerenciar parâmetros) para o caminho local de `3.2. Dados/parquet` e
clique em **Atualizar**. O caminho padrão está em `config.toml` (`[powerbi] pasta_dados`).

## Etapas

| # | Script | O que faz | Saída |
|---|---|---|---|
| 1 | `etl_catalogo.py` | Lê as fontes, padroniza a identificação dos produtos, monta dimensões e fatos e confere os totais com os valores publicados | `3.2. Dados/parquet/*.parquet`, `auditoria_etl.csv` |
| 2 | `gera_documentacao.py` | Dicionário de dados e catálogo de medidas | `docs/` |
| 3 | `gera_pbip.py` | Modelo semântico (TMDL), páginas (PBIR), tema 60-30-10, capa e tooltips | `3.3. Power BI/` |
| - | `valida_pbir.py` (opcional) | Valida os JSON do relatório contra os esquemas oficiais da Microsoft | relatório no terminal |

## Fontes (config.toml)

| Fonte | Conteúdo |
|---|---|
| `3.2. Dados/Fontes/Inventario_Sistemas_SITEC-2026.xlsx`, aba Avaliação 2026 | 39 softwares desenvolvidos internamente: PF, preço, VT, VI e VA de 2026 |
| `3.2. Dados/Dados.xlsx` | Histórico das avaliações da comissão (inventários de 2023 a 2025) |
| `3.2. Dados/Fontes/LEVANTAMENTO_INTANGIVEIS_ADQUIRIDOS_2026.xlsx` | 18 licenças, conciliação 2023 a 2026, SEAP e amortização |
| `4. Relatório Final/Laudos Técnicos de Avaliação/*/laudo_*.json` e `resultado_laudo.json` | Ficha de cada produto, módulos, funções, integrações, histórico e custo de projeto |
| `3.2. Dados/Fontes/curadoria_nota_tecnica_03.csv` e `diligencias_nota_tecnica_03.csv` | Documentação, principal achado e diligências (3ª Nota Técnica Consultiva) |

## Modelo em estrela

Dimensões `dProduto` (58 produtos), `dInventario`, `dPrecoPF`, `dDiligencia`, `dTipoFuncao`; fatos `fAvaliacao`
(produto × inventário), `fModulo`, `fFuncao`, `fIntegracao`, `fHistoricoLaudo`, `fCustoProjeto`, `fEconomicidade`,
`fAmortizacaoSEAP`; ponte `bProdutoDiligencia`. Detalhes em `docs/dicionario-dados.md`; medidas em
`docs/catalogo-medidas.md`.

## Conferências automáticas

O ETL só termina com sucesso se todos os totais conferirem (103 conferências), entre elas: VA e PF de cada laudo
contra a aba Avaliação 2026; total dos desenvolvidos (R$ 70.234.996,71); licenças (R$ 3.121.832,16); SEAP
(R$ 5.254.186,60); total de 2026 (R$ 78.611.015,47); totais de 2024 e 2025; custo de projeto registrado
(R$ 9.368.136,99, 9 sistemas); amortização do SEAP. O resultado fica em `3.2. Dados/parquet/auditoria_etl.csv`.

## Páginas do painel

Capa · Visão Geral · Desenvolvidos · Adquiridos · Economicidade · Cenários · Ponte 2025-2026 · Operacional · Ficha do Produto,
e os tooltips Produto e Economia. Todos os cards trazem contexto: variação sobre o inventário anterior (seta e cor: verde para
aumento, vermelho para redução) ou a participação no total.

Só o cabeçalho (abas e logotipo) e a barra de filtros ficam na imagem de fundo das páginas. Cards, quadros, títulos e textos
são visuais nativos (fundo, borda arredondada, sombra, título e subtítulo do próprio visual) e podem ser movidos,
redimensionados e formatados no Power BI Desktop. Os valores e contextos dos cards usam as medidas de texto da pasta
"10. Textos dos cards" (FORMAT na cultura pt-BR), geradas por `gera_pbip.py` a partir do formato de cada medida.

## Cenários e ponte 2025-2026

Explicam o aumento do valor dos desenvolvidos de 2025 (R$ 44,98 mi) para 2026 (R$ 70,23 mi). A ponte decompõe a variação de
cada sistema mantido em sequência: efeito do preço do PF (PF e VI de 2025 ao preço de 2026), efeito do tamanho (variação de PF
ao preço de 2026) e efeito do Valor Institucional (restante); os sistemas novos entram pelo valor integral. A página Cenários
compara, no estilo de placar, dois cenários escolhidos entre: Real 2025; 2025 ao preço de 2026; 2025 ao preço de 2026 com os
sistemas novos; 2025 com o tamanho de 2026 ao preço de 2025; 2026 com o VI de 2025; 2026 ao preço de 2025; Real 2026.

## Economicidade

Compara o que a SEPLAG pagou à fábrica de software do Contrato nº 014/2022/SEPLAG (custo de projeto registrado nos
laudos, TRDs até 07/2026) com o mesmo serviço ao preço de referência do PF do inventário (R$ 1.215,09):

- custo a preço de mercado = custo pago × (R$ 1.215,09 ÷ preço do PF no contrato informado no laudo). O custo pago já
  embute os percentuais de cada grupo de atividades e os deflatores do contrato; por isso a conversão é feita pelo
  preço, e não pelo PF faturado bruto. O resultado é conservador para os pagamentos feitos a preços anteriores
  (R$ 457,00 em 2022, R$ 519,99 em 05/2025);
- retorno por R$ 1,00 = VT e VA de 2026 divididos pelo custo pago.

Limites: o custo não inclui a equipe interna da SEPLAG, e os 30 sistemas sem custo registrado ficam fora da análise
(diligência D15). Para abrir a economicidade por ano, informe em `config.toml` o arquivo `fFaturamento.parquet` gerado
pelo projeto custos-projetos-fsw (`faturamento_trd`).

## Identidade visual

60-30-10: Porcelana Gelada `#E0ECEA` (fundos), Azul Mergulho `#155C78` (estrutura) e Laranja Mandarina `#FF8C42`
(destaque). A foto da capa (`assets/capa_foto_equipe.jpg`) veio das referências de inspiração e deve ser substituída
por uma imagem com direito de uso da SEPLAG antes da publicação; basta trocar o arquivo e rodar
`--reconstruir-pbip`.
