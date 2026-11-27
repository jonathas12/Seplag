# Dicionário de dados

Gerado por `gera_documentacao.py` a partir dos arquivos em `3.2. Dados/parquet`.

## Modelo em estrela

| Tabela | Tipo | Linhas | Descrição |
|---|---|---:|---|
| bProdutoDiligencia | Ponte | 108 | Ponte produto x diligência. |
| dDiligencia | Dimensão | 19 | Diligências D01 a D19 da 3ª Nota Técnica Consultiva. |
| dInventario | Dimensão | 4 | Inventários de 2023 a 2026, com o preço de referência do PF e a portaria da comissão. |
| dPrecoPF | Dimensão | 7 | Preços do ponto de função: referência de mercado de cada inventário e preços do Contrato nº 014/2022/SEPLAG. |
| dProduto | Dimensão | 58 | Dimensão de produtos: os 39 softwares desenvolvidos internamente, as 18 licenças e o SEAP, com a ficha de cada laudo. |
| dTipoFuncao | Dimensão | 5 | Tipos de função da análise de pontos de função (ALI, AIE, EE, CE, SE). |
| fAmortizacaoSEAP | Fato | 12 | Amortização linear do SEAP em 12 parcelas (Contrato nº 001/2026/SEPLAG, cláusula 4.2). |
| fAvaliacao | Fato | 186 | Fato principal: avaliação de cada produto em cada inventário (PF, preço, VT, VI e VA). |
| fCustoProjeto | Fato | 19 | Componentes do custo de projeto pago à fábrica de software (laudos com custo de projeto). |
| fEconomicidade | Fato | 9 | Economicidade por sistema: custo pago, mesmo serviço a preço de mercado do PF, economia e retorno por R$ 1,00. |
| fFuncao | Fato | 163 | Quantidade de funções e pontos de função por tipo, conforme o resultado de cada laudo. |
| fHistoricoLaudo | Fato | 117 | Histórico de medições registrado em cada laudo. |
| fIntegracao | Fato | 149 | Integrações declaradas em cada laudo. |
| fModulo | Fato | 192 | Pontos de função por módulo, conforme o resultado de cada laudo. |

Relacionamentos (todos 1:N, da dimensão para o fato): dProduto[ID Produto] filtra fAvaliacao, fModulo, fFuncao, fIntegracao,
fHistoricoLaudo, fCustoProjeto, fEconomicidade e bProdutoDiligencia; dInventario[Ano Inventário] filtra fAvaliacao;
dTipoFuncao[Tipo de Função] filtra fFuncao; dDiligencia[Código] filtra bProdutoDiligencia (filtro em ambas as direções, para a
ficha do produto listar as suas diligências).

## bProdutoDiligencia

Ponte produto x diligência.

| Coluna | Tipo | Exemplo |
|---|---|---|
| ID Produto | str | SISPAT |
| Código | str | D10 |

## dDiligencia

Diligências D01 a D19 da 3ª Nota Técnica Consultiva.

