---
name: contagem-detalhada-apf
description: Faz a contagem DETALHADA de pontos de função (IFPUG CPM 4.3.1, com tipos de dados e arquivos ou registros referenciados por função) de aplicações, projetos de desenvolvimento ou projetos de melhoria, com os fatores de impacto do Roteiro de Métricas do SISP, e revisa contagens apresentadas por contratadas (fábricas de software, fornecedores SaaS), gerando a planilha no modelo institucional e o Laudo Técnico de Revisão de Pontos de Função com conciliação. Use quando pedirem contagem detalhada, revisão ou auditoria de contagem de PF de fornecedor, conferência de orçamento ou medição em pontos de função, projeto de melhoria com fator de impacto.
---

# Contagem detalhada de pontos de função (IFPUG) e revisão de contagens

Terceiro nível de detalhe, depois da indicativa (`contagem-indicativa-apf`: só funções de dados, 35/15 PF) e da
estimativa (`contagem-estimativa-apf`: funções de dados e de transação com complexidade padrão). Na detalhada, cada
função tem seus tipos de dados (TD/DER) e arquivos referenciados (AR/FTR) ou registros lógicos (RLR/RET) contados, e a
complexidade sai da tabela IFPUG. Pasta de trabalho: `Inventário de Ativos Intangíveis/2026`; Python `.venv/bin/python`.

## Tabelas IFPUG (CPM 4.3.1)

| Tipo | Baixa | Média | Alta |
|---|---|---|---|
| ALI | 7 | 10 | 15 |
| AIE | 5 | 7 | 10 |
| EE | 3 | 4 | 6 |
| CE | 3 | 4 | 6 |
| SE | 4 | 5 | 7 |

- **ALI e AIE (RLR x DER):**
  - 1 RLR: até 50 DER baixa, 51 ou mais média;
  - 2 a 5 RLR: até 19 baixa, 20 a 50 média, 51 ou mais alta;
  - 6 ou mais RLR: até 19 média, 20 ou mais alta.
- **EE (AR x DER):**
  - 0 a 1 AR: até 15 baixa, 16 ou mais média;
  - 2 AR: até 4 baixa, 5 a 15 média, 16 ou mais alta;
  - 3 ou mais AR: até 4 média, 5 ou mais alta.
- **SE e CE (AR x DER):**
  - 0 a 1 AR: até 19 baixa, 20 ou mais média;
  - 2 a 3 AR: até 5 baixa, 6 a 19 média, 20 ou mais alta;
  - 4 ou mais AR: até 5 média, 6 ou mais alta.

A planilha institucional aplica essas regras sozinha (colunas F, H e I da aba Funções) quando D (TD) e E (AR) são
números. Com D ou E vazios, ela assume a complexidade padrão (ALI/AIE baixa, transações média): registre isso na coluna O.

## Regras de contagem que mais geram divergência

- **DER:** campo único reconhecido pelo usuário, inclusive mensagens e botões que disparam a ação (um por processo). Não contam campos técnicos (IDs internos, chaves geradas).
- **AR/FTR:** cada ALI mantido ou lido e cada AIE lido pela transação.
  - Tabelas temporárias, de controle ou de log técnico **não** são arquivo lógico.
  - Dados de código (tipos, situações) não contam como AR.
- **Processos elementares distintos:** mesma tela com lógica diferente (importação automática e manual, inclusão e alteração) conta separadamente. Mesma lógica em canais diferentes conta uma vez.
- **Combo-box:** é uma CE (lista de dados de ALI/AIE), não altera o ALI. A função de dados só é alterada quando a demanda inclui, altera ou exclui DER ou RLR do grupo de dados (ex.: novo campo gravado).
- **Novo campo em integração ou tela (cenários a confirmar com a contratada):**
  1. Apenas filtro na API ou na consulta, sem gravar: não altera ALI.
  2. Gravado na fronteira como campo novo: ALI alterado.
  3. Gravado, mas o campo já existe no sistema (outro módulo ou tela): campo repetido não é contado.
  4. Nova lista de seleção, nova e única: CE incluída (100%); se lista igual já existir, não conta.

  Gerar uma planilha por cenário e perguntar à contratada se outras funções (alterações, consultas, listagens,
  relatórios) passaram a usar o campo.
- **Versão do Roteiro SISP:** verificar no contrato. Se não estiver definida, recomendar formalizar a versão (a 3.0 é a mais recente, com mudanças técnicas e de critério) e apontar indícios de regras diferentes na planilha da contratada (ex.: fator de exclusão 0,3 contra 0,4 da versão 2.3).
- **Integração:**
  - dados de outro sistema lidos pela aplicação são AIE;
  - mudança no que é lido (novo campo da API) altera o AIE;
  - gravar o novo campo nos dados da aplicação altera o ALI também.

## Projeto de melhoria (Roteiro SISP)

- Conte só as funções incluídas (I, 100%), alteradas e excluídas (E, 40%) pela demanda.
- **Alteração:**
  - **A50** (50%): função desenvolvida ou já alterada pela empresa atual. Use para produto da própria contratada.
  - **A75** (75%): função de outra empresa.
  - **A90** (90%): A75 com redocumentação.
