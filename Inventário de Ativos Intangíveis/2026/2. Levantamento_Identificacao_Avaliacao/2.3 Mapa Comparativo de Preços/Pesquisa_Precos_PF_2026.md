# Pesquisa de Preços do Ponto de Função — 2026

Coleta realizada em 16/11/2026 para subsidiar a análise de agrupamento e o parecer técnico do preço de referência.

## 1. Objeto de referência

Contrato nº 014/2022/SEPLAG (KRP Consultoria em Tecnologia de Informação Ltda), por adesão à ARP nº 033/2021 da Procuradoria-Geral de Justiça do Tocantins (Pregão Eletrônico nº 015/2021): serviço técnico especializado, continuado, na modalidade de fábrica de software para sustentação, manutenção, desenvolvimento e melhorias de sistemas, medido em **ponto de função**. Preço original de R$ 457,00/PF (05/2022); R$ 519,99/PF após o quarto apostilamento (05/2025). Documentos em `Contrato_014-2022-SEPLAG/`.

Verificar se houve novo apostilamento ou aditivo em 2026 e atualizar este valor.

## 2. Fonte

API oficial de Dados Abertos do Compras.gov.br (Ministério da Gestão e da Inovação em Serviços Públicos), módulo **Pesquisa de Preço — Preços Praticados**, serviço `3_consultarServico`, e módulo **ARP**, serviço `2_consultarARPItem`.

- Endereço: `https://dadosabertos.compras.gov.br`
- Catálogo: CatSer, grupo 111 (Serviços de desenvolvimento e manutenção de software), 14 códigos ativos.
- Período: data da compra de 01/01/2025 a 16/11/2026.
- Fundamento: Decreto Estadual nº 1.525/2022 e IN SEGES/ME nº 65/2021 (contratações similares da Administração Pública e sistemas oficiais de governo).

O PNCP (`pncp.gov.br`) não respondeu às consultas feitas a partir do ambiente de trabalho. O Radar de Preços do TCE/MT, o Banco de Preços e as atas em PDF não foram consultados nesta coleta e dependem de acesso manual.

## 3. Resultado da coleta

| Etapa | Registros |
|---|---:|
| Preços praticados nos 14 códigos CatSer | 683 |
| Com unidade de medida Ponto de Função | 92 |
| Amostra A — aderente (Java, PF) | 9 |
| Amostra B — ampliada (PF, outras linguagens) | 52 |
| Descarte sugerido | 31 |

Critério de descarte sugerido: quantidade inferior a 100 PF, ou preço unitário abaixo de R$ 100,00 ou acima de R$ 3.000,00. São registros em que a unidade PF foi lançada para item de outra natureza (mensalidade, sprint, valor global). O descarte é sugestão e pode ser revisto na coluna `classificacao` do CSV.

Arquivo completo: `Precos_Ponto_Funcao_2025-2026.csv` (separador `;`).

## 4. Amostra A — Java, medido em ponto de função

CatSer 25852 (Desenvolvimento de novo software — Java) e 25925 (Manutenção evolutiva de software — Java).

