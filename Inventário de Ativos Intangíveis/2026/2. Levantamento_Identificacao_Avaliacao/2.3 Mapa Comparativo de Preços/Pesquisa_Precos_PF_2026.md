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
| 2 | 565,15 | 350 | 09/06/2025 | Secretaria da Segurança Pública e Defesa Social (RN) | Sigma Dataserv Informática | 92553507001232025 / 2 | Desenvolvimento e manutenção por PF |
| 3 | 1.060,00 | 3.000 | 15/08/2025 | Pagadoria de Pessoal da Marinha (RJ) | Indra Brasil | 77320205900022025 / 1 | Pregão. Já constava da amostra de 2025 |
| 4 | 735,00 | 5.000 | 14/11/2025 | Universidade Federal do Cariri (CE) | SIG Software & Consultoria | 15871905900072025 / 2 | Pregão |
| 5 | 750,00 | 1.000 | 10/12/2025 | Ministério Público do Estado do Pará (PA) | Thema Informática | 92598007001142025 / 4 | Fornecedor exclusivo de solução proprietária: sem competição |
| 6 | 2.192,73 | 17.324 | 23/12/2025 | INCRA (DF) | Serpro | 37308306001002025 / 1 | Contratação direta de empresa pública: sem competição |
| 7 | 1.264,22 | 1.000 | 07/01/2026 | Tribunal de Justiça do Pará (PA) | Siedos Sistemas | 92594205900282025 / 4 | Pregão para fornecimento e implantação de solução: PF acessório |
| 8 | 538,00 | 7.000 | 26/02/2026 | Ministério do Desenvolvimento e Assistência Social (DF) | Ibrowse Consultoria | 55000505900182025 / 1 | Pregão |
| 9 | 785,00 | 4.000 | 20/08/2026 | Secretaria Municipal da Educação de Salvador (BA) | Consórcio ASTEC IV | 92706307000382026 / 1 | Desenvolvimento e manutenção evolutiva e corretiva |

Evidências: `Dados_Abertos_Compras/Prints/` (captura do retorno da API por compra) e `Dados_Abertos_Compras/Dados_Brutos/` (retorno integral em JSON e registro das consultas com data e hora).

### Estatísticas preliminares, valores nominais

| Amostra | n | Mínimo | Mediana | Média | Máximo |
|---|---:|---:|---:|---:|---:|
| A (9 preços) | 9 | 538,00 | 750,00 | 938,34 | 2.192,73 |
| A sem os itens 5, 6 e 7 | 6 | 538,00 | 650,08 | 706,36 | 1.060,00 |
| B (ampliada) | 52 | 206,00 | 599,50 | 750,55 | 2.336,13 |

## 5. Ressalvas para a decisão

1. **Itens 5, 6 e 7** não vêm de disputa por fábrica de software. O item 6 (Serpro, R$ 2.192,73) é mais que o dobro do segundo maior preço e tende a formar sozinho um grupo. Recomenda-se justificar a manutenção ou a exclusão no parecer.
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
