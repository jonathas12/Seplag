---
name: laudo-avaliacao-intangivel
description: Elabora o Laudo Técnico de Avaliação de um software (bem intangível) da SEPLAG/MT medido por pontos de função, conforme a IN Conjunta nº 003/2022/SEPLAG/SEFAZ, no modelo institucional (HTML, PDF e Word). Inclui análise da documentação (histórias de usuário), leitura e conferência da planilha de contagem APF (abas Contagem e Funções), preenchimento dos quadros "Escopo da Contagem" e "Documentação Utilizada na Análise", cálculo VA = VT + (VT x VI), vida útil e ressalvas. Use quando o usuário pedir o laudo de avaliação, laudo técnico ou laudo de pontos de função de um sistema do inventário de bens intangíveis.
---

# Laudo Técnico de Avaliação de software (IN 03/2022, art. 20)

Um laudo por sistema, sempre com este fluxo. Tom técnico e formal. Nada é inventado: cada afirmação do laudo vem da
documentação do sistema, da planilha de contagem, da Manifestação Técnica da pesquisa de preços ou do usuário.
Decisões do usuário (preço do PF, Valor Institucional e sua justificativa, nível de detalhe, vida útil) não são
alteradas nem "melhoradas"; se algo parecer errado, aponte na resposta e deixe a decisão com ele.

Pasta de trabalho: `Inventário de Ativos Intangíveis/2026` (as ferramentas ficam em `_Modelo_Institucional`).
Python: `.venv/bin/python` (Linux) ou `.venv\Scripts\python.exe` (Windows).

## Entradas a obter do usuário

| Entrada | Exemplo (SICC) |
|---|---|
| Pasta da documentação (Drive ou local) | histórias de usuário em PDF |
| Pasta da APF e versão da linha de base | `Baseline-SICC 2.0-v1.3.xlsx` (usar a última versão) |
| Preço do PF aprovado pela comissão | R$ 1.215,09 (Manifestação Técnica de Aprovação do Preço do PF 2026, `2.3 Mapa Comparativo de Preços/7. Aprovação do Preço`) |
| Códigos Sigadoc | pesquisa SEPLAG-DIC-2026/59836-A; Manifestação da pesquisa SEPLAG-DIC-2026/59842-A; Aprovação do Preço SEPLAG-DIC-2026/59859 (campos `registro_preco`, `fonte_preco_curta`, `preco_fundamento`; copiar de `14. SICC/laudo_SICC.json`) |
| Valor Institucional e justificativa | 0,50, com o motivo dado pelo usuário |
| Nível de detalhe da medição | Estimativa (NESMA) |
| Situação e vida útil | relação de sistemas, aba "Avaliação 2026" |
| Número do sistema na pasta de medições | `14. SICC`, `5. SIGPAS` (mesma numeração de 2025) |
| Custo do projeto (se feito com a fábrica de software) | painel "Custos de Projetos - Fábrica de Software": custo total, componentes, PF faturados, data-base |

Se faltar uma entrada que muda o valor (preço, VI, tamanho), pergunte. As demais vêm da relação de sistemas.

## Passos

1. **Baixar os arquivos.** No Google Drive (`download_file_content`), os binários são gravados em disco; copie-os
   para o scratchpad com nomes legíveis. Baixe também as linhas de base anteriores, para o histórico de medições.
   Ignore duplicatas (mesmo nome e tamanho) e arquivos `~$...` (bloqueio do Excel).

2. **Analisar a documentação.**
   `python _Modelo_Institucional/extrai_historias.py <pasta_pdfs> <scratchpad>/historias.json`
   Leia premissas e histórias para entender finalidade, módulos, perfis, integrações e regras de negócio.
   Guarde os alertas (aprovação sem data, módulo não preenchido, código divergente): entram na resposta e, quando
   afetam a avaliação, nas ressalvas.

