# Estudo Técnico - Custos, Contabilização e Governança dos Produtos de Software

Cuiabá/MT, 18 de novembro de 2026.

> **Natureza do documento:** estudo consultivo e orientativo, para subsidiar a discussão com as áreas de TI, contabilidade, orçamento, patrimônio e controle interno. Não cria obrigação. Todas as normas e dados citados têm a fonte indicada na seção 12; o que é opinião ou proposta da comissão está identificado como tal.

## 1. Objetivo e perguntas que o estudo responde

O objetivo é ligar a engenharia de software às demonstrações contábeis, ao orçamento e à governança de TI, para que a SEPLAG saiba quanto custa construir, evoluir, manter e operar cada software, e trate esses valores corretamente no patrimônio.

| # | Pergunta |
|---|---|
| 1 | Quanto custou construir cada software, considerando a equipe interna e os contratos? |
| 2 | Quanto custa, por ano, manter e operar cada software, e esse custo está subindo ou caindo? |
| 3 | O que deve ir para o ativo intangível (investimento) e o que deve ir para despesa do período (custeio)? |
| 4 | Quando vale mais a pena reconstruir do que manter, ou dar baixa? |
| 5 | Que controles evitam distorções contábeis, como a capitalização indevida de despesas? |
| 6 | O que existe de norma hoje, e o que falta regulamentar em Mato Grosso? |

## 2. Diagnóstico da situação atual

1. **Folha de pagamento sem atribuição ao produto.** O custo da equipe interna é registrado como despesa de pessoal, sem identificar em qual software o esforço foi aplicado.
2. **Sem separação entre construir, evoluir e manter.** Desenvolvimento, melhorias, correções e sustentação são executados pelas mesmas equipes, sem classificação das demandas.
3. **Sustentação não medida.** Correções de erros, manutenções adaptativas, perfectivas e preventivas, suporte e atualizações de infraestrutura não têm esforço registrado por sistema.
4. **DevOps e infraestrutura não alocados.** Esteiras de integração e entrega contínuas (CI/CD), ambientes e servidores não têm custo atribuído aos produtos que os utilizam.
5. **Inventário só pelo valor de mercado.** Como não há custo histórico rastreável, o inventário avalia os softwares pelo tamanho em pontos de função vezes um preço de mercado (IN Conjunta nº 003/2022/SEPLAG/SEFAZ, art. 11). É o método previsto para documentação insuficiente, não um regime permanente.

Esses pontos se ligam aos apontamentos do inventário de 2025 (seção 11).

## 3. Marco normativo

### 3.1 Contabilidade pública e custos

| Norma | O que estabelece | Uso neste estudo |
|---|---|---|
| Lei nº 4.320/1964, arts. 94 a 96 | Registros analíticos dos bens e levantamento geral para o balanço | Base do inventário e do controle patrimonial |
| Lei Complementar nº 101/2000 (LRF), art. 50, § 3º | "A Administração Pública manterá sistema de custos que permita a avaliação e o acompanhamento da gestão orçamentária, financeira e patrimonial" | Obrigação legal de apurar custos |
| NBC TSP 08 - Ativo Intangível | Reconhecimento, fases de pesquisa e desenvolvimento, mensuração, vida útil, amortização | Tratamento contábil do software |
| NBC TSP 34 - Custos no Setor Público (CFC, 18/11/2021) | Diretrizes do sistema de informação de custos; define objeto de custo, recursos, regime de competência e alocação. Aplicação obrigatória desde 1º/01/2024 | O software (produto) como objeto de custo |
| MCASP - Manual de Contabilidade Aplicada ao Setor Público (STN, 11ª edição) | Procedimentos patrimoniais e orçamentários para União, Estados e Municípios | Lançamentos e classificação |
| Manual de Informações do Sistema de Custos - MIC, 2ª edição (Portaria STN nº 454/2025) | Metodologia de custos do Governo Federal: objetos de custo, direcionadores, rateio | Referência de método; aplicação direta é federal |

### 3.2 Contratação e mensuração de software

