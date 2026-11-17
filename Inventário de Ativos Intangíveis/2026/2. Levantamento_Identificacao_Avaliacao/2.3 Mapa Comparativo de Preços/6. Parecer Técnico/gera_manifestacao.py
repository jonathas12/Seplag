"""Gera a Manifestação Técnica da pesquisa de preços do ponto de função (HTML, PDF e DOCX) no modelo institucional.

Lê os resultados do notebook (5. Análise Estatística), a configuração (config_pesquisa.json), o mapa de preços
(4. Mapa Comparativo) e a conferência com o PNCP (3. Evidências). Os números do texto vêm desses arquivos.

Uso, a partir desta pasta:  python gera_manifestacao.py
"""
import csv, datetime, json, sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
sys.path.insert(0, str(RAIZ.parents[1] / '_Modelo_Institucional'))
from documento_seplag import Documento  # noqa: E402

CFG = json.loads((RAIZ / 'config_pesquisa.json').read_text(encoding='utf-8'))
R = json.loads((RAIZ / '5. Análise Estatística' / 'resultados_analise.json').read_text(encoding='utf-8'))
GRAF = RAIZ / '5. Análise Estatística' / 'graficos'
MAPA = [r for r in csv.DictReader(open(RAIZ / '4. Mapa Comparativo' / 'Precos_Ponto_Funcao_2025-2026.csv', encoding='utf-8-sig'), delimiter=';')]
A = [r for r in MAPA if r['classificacao'].startswith('AMOSTRA A')]
RESUMO_PNCP = RAIZ / '3. Evidências' / 'Documentos PNCP' / '_resumo_coleta.json'
CONF = json.loads(RESUMO_PNCP.read_text(encoding='utf-8'))['referencias'] if RESUMO_PNCP.exists() else []


def brl(v, casas=2):
    s = f'{float(v):,.{casas}f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
    return f'R$ {s}'


def pct(v, casas=1, sinal=False):
    s = f'{v:+.{casas}f}' if sinal else f'{v:.{casas}f}'
    return s.replace('.', ',') + '%'


APELIDO = {1: 'Casa da Moeda', 2: 'SESED-RN', 3: 'Marinha', 4: 'UFCA', 5: 'MP-PA', 6: 'INCRA/Serpro', 7: 'TJ-PA', 8: 'MDS', 9: 'SMED Salvador'}
ct = CFG['contrato_referencia']
C, C0 = ct['preco_vigente_pf'], ct['preco_original_pf']
P25 = CFG['inventario_2025']['preco_pf_adotado']
BASE = R['data_base_ipca']
D = R['descritiva']
DO, DA = D['Preço original'], D['Preço atualizado']
KO, KA = R['kmeans_2026_original'], R['kmeans_2026_atualizado']
am = sorted(R['amostra_2026'], key=lambda x: x['Ref'])
out = R['outlier_refs']
mes_ct = ct.get('mes_base_preco_vigente')

d = Documento('MANIFESTAÇÃO TÉCNICA',
              ['Pesquisa e Análise de Preços do Ponto de Função', 'Inventário de Bens Intangíveis - Exercício 2026',
               'Portaria nº 124/2026/SEPLAG | IN Conjunta nº 003/2022/SEPLAG/SEFAZ'],
              nome_arquivo='MANIFESTACAO_TECNICA_Preco_Ponto-Funcao_2026',
              setor='Coordenadoria de Planejamento e Projetos de TI (CPPTI/SEPLAG) | Comissão de Inventário e Avaliação de Bens Intangíveis',
              cidade_data=f"Cuiabá/MT, {datetime.date.fromisoformat(CFG['data_pesquisa']).strftime('%d/%m/%Y')}.")

d.p('A presente **Manifestação Técnica** reúne a pesquisa, o tratamento e a análise estatística de preços de mercado do **ponto de função (PF)**, '
    'insumo do valor dos softwares desenvolvidos internamente no Inventário de Bens Intangíveis de 2026 da SEPLAG/MT '
    '(IN Conjunta nº 003/2022/SEPLAG/SEFAZ, art. 11, § 3º: valor de mercado da FPA no momento da avaliação).')
