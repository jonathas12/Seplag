# 1ª Nota Técnica Consultiva - Gestão, contabilização e governança dos softwares da SEPLAG

Versão 0.2, de 16/11/2026. Elaboração: presidência da Comissão de Inventário e Avaliação de Bens Intangíveis.

**Natureza.** Documento consultivo e orientativo. Não altera os valores do inventário de 2026 nem cria obrigação para as unidades. Parte dos processos e documentos citados pode não existir ou não estar ao alcance da comissão; nesses casos, a nota indica o que seria necessário, sem presumir falha de quem executa.

## 1. Situação observada

1. Uma comissão anual faz o levantamento e a avaliação dos softwares.
2. Softwares próprios e personalizados não têm vida útil definida e não há base técnica segura para estimá-la.
3. Aplicações descontinuadas têm o banco de dados mantido em backup, recuperável para consulta.
4. Não se pratica amortização nem redução ao valor recuperável.
5. A manutenção é feita por pessoal próprio, com salários e encargos lançados como despesa operacional.
6. Não há separação organizacional nem de registro entre sustentação (suporte, correção, atualização de infraestrutura) e evolução (novas funcionalidades, melhoria de requisitos).
7. Parte dos sistemas é desenvolvida de forma híbrida: empresa contratada por ponto de função e equipe interna.
8. O ciclo de vida (desenvolvimento, sustentação, evolução, descontinuação) não é mensurado.

## 2. O que as normas dizem sobre cada ponto

| Ponto | Regra | Consequência prática |
|---|---|---|
| Vida útil indefinida | NBC TSP 08 e IN 03/2022, art. 15: aplica-se quando não há limite previsível para o período em que o ativo gera benefícios ou potencial de serviços. | A posição da SEPLAG é defensável para sistemas estruturantes. "Indefinida" não significa "infinita": a classificação precisa de justificativa por sistema e de revisão a cada exercício. |
| Amortização | IN 03/2022, art. 17: ativo de vida útil indefinida não se amortiza. | Correto não amortizar os sistemas próprios. Licenças com prazo contratual têm vida útil definida (art. 16, § 2º) e devem ser amortizadas. |
| Redução ao valor recuperável | IN 03/2022, art. 18, parágrafo único: itens de vida útil indefinida "não estão sujeitos à amortização, devendo-se utilizar somente a perda por redução ao valor recuperável". NBC TSP 09 e 10. | **Aqui a prática atual não se sustenta.** A dispensa de amortização é justamente o que torna o teste de recuperabilidade obrigatório. Sem ele, o ativo só cresce. |
| Sistema descontinuado com banco em backup | IN 03/2022, art. 2º, § 2º, II: software gerado internamente fora de uso por obsolescência não é registrado no intangível. | O backup preserva o dado, não o potencial de serviço da aplicação. Sistema desligado deve ser baixado. Se a base continuar servindo consultas, o que resta é um acervo de dados, a avaliar separadamente. |
| Pessoal interno como despesa | IN 03/2022, art. 10, III, "b": custos de benefícios a empregados compõem o custo do ativo gerado internamente. Art. 9º, VI: exige capacidade de mensurar os gastos do desenvolvimento. | Lançar tudo como despesa é o tratamento correto **enquanto não houver apontamento de horas por sistema e por fase**. Com apontamento, a parcela de desenvolvimento passa a ser capitalizável. |
| Pesquisa e desenvolvimento | IN 03/2022, art. 8º: fase de pesquisa é despesa; fase de desenvolvimento pode ser ativo se atendidos os seis requisitos do art. 9º. | Estudo de viabilidade, prova de conceito e levantamento preliminar são despesa. Construção após a decisão de fazer é custo do ativo. |
| Sustentação | IN 03/2022, art. 10, parágrafo único: manutenção periódica não entra no valor do software. | Suporte, correção de erros, atualização de infraestrutura e adaptação a ambiente são despesa do período. |
| Evolução | NBC TSP 08, gastos subsequentes: capitaliza-se o que aumenta o potencial de serviço além do originalmente previsto. | Nova funcionalidade ou módulo aumenta o ativo. Refatoração e melhoria de desempenho que só preservam a capacidade existente são despesa. |
| Desenvolvimento híbrido | IN 03/2022, art. 10, III: custo incorrido, pela entidade ou por terceiro contratado para esse fim. | A parcela contratada tem custo documentado por ordem de serviço. A parcela interna depende do apontamento. As duas somam no mesmo ativo. |

## 3. O efeito combinado