| Norma | O que estabelece | Uso neste estudo |
|---|---|---|
| IN SGD/ME nº 94/2022 | Planejamento das contratações de soluções de TIC no SISP federal | Referência de processo |
| Portaria SGD/MGI nº 750/2023 (consolidada, alterada pela Portaria SGD/MGI nº 4.777/2026) | Modelo federal de contratação de desenvolvimento, manutenção e sustentação de software. Define sustentação como as atividades para manter disponibilidade, estabilidade e desempenho do software em produção (item 2.1.2) e exige aferição por métricas de produto, com base histórica, em qualquer modalidade (item 12.3) | Separação entre desenvolvimento, manutenção e sustentação |
| Portaria SGD/MGI nº 3.656, de 16/06/2026, e Roteiro de Métricas de Software do SISP v3.0 | Institui o roteiro como guia complementar da Portaria 750, de adoção **preferencial** nos contratos firmados depois de sua publicação. Traz APF, SFP, Story Points Padronizados, Linhas de Código Funcionais e Horas de Serviço Técnico | Métrica de tamanho e de esforço |
| Acórdão nº 1.508/2020-TCU-Plenário (citado no Roteiro v3.0 e na página oficial do modelo de contratação) | Riscos da UST: superestimação, unidades criadas sem padronização, critérios subjetivos, falta de comparabilidade de preços | Cautela com UST |

### 3.3 Mato Grosso

| Norma | O que estabelece | Uso neste estudo |
|---|---|---|
| IN Conjunta nº 003/2022/SEPLAG/SEFAZ | Inventário e mensuração inicial dos intangíveis. Art. 9º, VI: capacidade de mensurar os gastos do desenvolvimento. Art. 10, III, "b": custos de benefícios a empregados compõem o custo do ativo gerado internamente. Art. 10, parágrafo único: manutenção periódica não entra no valor. Art. 23: toda alteração nos intangíveis deve ser comunicada ao setor contábil | Base estadual para capitalizar a folha e para comunicar eventos |
| Portaria nº 124/2026/SEPLAG, art. 8º | Toda alteração de valores patrimoniais deve gerar reflexo no FIPLAN | Comunicação à contabilidade |
| Decreto nº 2.411/2010 | Sistema Contábil do Estado; prevê sistema de custos sob o órgão central de contabilidade | Base para a participação da SEFAZ (verificar texto vigente) |
| Decreto nº 1.208/2021 e IN nº 008/2022/SEPLAG | Sistema Estadual de Tecnologia da Informação e regras de aquisição de TI | Governança estadual de TI (verificar texto vigente) |

> **Atenção:** a pesquisa não encontrou norma de Mato Grosso que obrigue os órgãos a apurar o custo de cada software, separar desenvolvimento de sustentação ou medir a produtividade das equipes internas. A obrigação geral existe (LRF, art. 50, § 3º; NBC TSP 34; IN 03/2022), mas falta o procedimento.

### 3.4 Experiências de outros órgãos

| Órgão e norma | O que faz | Por que interessa |
|---|---|---|
| TJCE - Portaria nº 2.503/2025 | Capitaliza o desenvolvimento interno só depois da fase de pesquisa, com cinco critérios cumulativos (art. 8º, § 2º). A TI envia à área de finanças, até o 10º dia útil de cada mês, o atesto da execução financeira do desenvolvimento, registrado em conta de "softwares em desenvolvimento" (art. 8º, § 5º). Ao fim, emite atesto de entrega definitiva para incorporar o ativo (§ 6º). Vida útil de 3 a 5 anos, com teste anual de recuperabilidade para vida útil indefinida (arts. 12 e 13). Melhorias que ampliam funcionalidade são capitalizadas; suporte e pequenas atualizações são despesa (arts. 19 e 21). A TI comunica formalmente aquisições, desenvolvimentos, melhorias e descontinuidades (art. 23, III) | Modelo pronto de comunicação de eventos e de separação entre investimento e despesa |
| TJPR - Instrução Normativa nº 74/2021 | Procedimentos de reconhecimento, mensuração e amortização dos intangíveis, incluindo softwares | Referência de manual interno |
| SEFAZ-BA - Orientação Técnica nº 72/2020 | Orientação estadual sobre ativos intangíveis | Exemplo de órgão central estadual orientando os demais |