d.p('O ponto de partida é o **Contrato nº 014/2022/SEPLAG**, que define o objeto, a unidade de medida e a tecnologia que os preços pesquisados devem ter '
    'para serem comparáveis. A partir dele, os preços foram coletados em fonte oficial, conferidos no PNCP, atualizados pelo IPCA e agrupados por '
    'algoritmo de ciência de dados (K-Means).')
d.cards([('Preços Java em PF coletados', str(len(am)), 'compras de 2025 e 2026'),
         ('Contrato 014/2022/SEPLAG', brl(C), f"{ct['ato_vigente']}"),
         ('Mediana dos preços originais', brl(DO['Mediana']), 'sem atualização'),
         ('Mediana dos preços atualizados', brl(DA['Mediana']), f'IPCA até {BASE}')])
d.caixa('info', 'Natureza deste documento:',
        'Esta manifestação **não indica o preço de referência**. Ela entrega os grupos de preços formados pelo algoritmo, as evidências de cada preço e as limitações da amostra. '
        'A escolha do grupo ou do preço, inclusive a de manter, excluir ou adotar um valor fora da curva, é decisão da presidência da comissão, a ser motivada no Relatório Final.')

# ---------------------------------------------------------------- 1
d.secao('📑', '1. Objeto de referência: Contrato nº 014/2022/SEPLAG')
d.p('O Contrato nº 014/2022/SEPLAG, firmado com a **KRP Consultoria em Tecnologia de Informação Ltda**, decorre da adesão à **Ata de Registro de Preços nº 033/2021** '
    'da Procuradoria-Geral de Justiça do Tocantins, gerada pelo **Pregão Eletrônico nº 015/2021**. Tem por objeto o serviço técnico especializado, continuado, '
    'na modalidade de fábrica de software para sustentação, manutenção, desenvolvimento e melhorias dos sistemas de informação da SEPLAG. '
    'Os documentos estão na pasta `1. Objeto de Referência`.')
d.subsecao('1.1. Por que o contrato é homogêneo aos softwares inventariados')
d.tabela(['Critério de homogeneidade', 'O que o Contrato 014/2022 e seu edital estabelecem', 'Correspondência com os softwares da SEPLAG'],
         [['Origem do preço', 'Pregão eletrônico com registro de preços (PE 015/2021, ARP 033/2021), aderido pela SEPLAG (Contrato, cláusulas 1.2 e 2.1).',
           'Preço formado em disputa pública e praticado pela própria Administração contratante.'],
          ['Natureza do serviço', 'Fábrica de software para sustentação, manutenção, desenvolvimento e melhorias de sistemas (cláusula 1.1); atuação em todas as fases do ciclo de vida (TR, item 2.1).',
           'É o mesmo tipo de trabalho que gerou os sistemas inventariados: construção e evolução de software sob medida.'],
          ['Unidade de medida', 'Ponto de função (cláusula 7.1).', 'O inventário mede os softwares em ponto de função (IN 03/2022, art. 11).'],
          ['Método de contagem', 'Roteiro de Métricas do SISP 2.3 e Manual de Práticas de Contagem (CPM 4.3) do IFPUG; fator de ajuste 1,00; sem conversão de horas em PF (TR, itens 8.1 a 8.3).',
           'As medições do inventário seguem o IFPUG (ISO/IEC 20926), sem fator de ajuste. O PF do contrato e o PF do inventário são a mesma unidade.'],
          ['Tecnologia', 'Java, JavaScript, HTML, Python, PHP, PostgreSQL, Docker e Kubernetes (TR, tabela 2); perfil com conhecimento avançado em Java (TR, item 3).',
           'Java é a tecnologia de back-end padronizada e predominante nos sistemas da SITEC. A pesquisa usou os mesmos códigos de catálogo de Java.'],
          ['Código de catálogo', 'CatSer 25852 (Desenvolvimento de novo software - Java), informado no edital (TR, tabela 1).',
           'Mesmo código usado como filtro na coleta de 2026 (com o 25925, manutenção evolutiva em Java).'],
          ['Local e sistemas', 'Serviços prestados na Superintendência de TI da SEPLAG (cláusula 3.1), sobre os sistemas da SEPLAG.',
           'Os sistemas mantidos pelo contrato são os mesmos que compõem o inventário.'],
          ['Propriedade intelectual', 'A contratada cede os direitos de propriedade intelectual e autorais da solução (obrigações da contratada, item XV).',
           'Atende ao requisito de controle do ativo pelo Estado (IN 03/2022, art. 2º, § 1º).'],
          ['Preço vigente', f"{brl(C0)} em 05/2022; {brl(519.99)} no 4º apostilamento (05/2025); {brl(C)} no {ct['ato_vigente']} (processo {ct['processo_ato_vigente']}).",
           'Preço efetivamente pago hoje pela SEPLAG pelo ponto de função.']],
         legenda='Tabela 1 - Critérios de homogeneidade entre o Contrato 014/2022/SEPLAG e os softwares inventariados', larguras=[17, 45, 38])