3. **Ler e conferir a contagem** (aba Funções; total em `Funções!L4`). Verifique e relate ao usuário, sem alterar a
   contagem dele:
   - soma das funções = total da planilha;
   - toda história de usuário tem função contada e todo grupo contado tem documentação (ou vem da linha de base anterior);
   - funções marcadas como de outra aplicação (fora da fronteira) e AIE possivelmente repetidos;
   - grupos de dados mantidos pelas transações (EE) sem ALI correspondente (possível subcontagem);
   - coerência do nível: na Estimativa NESMA, ALI = 7, AIE = 5, EE = 4, CE = 4, SE = 5;
   - tipo de contagem: se for "Projeto de Desenvolvimento" com tipos de manutenção (I, E, COS...), há três números
     possíveis (só inclusões; PF Local da FS, em `Funções!L6`; PF IFPUG, em `L4`). Pergunte ao usuário qual usar
     (no SIGPAS ele escolheu PF Local da FS) e registre em `medida`;
   - a faixa de linhas somada pela fórmula do total (ex.: `SUM(L11:L846)`): linhas fora dela não entram;
   - grupos com código em formato diferente (ex.: "[US_63]") também são histórias e precisam de módulo;
   - AIE que podem ser dados de código (tipos, unidades, municípios) e AIE repetidos.

4. **Preencher a aba Contagem** (nível de detalhe F7, Escopo A17, Documentação A22) sem perder gráfico e imagem da planilha:
   `python _Modelo_Institucional/preenche_contagem.py origem.xlsx destino.xlsx campos.json`
   Destino: `2. Levantamento_Identificacao_Avaliacao/2.2 Softwares Dev. Internamente/2.1. Medições em APF/<nº. SIGLA>/`.
   O Escopo diz: tipo e nível da contagem, normas, fronteira, módulos, histórias consideradas e o que está fora do escopo.
   A Documentação lista as histórias por módulo com versão e data, mais linhas de base anteriores usadas.

5. **Escrever a configuração do laudo** em `4. Relatório Final/Laudos Técnicos de Avaliação/<nº. SIGLA>/laudo_<SIGLA>.json`,
   copiando a estrutura de `14. SICC/laudo_SICC.json`. Campos de texto (finalidade, VI, integrações, fora do escopo)
   são escritos a partir da documentação e das falas do usuário. `documentos` leva código, nome, versão, data,
   aprovação e link de cada história; `modulos` mapeia número da história para módulo; `grupos_sem_historia`
   cobre grupos da planilha sem história.

   Campos opcionais (ver o cabeçalho de `laudo_apf.py`): `medida`, `formato_us` (ex.: "US{:02d}"), `base_legal`,
   `outros_documentos` (OS, e-mails, normas), `custo_projeto` (sistemas feitos com a fábrica de software do Contrato
   014/2022: componentes do painel de custos, PF faturados, fator do Grupo II da OS), textos específicos do sistema
   (`beneficio`, `texto_tipos`, `texto_evolucao`, `exemplos_tipos`, `motivo_variacao`). Exemplo completo: `5. SIGPAS/laudo_SIGPAS.json`.

6. **Gerar o laudo**:
   `python _Modelo_Institucional/laudo_apf.py "4. Relatório Final/Laudos Técnicos de Avaliação/<nº. SIGLA>/laudo_<SIGLA>.json"`
   O script confere a soma, calcula VT, VA e a comparação com o inventário anterior, gera os gráficos e grava HTML, PDF,
   Word e `resultado_laudo.json`.

7. **Conferir visualmente** o PDF (cards, tabelas, gráficos, anexos) e a coerência dos números com a planilha.

8. **Entregar**: commit semântico em nome do usuário (sem referência a IA), push na branch de trabalho, envio dos
   arquivos (PDF, Word e planilha preenchida) e resposta com: valores (PF, preço, VT, VI, VA), a linha para a relação
   de sistemas (aba Avaliação 2026) e os pontos de atenção da conferência (passos 2 e 3).

## Estrutura do laudo (gerada pelo script)

Cards de resumo; 1 Identificação (inclui identificação contábil, art. 20, II); 2 Descrição detalhada (finalidade,
módulos, integrações e fronteira); 3 Reconhecimento (arts. 2º, 6º, 8º, 9º e 11); 4 Metodologia (etapas, APF, níveis,
preço do PF sem expor parâmetros do K-Means, escala do VI, fórmula); 5 Mensuração (parâmetros, escopo, tipos, módulos,
evolução das linhas de base); 6 Valor (justificativa do VI, cálculo, comparação com o ano anterior); 7 Vida útil;
8 Limitações e ressalvas; 9 Conclusão e assinatura (art. 20, V); Anexo I documentação; Anexo II funções contadas.