O modelo atual mede os sistemas por pontos de função e os avalia a preço de mercado (IN, art. 11), método previsto para quando a documentação de custo é insuficiente. Somado à ausência de teste de recuperabilidade e de baixa, isso produz três efeitos:

1. **O gasto real e o ativo registrado não se relacionam.** O desenvolvimento interno já passou pelo resultado como despesa de pessoal. O ativo entra depois, por valor de reposição a preço de terceiros, acrescido de até 100% de Valor Institucional. Não há ligação contábil entre uma coisa e outra.
2. **O saldo só aumenta.** Cada evolução soma pontos de função, a correção monetária eleva o preço unitário e nada reduz o valor.
3. **O valor depende de uma variável de mercado.** Em 2025, o preço adotado foi de R$ 943,25 por ponto de função, com o contrato vigente da própria SEPLAG a R$ 519,99. A escolha entre os grupos de preço moveu dezenas de milhões de reais em um total de R$ 44,9 milhões.

Nada disso indica irregularidade: o método é o da norma estadual e foi aplicado com transparência. O ponto é que a norma o trata como solução de regularização (art. 13), não como regime permanente.

## 4. Riscos de não tratar

### 4.1 Contábeis e de controle

| Risco | Como se manifesta | Severidade |
|---|---|---|
| Superavaliação do ativo e do patrimônio líquido | Sistemas obsoletos ou desligados permanecem no balanço; valor cresce sem contrapartida de gasto | Alta |
| Ressalva nas contas | Auditoria do TCE/MT ou da CGE questiona a ausência de teste de recuperabilidade e de laudo por bem (IN, arts. 18 e 20) | Alta |
| Distorção do resultado | Evolução lançada como despesa subavalia o ativo; sustentação capitalizada o superavalia. Sem critério, ocorrem as duas | Média |
| Ausência de trilha de auditoria | Não é possível demonstrar como se chegou ao valor de um sistema a partir de documentos de origem | Alta |
| Dependência de pessoas | O método está concentrado em poucos servidores e em ferramentas próprias | Média |
| Decisão de investimento sem custo real | Não se sabe quanto custa manter cada sistema, nem se compensa evoluir, substituir ou desligar | Alta |
| Responsabilização | Inventário é documento hábil para ajuste contábil (IN, art. 22); quem assina responde pelo critério | Média |

### 4.2 Tecnológicos

| Risco | Como se manifesta |
|---|---|
| Portfólio sem dono | Sistemas sem gestor de negócio definido, sem decisão formal de continuidade |
| Dívida técnica invisível | Sustentação consome a capacidade da equipe sem aparecer em indicador |
| Obsolescência não percebida | Tecnologia sem suporte, risco de segurança e de indisponibilidade |
| Perda de conhecimento | Documentação e código sem repositório institucional único |
| Propriedade intelectual sem prova | Autoria e titularidade do Estado sem registro, em especial nos desenvolvimentos híbridos |
| Dados sem ciclo de vida | Backups mantidos sem prazo, com custo de armazenamento e exposição à LGPD |

### 4.3 Sobre a comparação com fraudes contábeis

O caso Americanas, divulgado em 2023, envolveu operações de financiamento de fornecedores não registradas como dívida e lançamentos redutores de custo sem lastro documental, mantidos por anos. A situação da SEPLAG é de natureza diferente: não há ocultação, e as limitações estão declaradas no próprio relatório de inventário. A lição que se aproveita é estrutural: saldo relevante sem documento de origem, sem teste periódico e sem conciliação independente acumula distorção sem que ninguém a perceba, até o ajuste ser grande. O remédio é o mesmo em qualquer setor: lastro, segregação de funções e revisão periódica.

### 4.4 Riscos orçamentários

A falta de distinção entre manutenção (custeio, grupo de natureza de despesa 3) e desenvolvimento ou evolução relevante (investimento, grupo 4) pode levar a erro de classificação na execução orçamentária, com efeito sobre indicadores fiscais e limites de gasto.

### 4.5 Síntese dos argumentos para mobilizar as equipes

Pontos trazidos da pesquisa de apoio feita pela presidência e conferidos com a IN 03/2022:

1. **Ativos sem vida.** Sem amortização, sem teste de recuperabilidade e sem baixa, o intangível acumula sistemas desligados que continuam valendo milhões no balanço.
2. **Custo real desconhecido.** Com toda a folha da engenharia de software e os contratos híbridos lançados como despesa indistinta, o Estado não sabe quanto custa desenvolver um sistema e quanto custa mantê-lo. Isso prejudica o sistema de custos do setor público (NBC TSP 34).
3. **Envelhecimento invisível.** Um sistema de doze anos com o mesmo valor contábil de um recém-lançado não mostra à alta gestão a obsolescência do parque, o que dificulta justificar orçamento de modernização.
4. **Sustentação contra evolução.** Sem a separação, a TI não demonstra quanto do esforço vai para manter e quanto gera entrega nova.
5. **Custo total por produto.** Misturar entregas da fábrica de software com horas de servidores, sem critério de apropriação, impede apurar o custo total de propriedade de cada sistema e fragiliza a fiscalização dos contratos.
6. **Controle externo.** Ausência de critério de mensuração, amortização e segregação de gastos é matéria de achado de auditoria e de ressalva nas contas.

### 4.6 Ponto em aberto: vida útil indefinida ou vida útil padrão

Há dois caminhos tecnicamente aceitos, e a escolha cabe à contabilidade:

| Caminho | Como funciona | Vantagem | Exigência |
|---|---|---|---|
| Vida útil indefinida (posição atual) | Não amortiza. Testa a recuperabilidade todo ano e revisa a classificação | Coerente com sistemas estruturantes sem prazo previsível (IN, art. 15) | Teste anual efetivo e baixa dos desligados |
| Vida útil padrão por norma interna | Fixa prazo para softwares próprios, por exemplo 5 anos, com revisão anual por laudo da TI | Simples, previsível, reduz o saldo de forma sistemática | Norma interna e parametrização no sistema patrimonial |

A pesquisa de apoio recomenda o segundo caminho, por analogia com a depreciação de bens móveis. A IN 03/2022 admite os dois. O que ela não admite é a situação atual, sem amortização e sem teste.

## 5. Proposta de regulamentação

### 5.1 Classificação única das demandas

Toda demanda de software recebe, na abertura, uma das classes abaixo. A classe define o tratamento contábil.

| Classe | Definição | Tratamento |
|---|---|---|
| Pesquisa | Estudo, prova de conceito, levantamento antes da decisão de construir | Despesa |
| Desenvolvimento | Construção de sistema ou módulo novo após aprovação do projeto | Custo do ativo |
| Evolutiva | Funcionalidade nova ou ampliação de capacidade em sistema em produção | Custo do ativo |
| Adaptativa | Ajuste a mudança legal, de ambiente ou de plataforma, sem funcionalidade nova | Despesa. Capitaliza apenas se ampliar o potencial de serviço |
| Corretiva | Correção de defeito | Despesa |
| Perfectiva e preventiva | Refatoração, desempenho, atualização de bibliotecas | Despesa |
| Sustentação | Suporte, operação, monitoramento | Despesa |

Referência técnica: ISO/IEC/IEEE 14764 (manutenção de software) e ISO/IEC/IEEE 12207 (processos de ciclo de vida).

### 5.2 Controles mínimos

1. **Catálogo de sistemas** com identificador único, gestor de negócio, gestor técnico, situação, tecnologia, data de entrada em produção e data de desligamento.
2. **Apontamento de esforço** da equipe interna por sistema e por classe de demanda. Basta uma marcação obrigatória na abertura da demanda, na ferramenta de gestão já usada pela TI, e o custo hora médio da categoria com encargos. Só as demandas de desenvolvimento e evolução geram custo de ativo; o restante é despesa do período.
3. **Ordens de serviço da fábrica de software** com sistema e classe identificados, para que o custo contratado seja atribuído ao ativo correto.
4. **Marco de entrada em produção** formal, que encerra a fase de desenvolvimento.
5. **Termo de descontinuação**, que dispara a baixa do ativo e define o destino dos dados.
6. **Linha de base em pontos de função** atualizada a cada entrega evolutiva, não uma vez por ano.
7. **Revisão anual por sistema**: continua em uso, mantém vida útil indefinida, há indício de perda de valor.

### 5.3 Verificação anual no inventário

O gestor de cada sistema responde a três perguntas no fechamento do inventário:

1. O sistema está em produção e com usuários ativos? Se não, baixa contábil, ainda que o banco de dados fique em backup.
2. Há previsão de descontinuidade nos próximos 12 meses? Se sim, registrar a perda por redução ao valor recuperável ou acelerar a amortização.
3. O sistema atende aos requisitos atuais sem necessidade de reconstrução total?

Outros indícios de perda de valor: queda relevante de uso; substituição em curso; tecnologia sem suporte; mudança legal que elimina a finalidade; custo de sustentação crescente e desproporcional; indisponibilidade recorrente.

### 5.4 Papéis