d.caixa('conclusao', 'Conclusão sobre o objeto de referência:',
        'O contrato reúne, no mesmo instrumento, a unidade de medida, o método de contagem, a tecnologia e o tipo de serviço dos softwares avaliados, '
        'com preço formado em licitação e praticado pela própria SEPLAG. Por isso ele define o recorte da pesquisa: só entram preços de serviços '
        'de software em **Java**, medidos em **ponto de função**, em regime de **fábrica de software**.')
d.subsecao('1.2. Evolução do preço do contrato')
hist = ct['historico']
d.tabela(['Ato', 'Preço por PF', 'Referência', 'Variação sobre o ato anterior'],
         [[h['ato'], brl(h['preco_pf']), h['referencia'], '-' if i == 0 else pct((h['preco_pf'] / hist[i - 1]['preco_pf'] - 1) * 100, 2, True)] for i, h in enumerate(hist)],
         legenda='Tabela 2 - Preço do ponto de função no Contrato 014/2022/SEPLAG', numericas=[1, 3], larguras=[34, 18, 30, 18],
         fonte=f'Variação acumulada de {brl(C0)} para {brl(C)}: {pct((C / C0 - 1) * 100, 2, True)}. Reajuste contratual pelo IGP-M/FGV (cláusula 7.2).')
med_a, menor_a = DA['Mediana'], DA['Mínimo']
d.caixa('atencao', 'Ressalvas que acompanham a escolha do contrato:',
        f'**a)** A disputa de preço ocorreu em 2021, em licitação de outro ente; a SEPLAG aderiu à ata. '
        f'**b)** O preço vencedor ({brl(C0)}) ficou {pct((1 - C0 / 1252.60) * 100)} abaixo do valor estimado no edital para o serviço remoto ({brl(1252.60)}) '
        f'e {pct((1 - C0 / 1185.93) * 100)} abaixo do estimado para o presencial ({brl(1185.93)}). '
        f'**c)** O contrato é reajustado pelo IGP-M; a pesquisa atualiza os preços de mercado pelo IPCA. Os índices são diferentes. '
        f'**d)** O preço vigente ({brl(C)}) está abaixo dos {len(am)} preços de mercado atualizados: {pct((1 - C / menor_a) * 100)} abaixo do menor ({brl(menor_a)}) '
        f'e {pct((1 - C / med_a) * 100)} abaixo da mediana ({brl(med_a)}). '
        + ('**e)** O mês-base do 5º apostilamento não foi informado em `config_pesquisa.json`; o preço vigente foi usado sem correção pelo IPCA.' if not mes_ct else ''))

# ---------------------------------------------------------------- 2
d.secao('🔎', '2. Coleta e curadoria dos preços')
d.p('A coleta usou a API oficial de **Dados Abertos do Compras.gov.br** (preços praticados), nos 14 códigos de catálogo de desenvolvimento e manutenção de software '
    f"(grupo 111 do CatSer), com compras de {datetime.date.fromisoformat(CFG['periodo_compras']['inicio']):%d/%m/%Y} a {datetime.date.fromisoformat(CFG['periodo_compras']['fim']):%d/%m/%Y}. "
    'Fundamento: Decreto Estadual nº 1.525/2022 (contratações similares da Administração Pública e sistemas oficiais de governo).')