| ID | Preço/PF (R$) | Qtde PF | Data | Órgão (UF) | Fornecedor | Compra / item | Observação |
|---:|---:|---:|---|---|---|---|---|
| 1 | 555,00 | 2.000 | 17/02/2025 | Casa da Moeda do Brasil (RJ) | M.I. Montreal Informática | 17908305900612024 / 1 | Pregão, registro de preços |
| 2 | 565,15 | 350 | 09/06/2025 | Secretaria da Segurança Pública e Defesa Social (RN) | Sigma Dataserv Informática | 92553507001232025 / 2 | Inexigibilidade: sem competição |
| 3 | 1.060,00 | 3.000 | 15/08/2025 | Pagadoria de Pessoal da Marinha (RJ) | Indra Brasil | 77320205900022025 / 1 | Pregão. Já constava da amostra de 2025 |
| 4 | 735,00 | 5.000 | 14/11/2025 | Universidade Federal do Cariri (CE) | SIG Software & Consultoria | 15871905900072025 / 2 | Pregão |
| 5 | 750,00 | 1.000 | 10/12/2025 | Ministério Público do Estado do Pará (PA) | Thema Informática | 92598007001142025 / 4 | Inexigibilidade, fornecedor exclusivo de solução proprietária |
| 6 | 2.192,73 | 17.324 | 23/12/2025 | INCRA (DF) | Serpro | 37308306001002025 / 1 | Dispensa, contratação direta de empresa pública |
| 7 | 1.264,22 | 1.000 | 07/01/2026 | Tribunal de Justiça do Pará (PA) | Siedos Sistemas | 92594205900282025 / 4 | Pregão para fornecimento e implantação de solução: PF acessório |
| 8 | 538,00 | 7.000 | 26/02/2026 | Ministério do Desenvolvimento e Assistência Social (DF) | Ibrowse Consultoria | 55000505900182025 / 1 | Pregão |
| 9 | 785,00 | 4.000 | 20/08/2026 | Secretaria Municipal da Educação de Salvador (BA) | Consórcio ASTEC IV | 92706307000382026 / 1 | Inexigibilidade: sem competição |

Evidências: `Referencias_PDF/` (ficha em PDF por referência), `Dados_Abertos_Compras/Prints/` (captura do retorno da API por compra) e `Dados_Abertos_Compras/Dados_Brutos/` (retorno integral em JSON e registro das consultas com data e hora).

### Links das referências da Amostra A