| Unidade | Papel |
|---|---|
| SITEC | Catálogo, classificação das demandas, apontamento, linha de base funcional |
| Gestor de negócio do sistema | Atesta uso, relevância (Valor Institucional) e continuidade |
| Patrimônio | Registro, baixa, guarda da documentação do inventário |
| Contabilidade | Critério de reconhecimento, amortização e teste de recuperabilidade, reflexo no FIPLAN |
| Comissão de inventário | Verificação anual e consolidação, deixando de ser a única fonte da informação |

### 5.5 Implantação em etapas

| Etapa | Prazo sugerido | Entrega |
|---|---|---|
| 1 | Inventário de 2026 | Vida útil justificada por sistema; baixa dos desligados; vida útil remanescente das licenças |
| 2 | 1º semestre de 2027 | Catálogo de sistemas; classificação das demandas; identificação nas ordens de serviço |
| 3 | 2º semestre de 2027 | Apontamento de esforço interno; primeiro ciclo de revisão de indícios de perda |
| 4 | 2028 | Sistemas novos mensurados pelo custo incorrido; pontos de função restritos ao legado |
| 5 | Contínuo | Portaria ou instrução interna consolidando o modelo; proposta de aperfeiçoamento da IN 03/2022 |

## 6. Registro de propriedade intelectual

A IN 03/2022, art. 28, deixa ao órgão decidir sobre o registro para proteção da propriedade intelectual dos ativos inventariados.

| Instrumento | Cabimento | Base legal |
|---|---|---|
| Registro de Programa de Computador (INPI) | Cabível para todos os sistemas próprios. Protege o código-fonte e serve de prova de autoria e titularidade. Procedimento eletrônico, de baixo custo e rápido. | Lei nº 9.609/1998 |
| Registro de Marca (INPI) | Cabível para nomes e sinais de sistemas com identidade perante o público ou outros órgãos. | Lei nº 9.279/1996 |
| Patente | Em regra não cabível: programa de computador em si não é invenção patenteável. Só há espaço quando o software integra solução técnica com efeito além do próprio programa. | Lei nº 9.279/1996, art. 10, V |

Pontos de atenção:

- A titularidade do software desenvolvido por servidor ou por contratada no exercício do contrato é do empregador ou contratante, salvo estipulação em contrário (Lei nº 9.609/1998, art. 4º). Convém que os contratos de fábrica de software tragam cláusula expressa de cessão de direitos e entrega de código-fonte.
- A taxa de registro compõe o custo do ativo (IN 03/2022, art. 10, III, "c").
- O registro não altera o valor do sistema no inventário. Ele reduz o risco jurídico e fortalece o critério de controle exigido para o reconhecimento do ativo.
- Sugere-se começar pelos sistemas de Valor Institucional "imprescindível" e pelos desenvolvidos em regime híbrido.

## 7. Melhorias no ciclo de engenharia de software

| Fase | Prática | Efeito para o inventário |
|---|---|---|
| Concepção | Termo de abertura com estimativa em pontos de função e classe da demanda | Separa pesquisa de desenvolvimento |
| Construção | Ordem de serviço e apontamento por sistema; repositório institucional de código | Custo rastreável; prova de titularidade |
| Entrega | Termo de aceite com contagem detalhada e atualização da linha de base | Dispensa recontagem anual |
| Operação | Indicadores de uso e de custo de sustentação por sistema | Subsidia Valor Institucional e indícios de perda |
| Evolução | Demanda classificada e medida | Capitalização correta |
| Descontinuação | Termo formal, plano de retenção e descarte de dados | Baixa do ativo; conformidade com a LGPD |

## 8. Referências

- IN Conjunta nº 003/2022/SEPLAG/SEFAZ.
- Instrução de Serviço nº 022/2020 - SACE/SEFAZ (registros contábeis de intangíveis).
- NBC TSP 08 - Ativo Intangível; NBC TSP 09 e NBC TSP 10 - Redução ao Valor Recuperável; NBC TSP 34 - Custos no Setor Público.
- Manual de Contabilidade Aplicada ao Setor Público (MCASP), STN.
- CPC 04 (R1) e CPC 01 (R1), como referência do setor privado.
- Lei nº 4.320/1964, arts. 94 a 96.
- Lei nº 9.609/1998 e Lei nº 9.279/1996.
- ISO/IEC 20926 (IFPUG); ISO/IEC/IEEE 12207; ISO/IEC/IEEE 14764; ISO/IEC 19770 (gestão de ativos de software); ISO/IEC 38500; COBIT 2019.
- COSO - Controle Interno, Estrutura Integrada.

Os números de normas e dispositivos acima, exceto os da IN 03/2022, foram citados de memória técnica e devem ser conferidos no texto vigente antes de uso em documento oficial.