cont = {k: sum(1 for r in MAPA if r['classificacao'].startswith(k)) for k in ('AMOSTRA A', 'AMOSTRA B', 'DESCARTE')}
d.tabela(['Etapa', 'Registros', 'Critério'],
         [['Preços praticados nos 14 códigos', '683', 'Todas as unidades de medida'],
          ['Medidos em ponto de função', str(len(MAPA)), 'Unidade de medida "Ponto de Função"'],
          ['Descartados', str(cont['DESCARTE']), 'Menos de 100 PF, ou preço abaixo de R$ 100,00 ou acima de R$ 3.000,00 (unidade lançada para item de outra natureza)'],
          ['Outras linguagens', str(cont['AMOSTRA B']), 'PF em tecnologia diferente de Java: só para comparação'],
          ['Amostra: Java em ponto de função', str(cont['AMOSTRA A']), 'CatSer 25852 e 25925, mesmo recorte do Contrato 014/2022']],
         legenda='Tabela 3 - Funil da coleta', numericas=[1], larguras=[30, 10, 60])
if CONF:
    ok = sum(1 for c in CONF if c['preco_confere'])
    d.caixa('conclusao', 'Conferência no PNCP:',
            f'Os {len(CONF)} preços da amostra foram conferidos com o resultado homologado publicado no Portal Nacional de Contratações Públicas. '
            f'**{ok} de {len(CONF)}** coincidem ao centavo. Os documentos oficiais de cada compra (edital, atas, contratos) e as páginas em que o preço aparece estão em `3. Evidências/Documentos PNCP`.')
linhas = []
for x in am:
    r = next(m for m in A if int(m['id']) == x['Ref'])
    linhas.append([str(x['Ref']), x['Órgão'], x['Modalidade'], x['Data da compra'], brl(x['Preço original']),
                   x['Dentro de 13 meses'], x['Disputa de preço']])
d.tabela(['Ref.', 'Órgão comprador', 'Modalidade', 'Data da compra', 'Preço por PF', 'Até 13 meses', 'Disputa de preço'], linhas,
         legenda='Tabela 4 - Amostra: preços de serviços em Java medidos em ponto de função', numericas=[4], larguras=[6, 34, 18, 12, 12, 9, 9],
         fonte='Disputa de preço: "Sim" para pregão; "Não" para inexigibilidade ou dispensa. Links e números de controle do PNCP no Anexo I.')

# ---------------------------------------------------------------- 3
def tab_desc(cols):
    nomes = ['Quantidade', 'Mínimo', 'Primeiro quartil (Q1)', 'Mediana', 'Média', 'Terceiro quartil (Q3)', 'Máximo', 'Desvio padrão',
             'Coeficiente de variação', 'Limite superior IQR']
    linhas = []
    for n in nomes:
        lin = [n]
        for c in cols:
            v = D[c][n]
            lin.append(str(v) if n == 'Quantidade' else pct(v) if n == 'Coeficiente de variação' else brl(v))
        linhas.append(lin)
    return linhas

d.secao('📊', '3. Análise sem atualização monetária')
d.p('Os preços originais são os valores homologados na data de cada compra, sem correção. A tabela traz as medidas de posição e o teste de valores fora da curva '
    'pelo intervalo interquartil (IQR): é considerado outlier o preço acima de Q3 + 1,5 × IQR.')
d.tabela(['Medida', 'Preços originais', f'Preços atualizados até {BASE}'], tab_desc(['Preço original', 'Preço atualizado']),
         legenda='Tabela 5 - Estatística descritiva', numericas=[1, 2], larguras=[40, 30, 30])
d.figura(GRAF / 'G01_distribuicao_original_x_atualizado.png', 'Figura 1 - Quantidade de preços em cada faixa de R$ 250, sem e com atualização monetária')
d.figura(GRAF / 'G02_boxplot_original_x_atualizado.png', 'Figura 2 - Boxplot: a caixa reúne os 50% centrais dos preços; em vermelho, o preço acima do limite de outlier')
ref_out = ', '.join(f"Ref. {o} ({APELIDO[o]})" for o in out) or 'nenhuma'
d.caixa('info', 'Leitura:',
        f'A média ({brl(DO["Média"])}) fica {pct((DO["Média"] / DO["Mediana"] - 1) * 100)} acima da mediana ({brl(DO["Mediana"])}) porque um único preço é muito alto. '
        f'O teste IQR aponta como outlier: {ref_out}, contratação por dispensa, sem disputa de preço. A mediana não é afetada por esse valor; a média é.')

