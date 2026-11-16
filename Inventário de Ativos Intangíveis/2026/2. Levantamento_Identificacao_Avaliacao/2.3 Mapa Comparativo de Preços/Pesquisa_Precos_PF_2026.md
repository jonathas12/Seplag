# PESQUISA DE PREÇOS DO PONTO DE FUNÇÃO - EXERCÍCIO 2026

Cuiabá/MT, 16/11/2026.

## 1. OBJETIVO

Reunir, em um só lugar, a pesquisa de preços do ponto de função do Inventário de Bens Intangíveis de 2026: o objeto de referência, a coleta, as evidências, o mapa comparativo, a análise estatística e o parecer técnico.

## 2. ORGANIZAÇÃO DA PASTA

| Pasta | Conteúdo |
|---|---|
| `1. Objeto de Referência` | Contrato nº 014/2022/SEPLAG, Edital do Pregão Eletrônico nº 015/2021 e ARP nº 033/2021 do Ministério Público do Tocantins |
| `2. Coleta de Dados` | Scripts de coleta e os dados brutos devolvidos pela API oficial, com o registro de cada consulta |
| `3. Evidências` | Ficha em PDF e print de cada um dos 9 preços; script para capturar prints e arquivos no PNCP e no Compras.gov.br |
| `4. Mapa Comparativo` | Planilha com a rastreabilidade de cada preço e arquivo CSV com a base completa |
| `5. Análise Estatística` | Notebook executado, gráficos e resultados |
| `6. Parecer Técnico` | Manifestação técnica com os grupos de preços, as evidências e as limitações |

## 3. FONTE E PERÍODO

API oficial de Dados Abertos do Compras.gov.br (`dadosabertos.compras.gov.br`), módulo de preços praticados, consultada em 16/11/2026. Compras de 01/01/2025 a 16/11/2026, nos 14 códigos do Catálogo de Serviços do grupo 111. Fundamento: Decreto Estadual nº 1.525/2022.

Resultado: 683 registros, dos quais 92 medidos em ponto de função. Destes, 9 em Java (amostra), 52 em outras linguagens (comparação) e 31 descartados.

## 4. RASTREABILIDADE DOS PREÇOS

Cada preço percorre cinco passos, todos registrados na aba `1 Rastreabilidade Java` da planilha e na ficha da referência:

1. Compra de origem: órgão, modalidade, número da compra e processo.
2. Item homologado: número do item, código do catálogo e quantidade.
3. Preço unitário na origem, com a data da compra.
4. Correção pelo IPCA até 10/2026, com o fator aplicado.
5. Preço usado na análise.

