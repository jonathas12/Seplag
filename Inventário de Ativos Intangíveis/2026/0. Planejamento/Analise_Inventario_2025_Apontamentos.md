# Análise do Inventário de 2025 e apontamentos para 2026

Fontes analisadas: `2025/4. Relatório Final` (Relatório v1 e Processo SEPLAG-PRO-2025/27297), `2025/2. Levantamento_Identificacao_Avaliacao/2.3 Mapa Comparativo de Preços` e a IN Conjunta nº 003/2022/SEPLAG/SEFAZ.

> Os apontamentos abaixo resultam do confronto entre o relatório de 2025 e a IN 03/2022. O processo de 2025 analisado termina na CI nº 07050/2025/CPPTI/SEPLAG (entrega à Coordenadoria de Patrimônio e Serviços, 12/12/2025) e não contém manifestação posterior do patrimônio, da contabilidade ou de órgão de controle. Se houver devolutiva formal fora desse arquivo, ela deve ser acrescentada aqui.

## 1. Como o inventário foi feito em 2025

| Etapa | O que foi feito |
|---|---|
| Designação | Portaria nº 138/2025/SEPLAG (DOE de 17/09/2025), prazo 30/10/2025 |
| Escopo | (1) softwares desenvolvidos internamente; (2) softwares licenciados; (3) licenciados e mantidos pela administração |
| Desenvolvidos internamente | Tamanho funcional por Análise de Pontos de Função (IFPUG, níveis indicativo, estimativo e detalhado) × preço de referência do PF, acrescido do Valor Institucional: `VA = VT + (VT × VI)` (IN, art. 11) |
| Preço do PF | 13 preços (Radar TCE/MT descartado, Banco de Preços, atas e contratos federais de 2024, Contrato 014/2022/SEPLAG), corrigidos pelo IPCA até 10/2025, teste IQR sem outliers, agrupamento K-Means em 3 grupos (R$ 633,92; R$ 943,25; R$ 1.174,50). Adotada a média do Grupo 2: **R$ 943,25** (SEPLAG-DIC-2025/36270) |
| Licenciados | Valor de aquisição registrado no sistema legado SIGPAT |
| SEAP | Avaliado em R$ 3.166.000,00, valor do item 3.2 do Contrato nº 043/2020/SEPLAG, vida útil declarada indefinida |
| Entrega | CI nº 07027/2025 e nº 07050/2025/CPPTI/SEPLAG, 11 e 12/12/2025 |

### Resultado de 2025

| Grupo | Bens | Tamanho | Valor (R$) |
|---|---:|---:|---:|
| Desenvolvidos internamente / medidos por PF | 31 | 26.660 PF | 44.976.518,13 |
| Licenciados e licenciados mantidos | 19 | - | 6.287.832,16 |
| **Total** | **50** | | **51.264.350,29** |

## 2. Apontamentos e tratamento em 2026