# ---------------------------------------------------------------- 4
d.secao('💹', '4. Atualização monetária pelo IPCA')
d.caixa('info', 'Como funciona a atualização:',
        '**1.** Para cada preço, identifica-se o mês da compra. **2.** Busca-se no Banco Central (série 433) a variação mensal do IPCA de cada mês, do mês da compra até o último mês publicado '
        f'({BASE}). **3.** Multiplicam-se os fatores mensais: Fator = (1 + IPCA₁/100) × (1 + IPCA₂/100) × ... × (1 + IPCAₙ/100). '
        '**4.** Preço atualizado = Preço original × Fator. O IPCA acumulado do período é (Fator − 1) × 100.',
        'Exemplo da Ref. 8: R$ 538,00 (fevereiro de 2026) × 1,037545 = R$ 558,20, isto é, IPCA acumulado de 3,75% entre 02/2026 e 10/2026. '
        'O método é o da ferramenta de atualização monetária usada em 2025 e inclui o IPCA do próprio mês da compra.')
d.tabela(['Ref.', 'Órgão', 'Preço original', 'Início da correção', 'Fim da correção', 'IPCA acumulado', 'Fator de correção', 'Preço atualizado', 'Diferença'],
         [[str(x['Ref']), APELIDO[x['Ref']], brl(x['Preço original']), x['Mês da compra'], x['Mês final'], pct(x['IPCA acumulado'], 2),
           f"{x['Fator IPCA']:.6f}".replace('.', ','), brl(x['Preço atualizado']), brl(x['Aumento (R$)'])] for x in am],
         legenda=f'Tabela 6 - Atualização de cada preço pelo IPCA até {BASE}', numericas=[2, 5, 6, 7, 8], larguras=[5, 15, 12, 10, 10, 10, 12, 13, 13])
d.figura(GRAF / 'G03_atualizacao_ipca_por_preco.png', 'Figura 3 - Cada preço antes (cinza) e depois (azul) da atualização, com o IPCA acumulado do período')

# ---------------------------------------------------------------- 5
d.secao('🧩', '5. Segmentação dos preços em grupos (K-Means)')
d.p('O algoritmo K-Means separa os preços em três grupos pela distância entre eles, sem interferência do analista. O valor que representa cada grupo é o **centroide** '
    '(média dos preços do grupo). Os grupos são numerados do mais barato (Grupo 1) ao mais caro (Grupo 3). Parâmetros iguais aos de 2025: 3 grupos, random_state 42, n_init 10. '
    'O algoritmo foi aplicado aos preços originais e aos atualizados, para mostrar se a correção monetária muda a composição dos grupos.')
lin = []
for nome, K in [('Originais', KO), (f'Atualizados até {BASE}', KA)]:
    for g in K['grupos']:
        lin.append([nome, g['Grupo'], str(g['Qtde de preços']), g['Preços do grupo'].replace('; ', '\n'), brl(g['Mínimo']), brl(g['Máximo']), brl(g['Centroide (média)'])])
d.tabela(['Preços', 'Grupo', 'Qtde', 'Preços que formam o grupo', 'Mínimo', 'Máximo', 'Centroide'],
         lin, legenda='Tabela 7 - Grupos formados pelo K-Means, com cada preço identificado', numericas=[2, 4, 5, 6], larguras=[12, 15, 6, 31, 12, 12, 12])
mud = [k for k in KO['atribuicao'] if KO['atribuicao'][k] != KA['atribuicao'][k]]
d.figura(GRAF / 'G04_kmeans_original_x_atualizado.png', 'Figura 4 - Cada preço com a cor do seu grupo; a linha preta é o centroide. A mesma referência ocupa a mesma linha nos dois painéis')
d.figura(GRAF / 'G05_centroides_original_x_atualizado.png', 'Figura 5 - Centroide de cada grupo antes e depois da atualização monetária')
d.caixa('info', 'Leitura:',
        ('A atualização monetária **não muda a composição dos grupos**: cada preço permanece no mesmo grupo. ' if not mud else
         f"A atualização monetária muda o grupo das referências {', '.join(mud)}. ")
        + f"Os centroides sobem entre {pct(min(a['Centroide (média)'] / o['Centroide (média)'] - 1 for a, o in zip(KA['grupos'], KO['grupos'])) * 100)} e "
        f"{pct(max(a['Centroide (média)'] / o['Centroide (média)'] - 1 for a, o in zip(KA['grupos'], KO['grupos'])) * 100)}, efeito apenas da inflação do período. "
        f"Índice de silhueta (separação entre os grupos, de -1 a 1): {KO['silhueta']:.2f} nos originais e {KA['silhueta']:.2f} nos atualizados.".replace('0.', '0,'))