## 4. Ponte entre a engenharia de software e a contabilidade

### 4.1 Cada fase do ciclo de vida tem um tratamento

| Fase ou evento | Exemplos | Tratamento patrimonial | Métrica | Evidência |
|---|---|---|---|---|
| Pesquisa e descoberta | Estudo de viabilidade, prova de conceito, levantamento preliminar | Despesa do período (VPD) | Horas de Serviço Técnico | Relatório de viabilidade |
| Desenvolvimento, depois de comprovada a viabilidade | Construção de sistema ou módulo novo | Ativo intangível em desenvolvimento (conta transitória) | APF ou SFP | Contagem por entrega, atesto mensal |
| Implantação | Entrada em produção | Incorporação definitiva ao ativo; início da amortização ou do teste anual de recuperabilidade | Linha de base em PF | Termo de entrega definitiva |
| Melhoria evolutiva | Funcionalidade nova que amplia a capacidade | Acréscimo ao valor do ativo | APF ou SFP (projeto de melhoria) | Contagem e atesto |
| Manutenção corretiva, adaptativa, perfectiva e preventiva | Correção de defeito, ajuste de ambiente, desempenho, refatoração | Despesa do período | APF com fator de impacto, ou Horas de Serviço Técnico | Registro da demanda |
| Sustentação e suporte | Disponibilidade, estabilidade, desempenho, atendimento | Despesa do período | Horas de Serviço Técnico; níveis de serviço | Relatório de sustentação |
| Infraestrutura e DevOps | Servidores, nuvem, esteira CI/CD, ambientes | Despesa do período, rateada aos produtos | Custo por produto (etiquetagem) | Relatório de alocação |
| Descontinuação | Sistema retirado de produção | Baixa do ativo | - | Termo de descontinuação |

As categorias de manutenção seguem a ISO/IEC/IEEE 14764: corretiva e preventiva formam o grupo de correções; adaptativa e perfectiva, o de melhorias.

### 4.2 Como medir o custo com pontos de função

O ponto de função mede o **tamanho funcional** do software, não o custo. O custo vem da relação entre o tamanho entregue e o custo da equipe que o entregou. O Roteiro do SISP v3.0 (item 9.5) usa essa lógica para o preço de contratos:

| Fórmula do Roteiro v3.0 | Significado |
|---|---|
| Estimativa de custo do PF = Custo mensal do time ÷ Produtividade esperada no mês | Quanto custa cada ponto de função entregue |
| Estimativa de custo do projeto = Tamanho em PF × Custo do PF | Custo do produto |

No exemplo ilustrativo do roteiro, um time de referência de R$ 91.828,18 por mês, com produtividade de 10 horas por PF (58,6 PF por mês), resulta em R$ 1.567,03 por PF. O roteiro alerta que os valores são ilustrativos.

**Aplicação proposta à equipe interna (proposta da comissão):**

1. **Custo mensal da equipe** = remunerações + encargos da equipe alocada ao produto + parcela rateada de infraestrutura e ferramentas.
2. **Produção do mês** = pontos de função entregues e aceitos no produto (APF ou SFP).
3. **Custo interno do PF** = custo mensal da equipe ÷ produção do mês.
4. **Custo do incremento** = PF entregues × custo interno do PF. É o valor que alimenta o ativo em desenvolvimento ou a melhoria.

Isso exige duas coisas que hoje não existem: registro do esforço da equipe por produto e por tipo de demanda, e uma base histórica de produtividade. Sem elas, qualquer valor de custo interno é estimativa.

### 4.3 A engenharia de software inteira, não só a codificação

O Roteiro v3.0 distribui o esforço de referência pelos processos técnicos da ISO/IEC 12207 (Tabela 11):

| Processo técnico | Atividades | Percentual do esforço |
|---|---:|---:|
| P1 - Necessidades e requisitos das partes interessadas | 6 | 16% |
| P2 - Requisitos de sistema/software | 4 | 11% |
| P3 - Arquitetura | 6 | 16% |
| P4 - Projeto (design) | 4 | 11% |
| P5 - Análise do sistema | 3 | 8% |
| P6 - Implementação | 3 | 8% |
| P7 - Integração | 3 | 8% |
| P8 - Verificação | 3 | 8% |
| P9 - Transição | 3 | 8% |
| P10 - Validação | 3 | 8% |
| Total | 38 | 100% |