| Ref. | Preço na origem (R$) | Preço atualizado (R$) | Órgão | Modalidade | Nº de controle PNCP | PNCP | Compras.gov.br |
|---:|---:|---:|---|---|---|---|---|
| 1 | 555,00 | 601,41 | Casa da Moeda do Brasil | Pregão (SRP) | 34164319000174-1-000162/2024 | [abrir](https://pncp.gov.br/app/editais/34164319000174/2024/162) | [abrir](https://cnetmobile.estaleiro.serpro.gov.br/comprasnet-web/public/landing?destino=acompanhamento-compra&compra=17908305900612024) |
| 2 | 565,15 | 597,00 | Segurança Pública do RN | Inexigibilidade | 00498299000156-1-000018/2025 | [abrir](https://pncp.gov.br/app/editais/00498299000156/2025/18) | [abrir](https://cnetmobile.estaleiro.serpro.gov.br/comprasnet-web/public/landing?destino=acompanhamento-compra&compra=92553507001232025) |
| 3 | 1.060,00 | 1.114,16 | Pagadoria de Pessoal da Marinha | Pregão | 00394502000144-1-002579/2025 | [abrir](https://pncp.gov.br/app/editais/00394502000144/2025/2579) | [abrir](https://cnetmobile.estaleiro.serpro.gov.br/comprasnet-web/public/landing?destino=acompanhamento-compra&compra=77320205900022025) |
| 4 | 735,00 | 769,02 | Universidade Federal do Cariri | Pregão | 18621825000199-1-000021/2025 | [abrir](https://pncp.gov.br/app/editais/18621825000199/2025/21) | [abrir](https://cnetmobile.estaleiro.serpro.gov.br/comprasnet-web/public/landing?destino=acompanhamento-compra&compra=15871905900072025) |
| 5 | 750,00 | 783,30 | Ministério Público do Pará | Inexigibilidade | 05054960000158-1-000186/2025 | [abrir](https://pncp.gov.br/app/editais/05054960000158/2025/186) | [abrir](https://cnetmobile.estaleiro.serpro.gov.br/comprasnet-web/public/landing?destino=acompanhamento-compra&compra=92598007001142025) |
| 6 | 2.192,73 | 2.290,10 | INCRA (Serpro) | Dispensa | 03204421000122-1-000418/2025 | [abrir](https://pncp.gov.br/app/editais/03204421000122/2025/418) | [abrir](https://cnetmobile.estaleiro.serpro.gov.br/comprasnet-web/public/landing?destino=acompanhamento-compra&compra=37308306001002025) |
| 7 | 1.264,22 | 1.316,01 | Tribunal de Justiça do Pará | Pregão | 04567897000190-1-000099/2025 | [abrir](https://pncp.gov.br/app/editais/04567897000190/2025/99) | [abrir](https://cnetmobile.estaleiro.serpro.gov.br/comprasnet-web/public/landing?destino=acompanhamento-compra&compra=92594205900282025) |
| 8 | 538,00 | 558,20 | Ministério do Desenvolvimento Social | Pregão | 05526783000165-1-000108/2025 | [abrir](https://pncp.gov.br/app/editais/05526783000165/2025/108) | [abrir](https://cnetmobile.estaleiro.serpro.gov.br/comprasnet-web/public/landing?destino=acompanhamento-compra&compra=55000505900182025) |
| 9 | 785,00 | 790,01 | Secretaria da Educação de Salvador | Inexigibilidade | 13927801000653-1-000030/2026 | [abrir](https://pncp.gov.br/app/editais/13927801000653/2026/30) | [abrir](https://cnetmobile.estaleiro.serpro.gov.br/comprasnet-web/public/landing?destino=acompanhamento-compra&compra=92706307000382026) |

## 5. EVIDÊNCIAS

As fichas e os prints da pasta `3. Evidências` reproduzem os dados públicos devolvidos pela API oficial. Não substituem o edital, a ata ou o contrato.

Os portais PNCP e Compras.gov.br exigem verificação hCaptcha antes de exibir os dados, o que impede a captura automática a partir do ambiente de trabalho em nuvem. Para obter os prints das telas e os arquivos oficiais, usar o script `3. Evidências/captura_evidencias_pncp.py` no computador do servidor, com o navegador visível. O script ainda não foi testado nos portais e pode exigir ajuste.

## 6. REAPROVEITAMENTO DA PESQUISA DE 2025

Critério informado pela presidência: aproveitar preços com até 13 meses na data da pesquisa, ou seja, a partir de 10/2025.

Nenhum dos 13 preços de 2025 atende ao critério. As atas e os contratos federais são de 08 a 10/2024, e o contrato da SEPLAG foi atualizado em 05/2025. A contratação da Marinha (R$ 1.060,00, de 08/2025) já integra a amostra de 2026 como referência 3. As duas contratações do Banco de Preços sem data nos arquivos de 2025 (R$ 650,00 e R$ 1.182,09) dependem de verificação. O detalhe está na aba `5 Pesquisa 2025` da planilha.

Pelo mesmo critério, as referências 1, 2 e 3 da amostra de 2026 também ficam fora da janela. O cenário C3 da análise mostra o resultado só com os seis preços dentro da janela.

## 7. RESULTADO DA ANÁLISE

| Cenário | Preços | Mediana (R$) | Grupo 1 (R$) | Grupo 2 (R$) | Grupo 3 (R$) |
|---|---:|---:|---:|---:|---:|
| C1 - 9 preços | 9 | 783,30 | 683,16 | 1.215,09 | 2.290,10 |
| C2 - sem o outlier | 8 | 776,16 | 585,54 | 780,78 | 1.215,09 |
| C3 - janela de 13 meses | 6 | 786,65 | 725,13 | 1.316,01 | 2.290,10 |
| C4 - apenas pregões | 5 | 769,02 | 579,81 | 769,02 | 1.215,09 |

Preços atualizados pelo IPCA até 10/2026. Os valores dos grupos são os centroides do K-Means. O detalhamento, os gráficos e as limitações estão na manifestação técnica da pasta `6. Parecer Técnico`.

## 8. PENDÊNCIAS

1. Capturar os prints e os arquivos oficiais no PNCP e no Compras.gov.br.
2. Verificar se houve reajuste do Contrato nº 014/2022/SEPLAG em 2026.
3. Verificar a data das duas contratações do Banco de Preços de 2025.
4. Escolher o preço de referência e registrar a motivação no Relatório Final.

## 9. COMO REPRODUZIR

A partir da pasta `2. Coleta de Dados`, executar na ordem: `coleta_precos_compras_gov.py`, `gera_mapa_comparativo.py`, `enriquece_links_referencias.py`, `atualiza_ipca_rastreabilidade.py`. Em seguida, executar o notebook da pasta `5. Análise Estatística` e, por fim, `gera_planilha_e_fichas.py`.

Elaboração:

Jonathas G. Marques

Gerente de projetos e cientista de dados (CPPTI/SITEC/SAAS/SEPLAG)

Matrícula: 280193