d.figura(GRAF / 'G08_teia_precos_por_referencia.png', 'Figura 6 - Gráfico de teia: cada eixo é uma referência; no painel B, sem o preço apontado como outlier, a escala é ampliada')
d.caixa('atencao', 'Cuidado na leitura do gráfico de teia:',
        'A área desenhada depende da ordem dos eixos e o preço mais alto comprime os demais. O gráfico serve para visualizar a distância de cada preço às linhas do contrato e de 2025; '
        'a comparação entre preços deve ser feita pela Figura 4 e pela Tabela 7.')

# ---------------------------------------------------------------- 6
d.secao('🧪', '6. Sensibilidade dos grupos à composição da amostra')
d.p('Com poucos preços, a entrada ou a saída de um único valor pode mudar os grupos. A tabela repete o agrupamento em cinco recortes da amostra, '
    'nos preços originais e nos atualizados.')
desc_c = {'C1': 'Os 9 preços', 'C2': 'Sem o outlier do IQR', 'C3': 'Só preços com até 13 meses', 'C4': 'Só pregões (com disputa de preço)',
          'C5': '9 preços + Contrato 014/2022 (critério de 2025)'}
lin = []
for c in R['cenarios']:
    k = c['Cenário'][:2]
    lin.append([f"{k} - {desc_c[k]}", c['Base'], str(c['Qtde']), brl(c['Mediana geral']),
                f"{brl(c['G1 centroide'])} ({c['G1 qtde']})", f"{brl(c['G2 centroide'])} ({c['G2 qtde']})", f"{brl(c['G3 centroide'])} ({c['G3 qtde']})",
                f"{c['Silhueta']:.2f}".replace('.', ',')])
d.tabela(['Cenário', 'Preços', 'Qtde', 'Mediana', 'Grupo 1 (qtde)', 'Grupo 2 (qtde)', 'Grupo 3 (qtde)', 'Silhueta'], lin,
         legenda='Tabela 8 - Centroides dos grupos em cada cenário (entre parênteses, a quantidade de preços do grupo)', numericas=[2, 3, 4, 5, 6, 7],
         larguras=[25, 12, 5, 12, 13, 13, 13, 7])
c2a = next(c for c in R['cenarios'] if c['Cenário'].startswith('C2') and c['Base'] != 'Original')
d.caixa('info', 'Leitura:',
        f"O Grupo 1 é o mais estável entre os cenários. Sem o outlier (C2), a amostra se divide em três grupos de 3, 3 e 2 preços, com a melhor separação (silhueta {str(round(c2a['Silhueta'], 2)).replace('.', ',')}); "
        f"nos demais cenários há grupos com um ou dois preços. A mediana geral varia pouco entre os cenários ({brl(min(c['Mediana geral'] for c in R['cenarios']))} a "
        f"{brl(max(c['Mediana geral'] for c in R['cenarios']))}).")

# ---------------------------------------------------------------- 7
d.secao('📅', '7. Comparação com o inventário de 2025')
d.p('Em 2025 foram usados 13 preços, atualizados pelo IPCA até 10/2025, e adotada a média do Grupo 2 do K-Means (**R$ 943,25**). '
    'Recalculado aqui com o mesmo algoritmo e os mesmos parâmetros, o agrupamento de 2025 **reproduz exatamente** os centroides publicados (R$ 633,92, R$ 943,25 e R$ 1.174,50). '
    'Para comparar valores de datas diferentes, os preços de 2025 também foram trazidos até ' + BASE + ' pelo IPCA de 11/2025 em diante '
    f"(fator {R['fator_ipca_2025_para_base']:.6f}".replace('.', ',') + ').')
p25 = R['amostra_2025']
d.tabela(['Nº', 'Fonte usada em 2025', 'Órgão', 'Original', 'Atualizado até 10/2025', f'Atualizado até {BASE}'],
         [[str(x['Ref']), x['Fonte'], x['Órgão'], brl(x['Preço original']), brl(x['Atualizado até 10/2025']), brl(x[f'Atualizado até {BASE}'])] for x in p25],
         legenda='Tabela 9 - Os 13 preços do inventário de 2025', numericas=[3, 4, 5], larguras=[5, 40, 19, 12, 12, 12],
         fonte='Fonte: Comparativo de Preços - FSW (pasta de 2025).')