## Regras

- Software de terceiro avaliado por PF (ex.: SIAG): ler os contratos e citar as cláusulas de entrega de código-fonte, cessão
  de resultados e restrições de cessão a terceiros (seção 2.3 via `contratos`, `texto_contratos`); vida útil decidida pelo
  usuário, com ressalva do art. 16, § 2º, em `texto_vida_util`. Tamanho composto por partes (medição indicativa sem
  planilha + projetos medidos) vai em `composicao` (exemplo: `26. SIAG/laudo_SIAG.json`).
- Quando houver vários números para o mesmo item (proposta, OFS, parecer, planilhas), apresentar ao usuário e perguntar.

- Evolução do tamanho: usar o registro histórico das avaliações da comissão (`3. Analise de Dados/3.2. Dados/Dados.xlsx`,
  inventários de 2023 a 2025) em `historico_medicoes`, com `inventario`, `data`, `situacao`, `nivel`, `pf` e `uso`;
  não reconstruir a série pelas versões das baselines. Citar a fonte em `fonte_historico`.
- Centavos: VT e VA são calculados sem arredondamento intermediário, como na planilha de avaliação
  (`=SOMA((M*N);M)`); o laudo precisa bater centavo a centavo com a aba Avaliação.
- Data de revisão da baseline: se R10 estiver vazia, perguntar ao usuário e gravar com `preenche_contagem.py`
  (valor "AAAA-MM-DD" é gravado como data).
- Histórias de usuário organizadas por sprint: listar a pasta inteira e usar a versão mais recente de cada história;
  conferir se há histórias sem funções na planilha (ex.: US32 do SIGPAS) e registrar em `ressalvas_extras`.

- Métodos: IFPUG CPM 4.3.1 (ISO/IEC 20926), NESMA (ISO/IEC 24570) e Roteiro de Métricas do SISP versão 2.3 (a do Contrato 014/2022), campo `roteiro_sisp`.
- Unidade de desenvolvimento dos sistemas internos: SSCPG/SAPGD/SEPLAG (não usar SITEC).
- Assinatura: Jonathas Gomes Marques, Presidente da CIABI, "Gerente de projetos e cientista de dados (CPPTI/SSCPG/SAPGD/SEPLAG)" (campo `responsavel.funcao`), Portaria nº 124/2026/SEPLAG, matrícula 280193. Não usar mais a sigla CPPTI/SITEC/SAAS/SEPLAG.
- Preço do PF: citar a pesquisa (Sigadoc SEPLAG-DIC-2026/59836-A), a Manifestação Técnica da pesquisa (SEPLAG-DIC-2026/59842-A), a Manifestação de Aprovação do Preço (Sigadoc SEPLAG-DIC-2026/59859) e as fichas dos preços do grupo (Ref. 3 SEPLAG-CAP-2026/73353-A; Ref. 7 SEPLAG-CAP-2026/73339-A). Ver `7. Aprovação do Preço/aprovacao_preco.json`.
- Sem links para o Google Drive particular do usuário; documentos são citados por código e, quando houver, pelo código do Sigadoc.
- Não citar arquivos .md no laudo; referências a documentos apontam para PDF, planilha ou link.
- Sem travessão longo.
- O K-Means é descrito só conceitualmente, sem parâmetros.
- O preço é decisão da comissão: descreva de onde ele vem (grupo, preços que o compõem, data-base), sem recomendar.
- A ressalva sobre a composição da comissão não entra no laudo (decisão do usuário); o campo `ressalva_comissao` é opcional.

## Sistemas da fábrica de software (Contrato nº 014/2022/SEPLAG) - lições do SISPAT, SIG-SST, PSICO e SIGED

Registro dos laudos de 2026 já entregues (não alterar laudos nem arquivos já gerados de outros sistemas; cada projeto tem sua
especificidade):