| # | Apontamento | Base | Tratamento proposto para 2026 |
|---|---|---|---|
| A1 | Entrega em 12/12/2025, após o prazo de 30/10 da portaria. Em 2026 o prazo de 30/10 também venceu. | Portaria, art. 3º, VI e art. 6º | Registrar em ata o replanejamento para 27/11/2026 e solicitar ato formal de prorrogação do prazo. |
| A2 | Não foi localizado, no processo analisado, Laudo Técnico de Avaliação por bem com o conteúdo mínimo exigido. O relatório é consolidado. | IN, art. 5º, VI; art. 20; art. 21 | Emitir laudo por bem (ou por grupo homogêneo, com anexo por bem) contendo descrição, conta contábil, critério de mensuração, vida útil e assinatura. |
| A3 | Vida útil e amortização foram colocadas fora do escopo. Só o SEAP teve vida útil declarada. | IN, art. 5º, IV e V; arts. 14 a 19 | Classificar cada bem como vida útil definida ou indefinida, com justificativa. Bem de vida útil indefinida não se amortiza, mas se sujeita à redução ao valor recuperável (art. 18, parágrafo único). |
| A4 | Softwares licenciados têm vida útil limitada à vigência do contrato de licença, portanto definida e amortizável. O relatório não trata disso. | IN, art. 16, § 2º; art. 17 | Levantar vigência de cada licença, calcular vida útil remanescente e valor amortizável. Excluir licenças com prazo vencido (art. 2º, § 2º, I). |
| A5 | A mensuração por PF é método para software com documentação insuficiente. A regra para ativo gerado internamente é o custo incorrido. O relatório não justifica, por bem, o enquadramento no art. 11. | IN, art. 10, III; art. 11 | Declarar por bem a insuficiência de documentação de custos. Para sistemas novos ou em desenvolvimento com custos rastreáveis (ordens de serviço do Contrato 014/2022), avaliar a mensuração pelo custo. |
| A6 | O preço adotado (R$ 943,25) é 81% superior ao preço do contrato vigente da própria SEPLAG (R$ 519,99). A amostra tinha 13 preços, parte repetida da mesma ata (R$ 886,51 aparece três vezes). | IN, art. 11, § 3º (valor de mercado da FPA) | Ampliar a amostra com fonte oficial (feito: 9 preços Java e 52 de outras linguagens, 2025-2026). Tratar repetições da mesma ata como um único preço. Apresentar análise de sensibilidade do valor total por grupo de preço. |
| A7 | Custos de manutenção periódica não entram no valor do software. Contratos de fábrica de software misturam desenvolvimento, evolução e sustentação no mesmo preço de PF. | IN, art. 10, parágrafo único | Registrar no parecer que o PF de referência remunera desenvolvimento e manutenção evolutiva. Medir apenas funcionalidade entregue (baseline), sem somar demandas corretivas. |
| A8 | SEAP: valor derivado de serviço consultivo sob demanda, com ressalvas do próprio relatório sobre lastro. Há erro de grafia do valor (R$ 3.166.00,00). | IN, art. 6º, parágrafo único, II (mensuração confiável) | Submeter o critério ao setor contábil (IN, art. 27). Verificar situação do Contrato 043/2020 em 2026 e reavaliar. |
| A9 | Licenciados mantidos pela administração: valores "podem sofrer divergências" por múltiplos contratos e aditivos. | IN, art. 12 (valor do conjunto) | Consolidar por sistema, com memória de cálculo por contrato e aditivo. |
| A10 | Marcas, patentes, APIs, painéis, bancos de dados e SaaS ficaram fora do escopo, sem decisão formal sobre registro de propriedade intelectual. | IN, art. 2º, II; art. 28 | Manter fora da mensuração em 2026 e recomendar registro de programa de computador e de marca (ver `5. Governança_Recomendações`). |
| A11 | Não há evidência, no processo, de retorno do setor contábil nem do reflexo no FIPLAN. | Portaria, art. 8º; IN, arts. 21 a 25 | Pedir à CPS e à contabilidade a posição do registro de 2025 antes de fechar 2026, para conciliar saldo inicial. |
| A12 | Falta conciliação entre o inventário anterior e o atual (entradas, baixas, reavaliações). | IN, art. 23 | Incluir no relatório quadro de movimentação 2025 → 2026 por bem. |
| A13 | Forma: numeração do escopo salta o item 5.0, erros de digitação, arquivos de 2024 na pasta de 2025. O relatório cita Aprendizado de Máquina; o método usado é K-Means (agrupamento), não KNN (classificação). | - | Revisão textual; padronizar nomenclatura como K-Means; cada exercício só com seus arquivos. |

## 3. Pontos fortes a manter

- Técnica de medição aderente à ISO/IEC 20926 (IFPUG) e à fórmula da IN.
- Pesquisa de preços documentada, com correção monetária e método estatístico reproduzível.
- Processo único no SIGADOC centralizando os artefatos.
- Repositório versionado com planilhas de medição por sistema, reaproveitáveis como linha de base em 2026.