lin = []
for c in R['comparacao_2025_2026']:
    lin.append([c['Grupo'], brl(c['2025 original']), brl(c['2026 original']), pct(c['Variação original (2026 / 2025)'], 1, True),
                brl(c[f'2025 atualizado até {BASE}']), brl(c[f'2026 atualizado até {BASE}']), pct(c[f'Variação real, mesma data-base {BASE}'], 1, True)])
d.tabela(['Grupo', '2025 original', '2026 original', 'Variação', f'2025 em {BASE}', f'2026 em {BASE}', 'Variação real'], lin,
         legenda='Tabela 10 - Centroides de 2025 e de 2026, sem atualização e na mesma data-base', numericas=[1, 2, 3, 4, 5, 6], larguras=[22, 13, 13, 10, 14, 14, 14])
d.figura(GRAF / 'G06_precos_2025_x_2026.png', 'Figura 7 - Todos os preços de 2025 e de 2026 na mesma régua, coloridos pelo grupo; o traço é o centroide')
d.figura(GRAF / 'G07_centroides_2025_x_2026.png', 'Figura 8 - Centroides de 2025 e de 2026: preços originais e mesma data-base')
g1 = R['comparacao_2025_2026'][0]
d.caixa('atencao', 'Como interpretar as variações:',
        f"**Grupo 1:** é comparável entre os anos (7 preços em 2025 e 6 em 2026) e variou {pct(g1[f'Variação real, mesma data-base {BASE}'], 1, True)} na mesma data-base. "
        '**Grupos 2 e 3:** mudaram de composição. Em 2025 o Grupo 2 tinha 4 preços entre R$ 886,51 e R$ 943,26, vindos da família da ARP 33/2024 do MGI; '
        'em 2026 não há preço nessa faixa, e os Grupos 2 e 3 têm 2 e 1 preço. As variações desses grupos refletem a mudança da amostra, **não uma alta de preços de mercado**.')
d.caixa('info', 'Fontes que aparecem nos dois anos:',
        '**Marinha (PE 90002/2025):** R$ 1.060,00 nos dois anos (2025: Banco de Preços, menor preço; 2026: Ref. 3). '
        '**Casa da Moeda (PE 90061/2024):** em 2025 entrou R$ 1.182,00, que era a média saneada das propostas finais calculada pelo Banco de Preços; '
        'em 2026 entra R$ 555,00, o preço unitário homologado do item 1, conferido no PNCP (Ref. 1).')

# ---------------------------------------------------------------- 8
d.secao('⚖️', '8. Resultados para a decisão')
d.subsecao('8.1. Fatos verificados')
fatos = [f'O teste IQR aponta {ref_out} como outlier, nos preços originais e nos atualizados.',
         f"Nos preços atualizados, o Grupo 1 reúne {KA['grupos'][0]['Qtde de preços']} dos 9 preços, com centroide de {brl(KA['grupos'][0]['Centroide (média)'])}.",
         f'O Contrato 014/2022/SEPLAG ({brl(C)}) fica abaixo dos 9 preços atualizados.',
         f'O preço adotado em 2025 ({brl(P25)}) fica acima de {sum(1 for x in am if x["Preço atualizado"] < P25)} e abaixo de {sum(1 for x in am if x["Preço atualizado"] > P25)} dos 9 preços atualizados.',
         f"Quatro das nove referências são contratações diretas, sem disputa de preço (Ref. {', '.join(str(x['Ref']) for x in am if x['Disputa de preço'] == 'Não')}).",
         f"Três referências têm mais de 13 meses na data da pesquisa (Ref. {', '.join(str(x['Ref']) for x in am if x['Dentro de 13 meses'] == 'Não')}).",
         'Nenhum dos 13 preços de 2025 atende à janela de 13 meses; o preço da Marinha já integra a amostra de 2026.']
d.lista(fatos)
d.subsecao('8.2. Limitações que afetam a robustez')
d.lista(['A amostra tem 9 preços. Com esse tamanho, os grupos mudam com a entrada ou a saída de um único preço, e há grupos com um ou dois preços.',
         'O índice de silhueta mede a separação entre os grupos, não a qualidade do preço.',
         'Os contratos de fábrica de software diferem em escopo, níveis de serviço e exigência de perfis, o que explica parte da dispersão e não é corrigido pela análise.',
         'O preço do contrato é reajustado pelo IGP-M; os preços de mercado foram atualizados pelo IPCA.'])