| Coluna | Tipo | Exemplo |
|---|---|---|
| Código | str | D01 |
| Objeto | str | Cessões da Autodesk AEC (N6500051) e da Adobe Creative Cloud (N6500050 |
| Destinatário | str | Coordenadoria de Infraestrutura e Serviços de TI; patrimônio setorial |
| Fundamento | str | IN, arts. 2º, § 2º, I; 16, § 2º; 23 |
| Prazo Sugerido | str | Prioritária: 10/12/2026 |
| Prioritária | str | Sim |
| Ordem | int64 | 1 |

## dInventario

Inventários de 2023 a 2026, com o preço de referência do PF e a portaria da comissão.

| Coluna | Tipo | Exemplo |
|---|---|---|
| Ano Inventário | int64 | 2023 |
| Inventário | str | 2023 |
| Preço PF Mercado (R$) | float64 | 705.6 |
| Portaria | str | Portaria nº 077/2023/SEPLAG |
| Data de Referência | datetime64[ms] | 2023-12-31 00:00:00 |
| Fonte do Preço | str | Inventário de 2023 (Dados.xlsx) |

## dPrecoPF

Preços do ponto de função: referência de mercado de cada inventário e preços do Contrato nº 014/2022/SEPLAG.

| Coluna | Tipo | Exemplo |
|---|---|---|
| Referência | str | Mercado - inventário 2023 |
| Tipo | str | Mercado |
| Data | datetime64[ms] | 2023-12-31 00:00:00 |
| Preço PF (R$) | float64 | 705.6 |
| Fonte | str | Dados.xlsx |

## dProduto

Dimensão de produtos: os 39 softwares desenvolvidos internamente, as 18 licenças e o SEAP, com a ficha de cada laudo.

| Coluna | Tipo | Exemplo |
|---|---|---|
| ID Produto | str | SISPAT |
| Sigla | str | SISPAT |
| Nome do Produto | str | Sistema de Gestão Patrimonial |
| Nome no Inventário | str | Sistema de Gestão Patrimonial |
| Categoria | str | Desenvolvido internamente |
| Grupo | str | Software desenvolvido internamente e/ou medido por pontos de função |
| Situação | str | Em produção |
| Situação Resumida | str | Em produção |
| Situação na Avaliação | str | Produção |
| Tecnologia | str | Java |
| Nível de Medição | str | Detalhada (IFPUG) |
| Medida PF | str | PF Local da FS |
| Vida Útil | str | Indefinida |
| Valor Institucional | float64 | 1.0 |
| Faixa Valor Institucional | str | Imprescindível |
| Unidade de Desenvolvimento | str | SEPLAG/MT (SSCPG/SAPGD/SEPLAG): requisitos, gestão de produto e de pro |
| Tipo de Bem | str | Software desenvolvido pela SEPLAG em conjunto com a fábrica de softwar |
| Propriedade | str | Desenvolvido pela SEPLAG com a fábrica de software do Contrato nº 014/ |
| Finalidade | str | O Sistema de Gestão Patrimonial (SISPAT) é a ferramenta do Estado de M |
| Benefício | str | Controle, avaliação, contabilização e inventário do patrimônio imobili |
| Base Legal | str | Lei Estadual nº 11.109/2020 (gestão patrimonial da administração estad |
| Áreas de Negócio | str | Superintendência de Patrimônio Público (SPP) da Secretaria Adjunta de  |
| Perfis de Usuário | str | Gestores patrimoniais central e setoriais, avaliadores, comissões e su |
| Justificativa do VI | str | O SISPAT é o sistema corporativo de gestão do patrimônio imobiliário e |
| Uso | str | Em produção (módulos Imobiliário e Inventário de Bens Imóveis em uso p |
| Integrações | str | FIPLAN (Sistema Integrado de Planejamento, Contabilidade e Finanças);  |
| Qtde Integrações | int64 | 8 |
| Qtde Módulos | int64 | 11 |
| Qtde Funções | float64 | 1172.0 |
| Documentação | str | Com lacunas |
| Principal Achado | str | 24 histórias com funções contadas não localizadas |
| Diligências | str | D10 |
| Ressalva de Documentação | str | O conteúdo e a qualidade das histórias de usuário são de responsabilid |
| Ressalvas | str | Das 214 histórias com funções contadas, 24 não foram localizadas na pa |
| Motivo da Variação | str | A variação decorre de três fatores: o aumento do tamanho funcional (de |
| Fora do Escopo | str | Requisitos não funcionais e atividades de sustentação, que não compõem |
| Linha de Base | str | APF- Baseline do SIABI - CELAD, SISPAT e Inventario de Bens - v0.47.xl |
| Data da Avaliação | datetime64[ms] | 2026-11-11 00:00:00 |
| Laudo | str | LAUDO_TECNICO_AVALIACAO_SISPAT_2026.pdf |
| Pasta do Laudo | str | 4. Relatório Final/Laudos Técnicos de Avaliação/3. SISPAT |
| Nº Laudo | int64 | 3 |
| Patrimônio | str |  |
| Fornecedor | str | SEPLAG (equipe interna e/ou fábrica de software) |
| Contrato | str |  |
| Tipo de Licença | str |  |
| Prazo da Licença | str |  |
| Data de Aquisição | datetime64[ms] | 2022-08-15 00:00:00 |
| Data Fim | datetime64[ms] | 2026-07-19 00:00:00 |
| Situação da Licença | str |  |
| Tem Custo de Projeto | str | Sim |

## dTipoFuncao

Tipos de função da análise de pontos de função (ALI, AIE, EE, CE, SE).

| Coluna | Tipo | Exemplo |
|---|---|---|
| Tipo de Função | str | ALI |
| Descrição | str | Arquivo Lógico Interno |
| Natureza | str | Dado |
| Ordem | int64 | 1 |

## fAmortizacaoSEAP

Amortização linear do SEAP em 12 parcelas (Contrato nº 001/2026/SEPLAG, cláusula 4.2).

| Coluna | Tipo | Exemplo |
|---|---|---|
| Parcela | int64 | 1 |
| Início do Período | datetime64[ms] | 2026-01-26 00:00:00 |
| Fim do Período | datetime64[ms] | 2026-02-25 00:00:00 |
| Amortização do Mês (R$) | float64 | 437848.88 |
| Amortização Acumulada (R$) | float64 | 437848.88 |
| Valor Contábil Líquido (R$) | float64 | 4816337.72 |
| Marco | str |  |

## fAvaliacao

Fato principal: avaliação de cada produto em cada inventário (PF, preço, VT, VI e VA).

| Coluna | Tipo | Exemplo |
|---|---|---|
| ID Produto | str | DBV |
| Ano Inventário | int64 | 2024 |
| Categoria | str | Desenvolvido internamente |
| Situação | str | Em Produção |
| Nível de Medição | str | Detalhada (IFPUG) |
| Tamanho Funcional (PF) | float64 | 181.7 |
| Preço PF (R$) | float64 | 707.64 |
| Valor Bruto VT (R$) | float64 | 128578.188 |
| Valor Institucional | float64 | 0.5 |
| Valor Final VA (R$) | float64 | 192867.282 |
| Fonte | str | Dados.xlsx (inventário 2024) |

## fCustoProjeto

Componentes do custo de projeto pago à fábrica de software (laudos com custo de projeto).

| Coluna | Tipo | Exemplo |
|---|---|---|
| ID Produto | str | SISPAT |
| Componente | str | Desenvolvimento - projeto principal (Imobiliário) |
| Tipo de Custo | str | Construção |
| Valor (R$) | float64 | 3114672.8 |

## fEconomicidade

Economicidade por sistema: custo pago, mesmo serviço a preço de mercado do PF, economia e retorno por R$ 1,00.

| Coluna | Tipo | Exemplo |
|---|---|---|
| ID Produto | str | SISPAT |
| Período | str | Acumulado até 07/2026 |
| PF Faturado | float64 | 14222.6 |
| Preço PF Contrato (R$) | float64 | 544.53 |
| Nota Preço Contrato | str | R$ 457,00 em 2022; R$ 519,99 em 05/2025; R$ 544,53 no 5º Termo de Apos |
| Custo Total Pago (R$) | float64 | 3744728.3 |
| Custo de Construção (R$) | float64 | 3626950.38 |
| Custo Médio por PF Faturado (R$) | float64 | 263.29421484116824 |
| PF Equivalentes Pagos | float64 | 6876.991717628046 |
| Preço PF Mercado 2026 (R$) | float64 | 1215.09 |
| Custo do Volume a Preço de Mercado (R$) | float64 | 8356163.866172662 |
| Economia vs Mercado (R$) | float64 | 4611435.566172662 |
| % Economia | float64 | 0.5518603560230106 |
| PF Medido 2026 | float64 | 5375.0 |
| VT 2026 (R$) | float64 | 6531108.75 |
| VA 2026 (R$) | float64 | 13062217.5 |
| Retorno VT por R$ 1 | float64 | 1.7440808055420203 |
| Retorno VA por R$ 1 | float64 | 3.4881616110840405 |
| Fator Grupo Contratado | float64 | 0.75 |
| Fonte | str | painel Custos de Projetos - Fábrica de Software, base: TRDs até 07/202 |

## fFuncao

Quantidade de funções e pontos de função por tipo, conforme o resultado de cada laudo.

| Coluna | Tipo | Exemplo |
|---|---|---|
| ID Produto | str | SISPAT |
| Tipo de Função | str | ALI |
| Qtde Funções | int64 | 80 |
| Tamanho Funcional (PF) | float64 | 655.8 |

## fHistoricoLaudo

Histórico de medições registrado em cada laudo.

| Coluna | Tipo | Exemplo |
|---|---|---|
| ID Produto | str | SISPAT |
| Ano Inventário | int64 | 2023 |
| Data da Medição | str | 10/08/2023 |
| Tamanho Funcional (PF) | float64 | 1850.0 |
| Nível de Medição | str | Detalhada (IFPUG) |
| Situação | str | Em homologação |
| Observação | str | VI 0,25 |

## fIntegracao

Integrações declaradas em cada laudo.

| Coluna | Tipo | Exemplo |
|---|---|---|
| ID Produto | str | SISPAT |
| Sistema Integrado | str | FIPLAN (Sistema Integrado de Planejamento, Contabilidade e Finanças) |
| Dados Trocados | str | Contas contábeis e de depreciação (FIP62), unidade orçamentária, eleme |
| Forma | str | Arquivos de Interface Externa (AIE) |

## fModulo

Pontos de função por módulo, conforme o resultado de cada laudo.

| Coluna | Tipo | Exemplo |
|---|---|---|
| ID Produto | str | SISPAT |
| Módulo | str | Imobiliário: cadastro, documentação e avaliação |
| Tamanho Funcional (PF) | float64 | 779.6 |
| Qtde Histórias | float64 | 19.0 |