| ID | Modalidade | Processo | Nº de controle PNCP | PNCP | Compras.gov.br |
|---:|---|---|---|---|---|
| 1 | Pregão - Eletrônico (SRP) | 104880/2023 | 34164319000174-1-000162/2024 | [abrir](https://pncp.gov.br/app/editais/34164319000174/2024/162) | [abrir](https://cnetmobile.estaleiro.serpro.gov.br/comprasnet-web/public/landing?destino=acompanhamento-compra&compra=17908305900612024) |
| 2 | Inexigibilidade | 00510027.001290/2024-72 | 00498299000156-1-000018/2025 | [abrir](https://pncp.gov.br/app/editais/00498299000156/2025/18) | [abrir](https://cnetmobile.estaleiro.serpro.gov.br/comprasnet-web/public/landing?destino=acompanhamento-compra&compra=92553507001232025) |
| 3 | Pregão - Eletrônico | 63438014037202481 | 00394502000144-1-002579/2025 | [abrir](https://pncp.gov.br/app/editais/00394502000144/2025/2579) | [abrir](https://cnetmobile.estaleiro.serpro.gov.br/comprasnet-web/public/landing?destino=acompanhamento-compra&compra=77320205900022025) |
| 4 | Pregão - Eletrônico | 23507000052202547 | 18621825000199-1-000021/2025 | [abrir](https://pncp.gov.br/app/editais/18621825000199/2025/21) | [abrir](https://cnetmobile.estaleiro.serpro.gov.br/comprasnet-web/public/landing?destino=acompanhamento-compra&compra=15871905900072025) |
| 5 | Inexigibilidade | GEDOC Nº 165845/2025 | 05054960000158-1-000186/2025 | [abrir](https://pncp.gov.br/app/editais/05054960000158/2025/186) | [abrir](https://cnetmobile.estaleiro.serpro.gov.br/comprasnet-web/public/landing?destino=acompanhamento-compra&compra=92598007001142025) |
| 6 | Dispensa | 54000.167145/2025-85 | 03204421000122-1-000418/2025 | [abrir](https://pncp.gov.br/app/editais/03204421000122/2025/418) | [abrir](https://cnetmobile.estaleiro.serpro.gov.br/comprasnet-web/public/landing?destino=acompanhamento-compra&compra=37308306001002025) |
| 7 | Pregão - Eletrônico | 0000622-60.2025.8 | 04567897000190-1-000099/2025 | [abrir](https://pncp.gov.br/app/editais/04567897000190/2025/99) | [abrir](https://cnetmobile.estaleiro.serpro.gov.br/comprasnet-web/public/landing?destino=acompanhamento-compra&compra=92594205900282025) |
| 8 | Pregão - Eletrônico | 71000013915202417 | 05526783000165-1-000108/2025 | [abrir](https://pncp.gov.br/app/editais/05526783000165/2025/108) | [abrir](https://cnetmobile.estaleiro.serpro.gov.br/comprasnet-web/public/landing?destino=acompanhamento-compra&compra=55000505900182025) |
| 9 | Inexigibilidade | 177037/2026 | 13927801000653-1-000030/2026 | [abrir](https://pncp.gov.br/app/editais/13927801000653/2026/30) | [abrir](https://cnetmobile.estaleiro.serpro.gov.br/comprasnet-web/public/landing?destino=acompanhamento-compra&compra=92706307000382026) |

No PNCP, a página da compra traz o edital, o termo de referência, a ata de registro de preços e o contrato, na aba de arquivos. As 61 referências das Amostras A e B têm os mesmos links nas colunas `link_pncp`, `link_compras_gov` e `link_api_item` do CSV e da planilha.

PDFs: `Mapa_Comparativo_Precos_PF_2026.pdf` (mapa consolidado com links) e `Referencias_PDF/` (uma ficha por referência da Amostra A, com preço, objeto, fornecedor, processo e links). As fichas reproduzem os dados da API oficial e não substituem a ata ou o contrato.

### Estatísticas preliminares, valores nominais

| Amostra | n | Mínimo | Mediana | Média | Máximo |
|---|---:|---:|---:|---:|---:|
| A (9 preços) | 9 | 538,00 | 750,00 | 938,34 | 2.192,73 |
| A, apenas pregões (itens 1, 3, 4, 7 e 8) | 5 | 538,00 | 735,00 | 830,44 | 1.264,22 |
| A, pregões de fábrica de software (itens 1, 3, 4 e 8) | 4 | 538,00 | 645,00 | 722,00 | 1.060,00 |
| B (ampliada) | 52 | 206,00 | 599,50 | 750,55 | 2.336,13 |

## 5. Ressalvas para a decisão

1. **Modalidade.** Só cinco das nove referências vêm de pregão (itens 1, 3, 4, 7 e 8). Os itens 2, 5 e 9 são inexigibilidade e o item 6 é dispensa (Serpro), sem disputa de preço. O item 7 é pregão para fornecimento e implantação de solução, em que o PF é acessório. O item 6 (R$ 2.192,73) é mais que o dobro do segundo maior preço e tende a formar sozinho um grupo. Recomenda-se justificar no parecer a manutenção ou a exclusão de cada um.
2. **Item 3** é a mesma contratação usada em 2025 (R$ 1.060,00). Mantê-lo é válido, sem duplicar com a fonte anterior.
3. **Valores nominais.** Falta a correção pelo IPCA de cada data de compra até a data-base do estudo, com a ferramenta `Atualização_Monetária_IPCA.py`.
4. **Amostra pequena.** Nove preços aderentes. A Amostra B serve para análise de sensibilidade, não para compor o preço de referência, por se tratar de tecnologias diferentes da padronizada na SITEC.
5. **Preço e quantidade homologados.** A API informa o preço praticado no resultado da compra. Para os itens escolhidos, juntar ao processo a ata de registro de preços ou o contrato em PDF, obtidos no PNCP ou no Compras.gov.br pelo identificador da compra.
6. **Fontes privadas.** Não foram coletadas cotações de fornecedores. Se desejado, a cotação direta é parâmetro subsidiário no Decreto Estadual nº 1.525/2022.

## 6. Próximos passos

1. Correção monetária da Amostra A.
2. Análise de agrupamento (K-Means, três grupos) e definição do grupo de referência.
3. Parecer técnico em `Parecer Técnico/`, com a motivação da escolha e a análise de sensibilidade do valor total do inventário.

## 7. Como reproduzir

```bash
cd Dados_Abertos_Compras && python3 coleta_precos_compras_gov.py
```

```bash
cd Dados_Abertos_Compras && python3 gera_mapa_comparativo.py
```

Executar a partir de `Dados_Abertos_Compras/`. Os dados brutos ficam em `Dados_Brutos/`. A API é pública e dispensa credencial.