d.subsecao('8.3. Ordem de grandeza do efeito sobre o inventário')
inv = CFG['inventario_2025']
cands = [(KA['grupos'][0]['Centroide (média)'], f'Grupo 1, 9 preços atualizados'), (c2a['G1 centroide'], 'Grupo 1, sem o outlier'),
         (c2a['G2 centroide'], 'Grupo 2, sem o outlier'), (DA['Mediana'], 'Mediana dos 9 preços atualizados'), (C, 'Contrato 014/2022/SEPLAG'),
         (P25, 'Preço adotado em 2025'), (KA['grupos'][1]['Centroide (média)'], 'Grupo 2, 9 preços atualizados'), (KA['grupos'][2]['Centroide (média)'], 'Grupo 3, 9 preços atualizados')]
cands = sorted(set(cands))
d.tabela(['Preço por PF', 'Origem do valor', 'Valor estimado do grupo de softwares', 'Variação sobre 2025'],
         [[brl(v), o, brl(inv['valor_grupo_desenvolvidos_internamente'] * v / P25), pct((v / P25 - 1) * 100, 1, True)] for v, o in cands],
         legenda='Tabela 11 - Efeito do preço escolhido sobre o valor dos softwares desenvolvidos internamente', numericas=[0, 2, 3], larguras=[16, 38, 28, 18],
         fonte=f"Estimativa com o tamanho funcional ({inv['tamanho_funcional_pf']:,.0f} PF".replace(',', '.') + ') e os valores institucionais de 2025, quando o grupo valia '
               f"{brl(inv['valor_grupo_desenvolvidos_internamente'])} ao preço de {brl(P25)}. Deve ser recalculada com as medições de 2026.")
d.caixa('conclusao', 'Valor de referência do ponto de função para 2026:',
        'A definir pela presidência da Comissão de Inventário e Avaliação de Bens Intangíveis no Relatório Final, com base nos grupos, nas evidências e nas limitações apresentados nesta manifestação.')

# ---------------------------------------------------------------- anexos
d.quebra()
d.secao('📎', 'Anexo I - Rastreabilidade de cada preço')
d.tabela(['Ref.', 'Órgão / processo', 'Nº de controle PNCP', 'Compra e item', 'Preço por PF', 'Link no PNCP'],
         [[r['id'], f"{r['uasg_nome'].title()}\nProcesso {r['processo']}", r['numero_controle_pncp'], f"{r['id_compra']} / item {r['item']}",
           brl(r['preco_unitario_pf']), f"[abrir]({r['link_pncp']})"] for r in A],
         legenda='Tabela 12 - Origem de cada preço da amostra', numericas=[4], larguras=[5, 33, 22, 20, 11, 9],
         fonte='A planilha `Mapa_Comparativo_Precos_PF_2026.xlsx` traz também o link do Compras.gov.br e da API de cada registro. '
               'A ficha e os documentos oficiais de cada preço estão em `3. Evidências`.')
d.secao('📎', 'Anexo II - Reprodução da análise')
d.p('Toda a análise é reproduzível em qualquer computador. Na pasta `2026`, executar `configurar_ambiente` (cria o ambiente Python e instala as bibliotecas) e, em seguida, '
    '`python executar.py --tudo`. O notebook `5. Análise Estatística/Analise_Precos_PF-2026.ipynb` refaz todas as tabelas e gráficos a partir de '
    '`4. Mapa Comparativo/Precos_Ponto_Funcao_2025-2026.csv`. Instruções no documento Como Executar o Projeto (`COMO_EXECUTAR.pdf`).', alinhar='left')
d.assinatura('Elaboração:', 'Jonathas G. Marques', 'Gerente de projetos e cientista de dados (CPPTI/SITEC/SAAS/SEPLAG)', 'Presidente da Comissão de Inventário (Portaria nº 124/2026/SEPLAG)', 'Matrícula: 280193')

if __name__ == '__main__':
    saidas = d.salvar(AQUI / 'MANIFESTACAO_TECNICA_Preco_Ponto-Funcao_2026')
    print('Gerados:', *[s.name for s in saidas])
