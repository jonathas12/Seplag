# Pesquisa de Preços do Ponto de Função - Exercício 2026

Cuiabá/MT, 16/11/2026.

## 1. Objetivo

Reunir em um só lugar a pesquisa de preços do ponto de função do Inventário de Bens Intangíveis de 2026: objeto de referência, coleta, evidências oficiais, mapa comparativo, análise estatística e manifestação técnica.

## 2. Objeto de referência

O ponto de partida é o **Contrato nº 014/2022/SEPLAG** (KRP Consultoria em Tecnologia de Informação Ltda), firmado por adesão à Ata de Registro de Preços nº 033/2021 da Procuradoria-Geral de Justiça do Tocantins (Pregão Eletrônico nº 015/2021). O preço vigente é **R$ 544,53 por ponto de função**, fixado pelo 5º Termo de Apostilamento (processo SEPLAG-PRO-2026/09621).

O contrato define o recorte da pesquisa porque reúne, no mesmo instrumento, o que os softwares inventariados têm: fábrica de software para desenvolvimento e manutenção, medição em ponto de função pelo IFPUG (Roteiro SISP e CPM 4.3, sem fator de ajuste), tecnologia Java (CatSer 25852) e execução sobre os sistemas da própria SEPLAG. A justificativa completa, com as ressalvas, está na seção 1 da manifestação técnica.

| Ato | Preço por PF | Referência |
|---|---|---|
| Contrato | R$ 457,00 | 05/2022 |
| 4º Termo de Apostilamento | R$ 519,99 | 05/2025 |
| 5º Termo de Apostilamento | R$ 544,53 | 2026, processo SEPLAG-PRO-2026/09621 |

> **Atenção:** o mês-base do 5º apostilamento ainda não foi informado. Enquanto o campo `mes_base_preco_vigente` de `config_pesquisa.json` estiver vazio, o preço do contrato é usado sem correção pelo IPCA.

## 3. Organização da pasta

| Pasta | Conteúdo |
|---|---|
| `1. Objeto de Referência` | Contrato nº 014/2022/SEPLAG, Edital do PE 015/2021 e ARP 033/2021 do MPTO |
| `2. Coleta de Dados` | Scripts de coleta e de montagem do mapa; dados brutos das APIs oficiais, com o registro de cada consulta |
| `3. Evidências` | Ficha em PDF e imagem de cada preço; documentos oficiais baixados do PNCP; script de prints das telas dos portais |
| `4. Mapa Comparativo` | Planilha com a rastreabilidade de cada preço; base completa em CSV; preços da pesquisa de 2025 |
| `5. Análise Estatística` | Notebook executado, gráficos, resultados em JSON e Excel |
| `6. Parecer Técnico` | Manifestação técnica em HTML, PDF e Word, gerada a partir dos resultados |
| `config_pesquisa.json` | Parâmetros da pesquisa: datas, contrato de referência, IPCA e K-Means |

## 4. Fonte e período

API oficial de Dados Abertos do Compras.gov.br, módulo de preços praticados, consultada em 16/11/2026. Compras de 01/01/2025 a 16/11/2026, nos 14 códigos do Catálogo de Serviços do grupo 111. Fundamento: Decreto Estadual nº 1.525/2022.

Resultado: 683 registros; 92 medidos em ponto de função; 9 em Java (amostra), 52 em outras linguagens (comparação) e 31 descartados.

## 5. Rastreabilidade e conferência no PNCP

Cada preço percorre cinco passos, registrados na aba `1 Rastreabilidade Java` da planilha e na ficha da referência: compra de origem, item homologado, preço unitário na origem, correção pelo IPCA e preço usado na análise.

Os 9 preços foram conferidos com o resultado homologado publicado no Portal Nacional de Contratações Públicas, pela API pública do PNCP, que não exige login nem captcha. **Os 9 coincidem ao centavo.** Para cada referência foram baixados os arquivos oficiais da compra (edital, termo de referência, anexos) e dos contratos vinculados, e geradas imagens das páginas em que o preço aparece, com o valor destacado. Tudo está em `3. Evidências/Documentos PNCP`.

| Ref. | Órgão | Modalidade | Preço por PF | Nº de controle PNCP |
|---|---|---|---|---|
| 1 | Casa da Moeda do Brasil | Pregão (SRP) | R$ 555,00 | 34164319000174-1-000162/2024 |
| 2 | Segurança Pública do RN | Inexigibilidade | R$ 565,15 | 00498299000156-1-000018/2025 |
| 3 | Pagadoria de Pessoal da Marinha | Pregão | R$ 1.060,00 | 00394502000144-1-002579/2025 |
| 4 | Universidade Federal do Cariri | Pregão | R$ 735,00 | 18621825000199-1-000021/2025 |
| 5 | Ministério Público do Pará | Inexigibilidade | R$ 750,00 | 05054960000158-1-000186/2025 |
| 6 | INCRA (Serpro) | Dispensa | R$ 2.192,73 | 03204421000122-1-000418/2025 |
| 7 | Tribunal de Justiça do Pará | Pregão | R$ 1.264,22 | 04567897000190-1-000099/2025 |
| 8 | Ministério do Desenvolvimento Social | Pregão | R$ 538,00 | 05526783000165-1-000108/2025 |
| 9 | Secretaria da Educação de Salvador | Inexigibilidade | R$ 785,00 | 13927801000653-1-000030/2026 |

## 6. Reaproveitamento da pesquisa de 2025

Critério da presidência: aproveitar preços com até 13 meses na data da pesquisa. Nenhum dos 13 preços de 2025 atende ao critério. A contratação da Marinha (R$ 1.060,00) já integra a amostra de 2026 como Ref. 3. A comparação completa entre 2025 e 2026 está na seção 7 da manifestação técnica.

## 7. Resultado

Os grupos formados pelo K-Means, com os preços originais e com os atualizados pelo IPCA, os cenários de sensibilidade e a comparação com 2025 estão na manifestação técnica, na pasta `6. Parecer Técnico`. A manifestação não indica preço: a escolha é da presidência da comissão, no Relatório Final.

## 8. Pendências

1. Informar o mês-base do 5º apostilamento em `config_pesquisa.json` e gerar novamente a análise.
2. Tirar os prints das telas do PNCP e do Compras.gov.br com o script `3. Evidências/captura_telas_portais.py`, no computador da SEPLAG.
3. Escolher o preço de referência e registrar a motivação no Relatório Final.

## 9. Como reproduzir

Instruções no documento "Como Executar o Projeto" (PDF), na pasta `2026`.

Elaboração: Jonathas G. Marques, Gerente de projetos e cientista de dados (CPPTI/SITEC/SAAS/SEPLAG), matrícula 280193.