Requisitos (P1 e P2) somam 27% do esforço; a implementação, só 8%. Medir apenas a codificação deixaria de fora a maior parte do custo. O roteiro permite ajustar esses percentuais (fatores de impacto) à metodologia do órgão, desde que documentado, o que viabiliza medir a especificação de requisitos e cada fase do ciclo.

### 4.4 Fatores de impacto em manutenção (Roteiro v3.0)

| Situação | Fórmula | Fator |
|---|---|---|
| Projeto de melhoria: funções alteradas, desenvolvidas ou mantidas pela mesma empresa (item 7.3) | PF incluído + FI × PF alterado + PF excluído + PF de conversão | 63% |
| Projeto de melhoria: funções alteradas, não desenvolvidas nem mantidas antes pela empresa | idem | 84% |
| Manutenção corretiva fora da garantia, feita pela mesma empresa (item 7.7) | FI × PF alterado | 47% |
| Manutenção corretiva fora da garantia, feita por outra empresa | FI × PF alterado | 55% |

> **Atenção:** os fatores de 63% e 84% se aplicam às funções alteradas em projetos de melhoria. Não significam "manutenção interna" e "manutenção externa", como aparece em algumas pesquisas de internet.

### 4.5 O que o ponto de função não mede

| Trabalho | Métrica indicada | Observação |
|---|---|---|
| Requisitos não funcionais, consultoria, treinamento, suporte, operação | Horas de Serviço Técnico (HST), com catálogo de serviços técnicos (Roteiro v3.0, seção 16) | O roteiro trata a HST como métrica auxiliar, vinculada a entregas aferíveis |
| UST (Unidade de Serviço Técnico) | Usar com cautela | O TCU apontou riscos de superestimação, falta de padrão e subjetividade (Acórdão 1.508/2020) |
| Desempenho da entrega (DevOps) | Métricas DORA: frequência de implantação, tempo de entrega de mudanças, taxa de falha de mudanças, tempo de recuperação | Medem desempenho, não custo |
| Custo de infraestrutura e nuvem | Alocação por etiquetas (prática FinOps) e taxonomia TBM | Atribui o custo de servidores, nuvem e esteiras a cada produto |

## 5. Indicadores de gestão de produto

| Indicador | Cálculo | Para que serve |
|---|---|---|
| Custo total de propriedade (TCO) anual | Desenvolvimento e melhorias + sustentação + infraestrutura + licenças do produto | Saber quanto cada sistema custa por ano |
| Custo interno do PF | Custo da equipe ÷ PF entregues | Comparar com o preço de mercado e com o Contrato nº 014/2022/SEPLAG |
| Proporção de sustentação | Esforço em correção e sustentação ÷ esforço total do produto | Sinal de envelhecimento do sistema |
| Densidade de defeitos | Defeitos em produção ÷ PF da linha de base | Qualidade |
| Métricas DORA | Conforme seção 4.5 | Maturidade da entrega |
| Valor gerado | Serviços prestados, usuários, processos atendidos | Base para avaliar retorno |

**Manter ou reconstruir (proposta de método, não norma):** comparar, para os próximos anos, o custo anual de sustentação projetado do sistema atual com o custo anual equivalente de um sistema novo (custo de construção dividido pela vida útil esperada, mais a sustentação esperada), somados os riscos operacionais. Os percentuais de alerta, como uma proporção de sustentação acima de um patamar, devem ser definidos a partir da base histórica da própria SEPLAG. Não há percentual normativo.

## 6. Riscos de distorção e fraude

| Caso | O que aconteceu | Lição para a gestão de software |
|---|---|---|
| Americanas (2023) | Fato relevante de 11/01/2023 apontou inconsistências de cerca de R$ 20 bilhões. O comitê independente (julho de 2024) indicou lançamentos indevidos na conta de fornecedores, por contratos fictícios de verbas de propaganda cooperada (VPC) e operações de risco sacado. O caso ainda está em apuração na CVM | Lançamento contábil sem lastro em documento real, mantido por anos, sem conciliação independente |
| WorldCom (2002) | A SEC acusou a empresa de capitalizar, em vez de lançar como despesa, cerca de US$ 3,8 bilhões de custos operacionais, para manter o lucro dentro das projeções | É exatamente o risco de classificar sustentação (despesa) como desenvolvimento (ativo) |