| Sistema | Pasta | Medida | PF | VI | VA |
|---|---|---|---|---|---|
| SISPAT | `3. SISPAT` | PF Local da FS (baseline v0.47) | 5.375 | 1,00 | R$ 13.062.217,50 |
| SIG-SST | `1. SST/SIG-SST` | PF Local da FS (baseline v0.15) | 2.416,8 | 1,00 | R$ 5.873.259,02 |
| PSICO | `1. SST/PSICO` | PF Local da FS (baseline v0.9) | 734 | 1,00 | R$ 1.783.752,12 |
| SIGED | `6. SIGED` | PF Local da FS (baseline v0.14) | 1.565,8 | 0,75 | R$ 3.329.528,86 |

Fluxo e regras que se repetiram:

- **Fontes a ler**: processo/DOD no Sigadoc, Ordens de Serviço (Grupo I = requisitos, análise e projeto, 25%; Grupo II =
  construção, testes e homologação, 75%), e-mails de abertura e aceite, documento de escopo (DES), comunicações de
  disponibilização em produção, notícias e normas do sistema. PDFs de e-mail e páginas web costumam ser imagem: converter
  com `pdftoppm` e ler as páginas.
- **Histórias de usuário (docx)**: baixar todas pelo Drive; mapear arquivo ↔ história pelo par `fileId → blob` devolvido
  no download (o código dentro do texto não identifica a história). Versão = nome do arquivo; data = última revisão
  registrada no histórico de versões (a linha "Versão Aprovada" costuma vir sem data). Ler o docx pelo XML
  (`word/document.xml`), porque o python-docx falha quando faltam imagens no pacote.
- **Conferência da baseline**: comparar com a baseline do inventário anterior (hash MD5; o SIG-SST e o PSICO de 2026 eram
  idênticos aos de 2025); conferir a faixa das fórmulas `L4`/`L6` (no PSICO a `L4` parava na linha 202; no SIGED a US_28
  ficou fora de `L11:L753`); funções sem complexidade (não pontuam; relatar a possível subcontagem); grupos sem funções
  ("mesmo processo da US x"); AIE de dados do próprio sistema; ALI repetidos; campo Projeto (F8) incoerente.
- **Histórias contadas sem documento na pasta**: listar com os PF em `ressalvas_extras` e o percentual do tamanho
  (SIG-SST 27,6%; SIGED 53,4%).
- **R10 vazia**: usar a data de mensuração registrada na relação de sistemas (aba Avaliação 2026) e registrar em ressalva.
- **Medida**: PF Local da FS (`Funções!L6`); se o inventário anterior usou PF IFPUG, explicar a diferença em
  `texto_evolucao` e `motivo_variacao`.
- **VI**: decisão do usuário, mesmo quando difere da relação de sistemas (SISPAT 0,75 → 1,00; SIGED 0,50 na relação →
  0,75); escrever a justificativa com fatos documentados (produção, usuários, normas, reconhecimentos externos como o
  XI CNA) e apontar a divergência na resposta.
- **Custo do projeto** (`custo_projeto`): dados do painel "Custos de Projetos - Fábrica de Software" (desenvolvimento,
  tickets, PF de teste, PF faturados, base TRDs). Usar `fator_grupo_contratado` só quando a fábrica executou apenas o
  Grupo II; quando executou os Grupos I e II, omitir o fator e dizer que a diferença entre custo médio e preço do contrato
  não foi decomposta. Não usar a "economia vs mercado" do painel (preço de mercado diferente do aprovado pela comissão).
  Se o usuário não enviar o painel, pedir antes de entregar.
- **Sistemas que são um só na prática mas têm baselines e OS separadas** (SIG-SST e PSICO): um laudo por baseline, com o
  vínculo explicado na finalidade e no fora do escopo; a separação das histórias segue a baseline.
- **Gerador**: `laudo_apf.py` (geral) não deve ser alterado. `laudo_apf_sispat.py` é a cópia com módulos por seção da
  planilha (`secoes`, `modulos_grupo`, `ordem_modulos`, `descricao_modulos`, `quebrar_rotulos_grafico`) e tolera funções
  sem complexidade; foi usado no SISPAT e no SIGED.
- **Entrega**: commit só dos arquivos novos do sistema (conferir `git status` e restaurar arquivos de outros sistemas
  regerados em testes).