- Outros deflatores na aba Deflatores: COR, ARN, PFT (testes, 15%), AER e demais.
- **Duas grandezas, nomes claros:** nos laudos, não escrever "PF bruto / PF".
  - **"Tamanho das funções afetadas (PF IFPUG)"** (`Funções!L4`) é o tamanho completo das funções tocadas, como se construídas do zero.
  - **"Tamanho da demanda (PF a aceitar)"** (`Funções!L6`, PF Local da FS) é esse tamanho multiplicado pelo fator de impacto. É o que se aceita e mede.
  - Analogia: a área da cozinha (12 m²) é uma coisa, o tamanho da reforma é outra.
  - Uma função incluída entra com 100% nas duas grandezas.
- Funções de teste e itens não mensuráveis só entram se a demanda os previr.

## Passos

1. **Ler os requisitos** (ERS, histórias, OS): identificar o que é incluído, alterado e excluído, e o que está fora do
   escopo (telas não alteradas). PDF escaneado: ler as páginas como imagem.
2. **Ler a contagem da contratada**, que pode estar em outro modelo (ex.: planilha SISP do fornecedor em .xls):
   - converter com `soffice --headless --convert-to xlsx` e ler valores e fórmulas;
   - conferir função a função: tipo, operação, DER, AR/RLR, complexidade, PF e fator de impacto;
   - conferir os totais e as fórmulas de resumo (faixas que não cobrem as linhas, abas ocultas com totais parciais);
   - conferir os campos de identificação (contrato, solicitante, datas).
3. **Responder às dúvidas do solicitante** com a regra IFPUG aplicável e a evidência da especificação. Quando a
   evidência for insuficiente, apresentar cenários com o tamanho de cada um.
4. **Gravar a contagem revisada**:
   ```
   python _Modelo_Institucional/gera_contagem_detalhada.py modelo.xlsx destino.xlsx contagem.json
   ```
   - **Grupos:** `[nome, tipo, manutenção, TD, AR, observação]`. Registre na observação "Contratada: ..." e a decisão da revisão.
   - **Modelo:** uma planilha institucional, ex.: `2.1. Medições em APF/23. Revisa Consignados/APF-Revisão de Contratos Consignações-v1.2.xlsx`.
   - **Conferência automática:** o script grava TD/AR como números, força o recálculo no LibreOffice e confere L4 (bruto) e L6 (com deflatores) com o esperado pela tabela IFPUG.
   - **Aba Contagem:** `contagem` (F6 "Projeto de Melhoria" ou "Aplicação", F7 "Detalhada (IFPUG)", F9 responsável original, F10 revisor, R9/R10 datas, A12, A17, A22).
5. **Laudo Técnico de Revisão**:
   ```
   python _Modelo_Institucional/laudo_revisao_apf.py "<pasta>/laudo_revisao.json"
   ```
   O JSON é uma lista de blocos (seção, parágrafo, tabela, lista, caixa). Exemplo completo:
   `5. Governança_Recomendações/Revisoes_Contagem/2026-11 SEDUC SAFF Integracao FIPLAN/laudo_revisao.json`. Estrutura:
   1. identificação;
   2. objeto e escopo (o que não é analisado);
   3. documentos analisados, citando os anexos não recebidos;
   4. método;
   5. requisitos da demanda;
   6. análise da contagem da contratada (tabelas de funções de dados e de transação: contratada x revisão x situação);
   7. questões específicas;
   8. inconsistências formais;
   9. **conciliação e recomendações**: tabela por item (contratada x revisão x diferença), cenários quando houver condição, recomendações separadas para a contratante, a contratada e a área financeira ou fiscalização;
   10. conclusão e assinatura.
6. **Conferir o PDF** e entregar a planilha revisada, o PDF e o DOCX.
   - Não commitar os documentos recebidos: contrato, e-mails e planilha do fornecedor têm dados pessoais e de terceiros.

## Estilo e limites

- **Escopo:** só a contagem. Não opinar sobre preço do PF, enquadramento contratual ou trâmites, salvo pedido expresso; a conciliação é em pontos de função.
- **Tom:** técnico, em terceira pessoa ("o analista", "a revisão constatou"), sem adjetivos, sem travessão longo.
- **Laudo como perícia:**
  - abrir com preâmbulo (camada de governança consultiva e orientativa, imparcial; quem pediu e por quê) e uma pergunta-guia;
  - explicar ponto de função em linguagem simples (metro quadrado, os 5 tipos com exemplos da própria demanda);
  - mostrar a conta da contratada passo a passo, com ícones discretos de situação (✅ confere, ⚠️ ajuste, ❓ em aberto);
  - na conciliação, explicar "o que foi contado, o que a revisão constatou, por quê e o efeito". Cada divergência cita o requisito (item da ERS) e a regra.
- **Contratada correta:** quando a contagem da contratada está correta, dizer isso claramente e separar as inconsistências formais, que não mudam o total, das que mudam o tamanho.
- **Assinatura:** Jonathas Gomes Marques, "Analista de métricas de software (Análise de Pontos de Função)", "Gerente de projetos e cientista de dados (CPPTI/SSCPG/SAPGD/SEPLAG)", matrícula 280193.