Na gestão de software, o risco análogo é a **capitalização indevida**: lançar correções e sustentação como desenvolvimento, inflando o ativo e reduzindo a despesa do período. O caminho inverso também distorce: lançar como despesa o que é investimento subavalia o patrimônio.

**Controles propostos:**

1. Classificação obrigatória de cada demanda na abertura (pesquisa, desenvolvimento, melhoria, manutenção, sustentação), na ferramenta de gestão já usada pela TI.
2. Capitalização só com evidência: contagem de PF aceita, atesto mensal e termo de entrega.
3. Segregação de funções: quem executa não aprova a classificação, e quem aprova não lança na contabilidade.
4. Conciliação mensal entre o registro da TI e o razão contábil.
5. Teste anual de recuperabilidade e baixa dos sistemas descontinuados.
6. Revisão periódica pela Unidade Setorial de Controle Interno.

## 7. Frameworks de governança

| Framework | Prática aplicável | Contribuição |
|---|---|---|
| COBIT 2019 | APO06 - Gerenciar orçamento e custos; BAI01 - Gerenciar programas | Orçamento e custos de TI por serviço e produto; caso de negócio antes do investimento |
| ITIL 4 | Gerenciamento financeiro de serviços | Custos e orçamento dos produtos e serviços digitais |
| ISO/IEC 38500 | Governança corporativa de TI | Responsabilidade da alta administração sobre o uso da TI |
| ISO/IEC 19770 | Gestão de ativos de software | Inventário e ciclo de vida dos ativos de software |
| TBM (Technology Business Management) | Taxonomia de custos de tecnologia | Levar o custo do razão contábil aos produtos (TCO por aplicação) |
| FinOps | Alocação de custos de nuvem por etiquetas | Custo de infraestrutura por produto |
| Métodos ágeis | Backlog classificado; Story Points Padronizados do Roteiro v3.0 | Classificação na origem; medição comparável |

## 8. Comunicação dos eventos do ciclo de vida

Assim como nos bens móveis, toda mudança de situação do software deve ser comunicada às áreas que registram o patrimônio e o orçamento. A base estadual já existe: a IN Conjunta nº 003/2022, art. 23, exige que todas as alterações nos intangíveis sejam comunicadas ao setor contábil, e a Portaria nº 124/2026/SEPLAG, art. 8º, exige reflexo no FIPLAN. O que falta é definir quem informa, quando e com que documento.

| Evento | Quem informa | A quem | Documento | Efeito |
|---|---|---|---|---|
| Início do desenvolvimento (fim da fase de pesquisa) | Gestor do produto e TI | Contabilidade, orçamento, patrimônio | Termo de início, com caso de negócio e viabilidade | Abertura do ativo em desenvolvimento |
| Execução mensal do desenvolvimento | TI | Contabilidade | Atesto mensal de PF entregues e custo apropriado | Registro no ativo em desenvolvimento |
| Implantação (entrada em produção) | TI | Patrimônio e contabilidade | Termo de entrega definitiva e linha de base em PF | Incorporação; início da amortização ou do teste de recuperabilidade |
| Passagem para sustentação | Gestor do produto | Contabilidade e orçamento | Comunicação de passagem | Gastos seguintes passam a despesa |
| Melhoria evolutiva concluída | TI | Patrimônio e contabilidade | Termo de entrega com contagem do projeto de melhoria | Acréscimo ao ativo |
| Descontinuação | Gestor do produto | Patrimônio e contabilidade | Termo de descontinuação e destino dos dados | Baixa do ativo |

## 9. Impactos esperados

| Área | Impacto |
|---|---|
| Contabilidade | Ativo intangível com lastro em custo e evidência; despesa e investimento separados; menos dependência de avaliação a valor de mercado no inventário |
| Orçamento | Planejamento por produto; separação entre investimento e custeio de TI; projeção do custo de sustentação |
| Governança de TI | Portfólio de produtos com custo, valor e risco; decisões de manter, reconstruir ou descontinuar com base em dados |
| Controle | Trilha de auditoria; conciliação; redução do risco de capitalização indevida |
| Equipes | Classificação das demandas e registro de esforço; visibilidade do próprio trabalho |

## 10. Caminho de implantação (proposta da comissão)

| Etapa | Ação | Resultado |
|---|---|---|
| 1 | Levantar práticas de outros órgãos estaduais e tribunais (como TJCE e TJPR) e consultar a contabilidade da SEFAZ-MT sobre o lançamento da capitalização de pessoal | Modelo validado com o órgão central de contabilidade |
| 2 | Piloto em um ou dois produtos: classificação de demandas, registro de esforço, contagem por entrega | Primeira base histórica de custo interno do PF |
| 3 | Política interna da SEPLAG, com o modelo de comunicação de eventos | Procedimento formal |
| 4 | Proposta de Instrução Normativa Conjunta SEPLAG/SEFAZ, a exemplo da IN 03/2022 (minuta anexa) | Norma estadual |
| 5 | Adoção gradual e revisão anual | Melhoria contínua |

## 11. Relação com os apontamentos do inventário de 2025

| Apontamento | Como o estudo contribui |
|---|---|
| A3 e A4 - Vida útil e amortização | Termo de entrega e evento de descontinuação dão a base para vida útil, amortização e baixa |
| A5 - Enquadramento no art. 11 | Com custo histórico, os sistemas novos deixam de depender da avaliação a valor de mercado |
| A7 - Manutenção fora do valor | Classificação das demandas separa manutenção (despesa) de melhoria (ativo) |
| A11 e A12 - Conciliação e FIPLAN | Comunicação de eventos e conciliação mensal |

## 12. Referências

| Referência | Link | Arquivo na pasta Referencias |
|---|---|---|
| Roteiro de Métricas de Software do SISP v3.0 (MGI, 2026) | [gov.br](https://www.gov.br/governodigital/pt-br/estrategias-e-governanca-digital/sisp/documentos/arquivos/roteiro-de-metricas-do-sisp-v3.0.pdf) | Roteiro_Metricas_Software_SISP_v3.0_2026.pdf |
| Portaria SGD/MGI nº 750/2023, consolidada | [gov.br](https://www.gov.br/governodigital/pt-br/contratacoes-de-tic/legislacao/modelo-de-contratacao-de-servicos-de-desenvolvimento-manutencao-e-sustentacao-de-software/portaria-sgd-mgi-no-750-de-20-de-marco-de-2023) | Portaria_SGD-MGI_750-2023_consolidada.pdf |
| Modelo de Contratação de Desenvolvimento, Manutenção e Sustentação de Software | [gov.br](https://www.gov.br/governodigital/pt-br/contratacoes-de-tic/legislacao/modelo-de-contratacao-de-servicos-de-desenvolvimento-manutencao-e-sustentacao-de-software/modelo-de-contratacao) | - |
| Portaria SGD/MGI nº 3.656/2026 (texto) | [okai.com.br](https://okai.com.br/documento/2026-06-17/portaria-sgd-mgi-no-3-656-de-16-de-junho-de-2026) (conferir no DOU) | - |
| NBC TSP 34 - Custos no Setor Público | [Tesouro Nacional](https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/thot/arquivos/publicacoes/53843_1696024/NBCTSP34.pdf) | NBC_TSP_34_Custos_no_Setor_Publico.pdf |
| Manual de Informações do Sistema de Custos, 2ª ed. (Portaria STN nº 454/2025) | [Tesouro Nacional](https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/thot/arquivos/publicacoes/51563_1625344/Manual%20de%20Informa%C3%A7%C3%B5es%20do%20Sistema%20de%20Custos%20-%20MIC%202%C2%AA%20Edi%C3%A7%C3%A3o.pdf) | STN_Manual_Informacoes_Sistema_Custos_MIC_2ed_2025.pdf |
| Custos no setor público (página do Tesouro) | [gov.br](https://www.gov.br/tesouronacional/pt-br/contabilidade-e-custos/custos) | - |
| Lei Complementar nº 101/2000 (LRF) | [Planalto](https://www.planalto.gov.br/ccivil_03/leis/lcp/lcp101.htm) | - |
| Lei nº 4.320/1964 | [Planalto](https://www.planalto.gov.br/ccivil_03/leis/l4320.htm) | - |
| CPC 04 (R1) - Ativo Intangível (setor privado, referência) | [CVM](https://conteudo.cvm.gov.br/export/sites/cvm/menu/regulados/normascontabeis/cpc/CPC_04_R1_rev_12.pdf) | - |
| MCASP 11ª edição | [CNM (cópia)](https://cnm.org.br/storage/noticias/2024/Links/MCASP%20-%2011%C2%AA%20Edi%C3%A7%C3%A3o.pdf) | - |
| IN Conjunta nº 003/2022/SEPLAG/SEFAZ | - | MT_IN_Conjunta_03-2022-SEPLAG-SEFAZ.pdf |
| TJCE - Portaria nº 2.503/2025 | [TJCE](https://www.tjce.jus.br/atos_normativos/portaria-no-2503-2025/) | TJCE_Portaria_2503-2025_ativos_intangiveis.pdf |
| TJPR - Instrução Normativa nº 74/2021 | [TJPR](https://portal.tjpr.jus.br/pesquisa_athos/anexo/6455742) | TJPR_IN_74-2021_ativos_intangiveis.pdf |
| SEFAZ-BA - Orientação Técnica nº 72/2020 | [SEFAZ-BA](https://www.sefaz.ba.gov.br/docs/financas-publicas/orientacoes-tecnicas/ot_72.pdf) | - |
| Acórdão nº 1.508/2020-TCU-Plenário (citado no Roteiro v3.0) | [Pesquisa de jurisprudência do TCU](https://pesquisa.apps.tcu.gov.br/) | - |
| COBIT 2019 e ITIL 4 (correspondência APO06 e gerenciamento financeiro de serviços) | [AXELOS](https://www.axelos.com/resource-hub/white-paper/using-itil-cobit-2019-create-integrated-environment) | - |
| ITIL 4 - Service Financial Management | [AXELOS](https://axelos.com/resource-hub/practice/service-financial-management-itil-4-practice-guide) | - |
| TBM Taxonomy | [TBM Council](https://www.tbmcouncil.org/taxonomy) | - |
| FinOps - Cost Allocation | [FinOps Foundation](https://www.finops.org/framework/capabilities/cost-allocation/) | - |
| Simple Function Point (IFPUG SFP) | [Wikipedia](https://en.wikipedia.org/wiki/The_Simple_Function_Point_method) | - |
| ISO/IEC 20926 (IFPUG) | [IEC Webstore](https://webstore.iec.ch/en/publication/10866) | - |
| Americanas - comitê independente (2024) | [InfoMoney](https://www.infomoney.com.br/?p=2619928) e [NeoFeed](https://neofeed.com.br/negocios/comite-de-investigacao-da-americanas-detalha-fraude-e-acusa-diretoria-anterior) | - |
| Americanas - fato relevante de jan/2023 e reconhecimento da fraude | [Mercado & Consumo](https://mercadoeconsumo.com.br/13/06/2023/destaque-do-dia/americanas-documentos-analisados-por-assessores-juridicos-indicaram-fraude/) | - |
| WorldCom - ação da SEC (2002) | [SEC Litigation Release 17588](https://www.sec.gov/litigation/litreleases/2002/lr17588.htm) | - |
| Aplicação da APF na estimativa de custos de software (SBC/WCGE) | [SBC](https://sol.sbc.org.br/index.php/wcge/article/download/33023/32820/) | - |

> **Atenção:** os itens marcados para conferência (Decretos nº 2.411/2010 e nº 1.208/2021, IN nº 008/2022/SEPLAG, Portaria nº 3.656/2026 no DOU e a vigência das partes do MCASP 11ª edição) foram localizados em fontes secundárias e devem ser confirmados no texto oficial antes de citação em documento formal.

Elaboração: Jonathas G. Marques, Gerente de projetos e cientista de dados (CPPTI/SITEC/SAAS/SEPLAG), matrícula 280193.
