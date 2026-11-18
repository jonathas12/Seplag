"""Laudo Técnico de Avaliação de software medido por pontos de função (IN Conjunta nº 003/2022/SEPLAG/SEFAZ).

Lê a planilha de contagem (abas Contagem e Funções), agrupa as funções por módulo, gera os gráficos e
monta o laudo no modelo institucional (HTML, PDF e Word), a partir de um arquivo de configuração por sistema.

Uso (na pasta 2026):
    python _Modelo_Institucional/laudo_apf.py "4. Relatório Final/Laudos Técnicos de Avaliação/14. SICC/laudo_SICC.json"

O valor segue o art. 11 da IN: VA = VT + (VT x VI), com VT = tamanho em PF x preço do PF.
"""
import collections
import json
import re
import sys
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import openpyxl

sys.path.insert(0, str(Path(__file__).parent))
from documento_seplag import Documento  # noqa: E402

AZUL, CINZA, TINTA = '#0b3d91', '#8A94A3', '#1f2937'
PF_PADRAO = {  # IFPUG: (tipo, complexidade) -> PF; usado só se a planilha não tiver valores calculados
    ('ALI', 'Baixa'): 7, ('ALI', 'Média'): 10, ('ALI', 'Alta'): 15,
    ('AIE', 'Baixa'): 5, ('AIE', 'Média'): 7, ('AIE', 'Alta'): 10,
    ('EE', 'Baixa'): 3, ('EE', 'Média'): 4, ('EE', 'Alta'): 6,
    ('CE', 'Baixa'): 3, ('CE', 'Média'): 4, ('CE', 'Alta'): 6,
    ('SE', 'Baixa'): 4, ('SE', 'Média'): 5, ('SE', 'Alta'): 7}
NOME_TIPO = {'ALI': 'Arquivo Lógico Interno (ALI)', 'AIE': 'Arquivo de Interface Externa (AIE)',
             'EE': 'Entrada Externa (EE)', 'CE': 'Consulta Externa (CE)', 'SE': 'Saída Externa (SE)'}
VI_TABELA = [('Imprescindível', 'Na hipótese de inoperância, provocará prejuízo de altíssimo impacto', 1.0),
             ('Muito importante', 'Na hipótese de inoperância, provocará prejuízo de alto impacto', 0.75),
             ('Importante', 'Na hipótese de inoperância, provocará prejuízo de médio impacto', 0.50),
             ('Relativa importância', 'Na hipótese de inoperância, provocará prejuízo de baixo impacto', 0.25)]


def brl(v):
    return 'R$\u00a0' + f'{v:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')


def num(v, casas=0):
    return f'{v:,.{casas}f}'.replace(',', 'X').replace('.', ',').replace('X', '.')


def pct(v):
    return num(v * 100, 1) + '%'


def codigo_us(texto):
    m = re.search(r'US-?0*(\d{2,4})', texto or '')
    return int(m.group(1)) if m else None


# ---------------------------------------------------------------- leitura da planilha
def ler_baseline(caminho):
    wb = openpyxl.load_workbook(caminho, data_only=True)
    c, f = wb['Contagem'], wb['Funções']
    cab = {'empresa': c['F4'].value, 'aplicacao': c['F5'].value, 'tipo': c['F6'].value, 'nivel': c['F7'].value,
           'projeto': c['F8'].value, 'responsavel': c['F9'].value, 'revisor': c['F10'].value,
           'tecnologia': c['R7'].value, 'guia': c['R8'].value, 'criacao': c['R9'].value, 'revisao': c['R10'].value,
           'proposito': c['A12'].value, 'escopo': c['A17'].value, 'documentacao': c['A22'].value,
           'pf_planilha': f['L4'].value}
    funcoes, grupo = [], None
    for r in range(8, f.max_row + 1):
        nome, tipo = f.cell(r, 1).value, f.cell(r, 2).value
        if nome and not tipo:
            grupo = str(nome).strip()
            continue
        if not tipo:
            continue
        complexidade = f.cell(r, 6).value
        pf = f.cell(r, 8).value
        if pf in (None, ''):
            pf = PF_PADRAO[(tipo, complexidade)]
        funcoes.append({'linha': r, 'grupo': grupo, 'funcao': str(nome).strip(), 'tipo': tipo,
                        'manutencao': f.cell(r, 3).value, 'complexidade': complexidade, 'pf': float(pf),
                        'obs': f.cell(r, 15).value})
    return cab, funcoes


def atribuir_modulos(funcoes, cfg):
    por_us = {n: m for m, lista in cfg['modulos'].items() for n in lista}
    for fn in funcoes:
        us = codigo_us(fn['funcao']) or codigo_us(fn['grupo'])
        fn['us'] = us
        fn['modulo'] = por_us.get(us) or cfg.get('grupos_sem_historia', {}).get(fn['grupo'], 'Outros')
    return funcoes


# ---------------------------------------------------------------- gráficos
def _estilo():
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9.5, 'axes.edgecolor': '#d9e1ec',
                         'axes.labelcolor': TINTA, 'xtick.color': TINTA, 'ytick.color': TINTA,
                         'axes.spines.top': False, 'axes.spines.right': False, 'text.parse_math': False})


def grafico_barras_h(rotulos, valores, titulo, arquivo, sufixo=' PF'):
    _estilo()
    pares = sorted(zip(rotulos, valores), key=lambda x: x[1])
    fig, ax = plt.subplots(figsize=(8.6, 0.42 * len(pares) + 1.1))
    ax.barh([p[0] for p in pares], [p[1] for p in pares], color=AZUL, height=0.62)
    total = sum(valores)
    for i, (_, v) in enumerate(pares):
        ax.text(v + total * 0.006, i, f'{num(v)}{sufixo} ({pct(v / total)})', va='center', fontsize=8.8, color=TINTA)
    ax.set_xlim(0, max(valores) * 1.28)
    ax.xaxis.set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.tick_params(axis='y', length=0)
    ax.set_title(titulo, loc='left', fontweight='bold', color=TINTA, fontsize=10.5)
    fig.tight_layout()
    fig.savefig(arquivo, dpi=200)
    plt.close(fig)


def grafico_evolucao(historico, arquivo, titulo):
    _estilo()
    fig, ax = plt.subplots(figsize=(8.6, 3.2))
    rot = [f"v{h['versao']}\n{h['data']}" for h in historico]
    val = [h['pf'] for h in historico]
    ax.bar(rot, val, color=[CINZA] * (len(val) - 1) + [AZUL], width=0.5)
    for i, v in enumerate(val):
        ax.text(i, v + max(val) * 0.02, f'{num(v)} PF', ha='center', fontsize=9, color=TINTA, fontweight='bold')
    ax.set_ylim(0, max(val) * 1.18)
    ax.yaxis.set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.tick_params(axis='x', length=0)
    ax.set_title(titulo, loc='left', fontweight='bold', color=TINTA, fontsize=10.5)
    fig.tight_layout()
    fig.savefig(arquivo, dpi=200)
    plt.close(fig)


# ---------------------------------------------------------------- laudo
def gerar(caminho_cfg):
    caminho_cfg = Path(caminho_cfg).resolve()
    pasta = caminho_cfg.parent
    cfg = json.loads(caminho_cfg.read_text(encoding='utf-8'))
    cab, funcoes = ler_baseline(pasta / cfg['baseline'])
    atribuir_modulos(funcoes, cfg)
    graf = pasta / 'graficos'
    graf.mkdir(exist_ok=True)

    sig, nome = cfg['sigla'], cfg['nome']
    pf_total = sum(f['pf'] for f in funcoes)
    if cab['pf_planilha'] not in (None, '') and abs(float(cab['pf_planilha']) - pf_total) > 0.01:
        raise SystemExit(f'Soma das funções ({pf_total}) difere do total da planilha ({cab["pf_planilha"]}).')
    preco, vi = cfg['preco_pf'], cfg['vi']
    vt = round(pf_total * preco, 2)
    va = round(vt + vt * vi, 2)
    rotulo_vi = next(r for r, _, i in VI_TABELA if abs(i - vi) < 1e-9)
    docs = cfg['documentos']
    n_aprov = sum(1 for x in docs if x.get('aprovacao'))
    sem_aprov = [x['codigo'] for x in docs if not x.get('aprovacao')]
    txt_aprov = (f'{n_aprov} das {len(docs)} histórias de usuário têm aprovação datada pelas áreas de negócio'
                 if sem_aprov else f'As {len(docs)} histórias de usuário têm aprovação datada pelas áreas de negócio')

    por_tipo = collections.OrderedDict((t, [0, 0.0]) for t in ['ALI', 'AIE', 'EE', 'CE', 'SE'])
    for f in funcoes:
        por_tipo[f['tipo']][0] += 1
        por_tipo[f['tipo']][1] += f['pf']
    por_tipo = {k: v for k, v in por_tipo.items() if v[0]}
    por_mod = collections.OrderedDict()
    for m in list(cfg['modulos']) + ['Outros']:
        itens = [f for f in funcoes if f['modulo'] == m]
        if itens:
            por_mod[m] = itens
    dados_pf = sum(v[1] for k, v in por_tipo.items() if k in ('ALI', 'AIE'))

    grafico_barras_h([NOME_TIPO[t] for t in por_tipo], [v[1] for v in por_tipo.values()],
                     f'Tamanho funcional do {sig} por tipo de função', graf / 'G1_pf_por_tipo.png')
    grafico_barras_h(list(por_mod), [sum(f['pf'] for f in v) for v in por_mod.values()],
                     f'Tamanho funcional do {sig} por módulo', graf / 'G2_pf_por_modulo.png')
    grafico_evolucao(cfg['historico_medicoes'], graf / 'G3_evolucao_baseline.png',
                     f'Evolução do tamanho funcional do {sig} nas linhas de base')

    resp = cfg['responsavel']
    d = Documento(f'Laudo Técnico de Avaliação - {sig}',
                  [f'Inventário de Bens Intangíveis - Exercício {cfg["exercicio"]}', nome],
                  cfg['arquivo_saida'], setor='Comissão de Inventário e Avaliação de Bens Intangíveis (CIABI/SEPLAG)',
                  cidade_data=cfg['cidade_data'])
    d.cards([('Tamanho funcional', f'{num(pf_total)} PF', cfg['nivel_contagem']),
             ('Preço do ponto de função', brl(preco), 'data-base 10/2026'),
             ('Valor Institucional', num(vi, 2), rotulo_vi),
             ('Valor do ativo (VA)', brl(va), 'IN 03/2022, art. 11')])
    d.p(f'Este Laudo Técnico de Avaliação determina o valor do {nome} ({sig}), bem intangível da Secretaria de Estado '
        f'de Planejamento e Gestão de Mato Grosso, para fins de inventário e registro contábil do exercício de '
        f'{cfg["exercicio"]}, nos termos dos arts. 5º, VI, 11 e 20 da Instrução Normativa Conjunta nº 003/2022/SEPLAG/SEFAZ.')

    # 1. Identificação
    d.secao('📌', '1. Identificação do bem')
    d.tabela(['Item', 'Informação'], [
        ['Sigla e nome', f'{sig} - {nome}'],
        ['Tipo de bem', cfg['tipo_bem']],
        ['Situação', cfg['situacao']],
        ['Tecnologia predominante', cfg['tecnologia']],
        ['Desenvolvimento', cfg['unidade_desenvolvimento']],
        ['Áreas de negócio', cfg['areas_negocio']],
        ['Perfis de usuário', cfg['perfis']],
        ['Identificação contábil (IN, art. 20, II)', 'Ativo intangível, grupo Softwares (PCASP 1.2.4.1). Conta detalhada conforme a Instrução de Serviço nº 022/2020-SACE/SEFAZ, item 4.7, a confirmar pelo setor contábil'],
        ['Vida útil', cfg['vida_util']],
        ['Planilha de contagem', f'{cfg["baseline_nome"]} (revisão de {cab["revisao"]:%d/%m/%Y})'],
    ], legenda='Tabela 1 - Identificação do bem avaliado', larguras=[30, 70])

    # 2. Descrição
    d.secao('🧩', '2. Descrição detalhada do bem')
    for par in cfg['finalidade']:
        d.p(par)
    d.subsecao('2.1 Módulos e funcionalidades')
    linhas = []
    for m, itens in por_mod.items():
        uss = sorted({f['us'] for f in itens if f['us']})
        linhas.append([m, ', '.join(f'US{u:04d}' for u in uss) or 'Funções herdadas da linha de base anterior',
                       num(len(itens)), num(sum(f['pf'] for f in itens))])
    d.tabela(['Módulo', 'Histórias de usuário', 'Funções', 'PF'], linhas,
             legenda='Tabela 2 - Módulos do sistema, histórias de usuário e tamanho funcional', numericas=[2, 3],
             larguras=[30, 50, 10, 10])
    d.subsecao('2.2 Integrações e fronteira da aplicação')
    d.tabela(['Sistema ou serviço', 'Uso pelo ' + sig, 'Tratamento na contagem'], cfg['integracoes'],
             legenda='Tabela 3 - Sistemas com que o bem se relaciona', larguras=[28, 44, 28])

    # 3. Enquadramento
    d.secao('⚖️', '3. Reconhecimento como ativo intangível')
    d.p('Antes da mensuração, a comissão verificou se o bem atende aos critérios de reconhecimento da IN. O resultado está na Tabela 4.')
    d.tabela(['Critério', 'Base na IN', 'Verificação'], [
        ['Código-fonte de propriedade do Estado', 'art. 2º, § 1º', f'Software desenvolvido internamente pela SEPLAG/MT'],
        ['Em uso, sem obsolescência', 'art. 2º, § 2º, II', f'{cfg["situacao"]}, com histórias de usuário revisadas em {cfg["exercicio"]}'],
        ['Gerador de benefícios ou potencial de serviços', 'art. 6º, parágrafo único, I', 'Sustenta o ciclo das Certidões de Crédito e dos créditos salariais devidos pelo Estado'],
        ['Mensuração confiável', 'art. 6º, parágrafo único, II', f'Tamanho funcional de {num(pf_total)} PF medido por método normatizado (ISO/IEC 20926 e ISO/IEC 24570)'],
        ['Fase de desenvolvimento, não de pesquisa', 'arts. 8º e 9º', f'Funcionalidades especificadas e em produção. {txt_aprov}'],
        ['Documentação de custos insuficiente', 'art. 11', cfg['custo_incorrido']],
    ], legenda='Tabela 4 - Critérios de reconhecimento e enquadramento na metodologia do art. 11', larguras=[28, 20, 52])
    d.caixa('conclusao', 'Conclusão do reconhecimento:',
            f'O {sig} atende aos critérios de reconhecimento e é avaliado pela metodologia do art. 11 da IN, '
            'com base no tamanho funcional em pontos de função e no Valor Institucional.')

    # 4. Metodologia
    d.secao('🔎', '4. Metodologia de identificação, mensuração e avaliação')
    d.p('A avaliação seguiu as etapas do art. 5º da IN, detalhadas no fluxo abaixo. Cada etapa tem um registro que permite refazê-la.')
    d.tabela(['Etapa', 'O que foi feito', 'Registro'], [
        ['1. Levantamento', 'Inclusão do bem na relação de sistemas da SEPLAG para o exercício', 'Relação de sistemas (aba Avaliação 2026)'],
        ['2. Reconhecimento', 'Verificação dos critérios dos arts. 2º, 6º, 8º, 9º e 11 da IN', 'Tabela 4 deste laudo'],
        ['3. Análise documental', f'Leitura das {len(cfg["documentos"])} histórias de usuário: premissas, critérios de aceitação, regras de negócio, protótipos, histórico de versões e aprovações', 'Anexo I'],
        ['4. Mensuração do tamanho funcional', 'Contagem de pontos de função das funções de dados e de transação', f'{cfg["baseline_nome"]}, abas Contagem e Funções; Anexo II'],
        ['5. Preço do ponto de função', 'Pesquisa de preços em fontes oficiais, atualização monetária, análise de agrupamento e aprovação do preço pela comissão', cfg.get('registro_preco', 'Manifestação Técnica da pesquisa de preços de 2026')],
        ['6. Valor Institucional', 'Classificação do grau de importância do bem (art. 11, § 4º)', 'Seção 6 deste laudo'],
        ['7. Valor e vida útil', 'Cálculo VA = VT + (VT x VI) e classificação da vida útil', 'Seções 6 e 7 deste laudo'],
        ['8. Laudo', 'Consolidação neste documento (art. 20)', 'Este laudo'],
    ], legenda='Tabela 5 - Etapas da avaliação', larguras=[22, 50, 28])

    d.subsecao('4.1 Análise de Pontos de Função')
    d.p('A Análise de Pontos de Função (APF) mede o tamanho do software pelas funcionalidades que ele entrega ao usuário, '
        'independentemente da linguagem, da tecnologia ou de quem o desenvolveu. A medição segue o Manual de Práticas de '
        'Contagem do IFPUG (CPM 4.3.1), publicado como norma ISO/IEC 20926:2009, e o Roteiro de Métricas de Software do '
        f'SISP, versão {cfg.get("roteiro_sisp", "2.3")}, adotado no Contrato nº 014/2022/SEPLAG. Os níveis indicativo e estimativo seguem '
        'o método da NESMA (ISO/IEC 24570:2018).')
    d.tabela(['Tipo de função', 'O que representa', 'Exemplo no ' + sig], [
        ['Arquivo Lógico Interno (ALI)', 'Grupo de dados mantido pela aplicação', 'Amparo Legal, Crédito Salarial, Minuta de Certidão'],
        ['Arquivo de Interface Externa (AIE)', 'Grupo de dados de outra aplicação, apenas lido', 'Dados do SEAP; consulta de compensação na API da PGE'],
        ['Entrada Externa (EE)', 'Processo que recebe dados e altera um ALI', 'Solicitar estorno; salvar minuta'],
        ['Consulta Externa (CE)', 'Processo que apresenta dados sem cálculo', 'Listar e pesquisar; visualizar documento'],
        ['Saída Externa (SE)', 'Processo que apresenta dados com cálculo ou dado derivado', 'Cálculo do valor de desconto; gerar a certidão'],
    ], legenda='Tabela 6 - Tipos de função da APF', larguras=[26, 40, 34])
    d.p('A contagem percorre os passos do IFPUG: (1) definir o propósito da contagem; (2) definir o tipo de contagem '
        '(aplicação, projeto de desenvolvimento ou de melhoria); (3) definir o escopo e a fronteira da aplicação, '
        'separando o que é do sistema do que pertence a outros sistemas; (4) identificar as funções de dados (ALI e AIE); '
        '(5) identificar as funções de transação (EE, CE e SE) a partir dos processos elementares descritos na documentação; '
        '(6) classificar a complexidade de cada função; (7) somar as contribuições em pontos de função.')
    d.subsecao('4.2 Nível de detalhe da contagem')
    d.tabela(['Nível', 'Como é feito', 'Quando se usa'], [
        ['Indicativa (NESMA)', 'Considera só as funções de dados: 35 PF por ALI e 15 PF por AIE (IN, art. 11, § 2º)', 'Visão inicial, poucos requisitos conhecidos'],
        ['Estimativa (NESMA)', 'Identifica todas as funções de dados e de transação; atribui complexidade baixa às funções de dados e média às de transação', 'Funcionalidades conhecidas, sem detalhe de campos e registros'],
        ['Detalhada (IFPUG)', 'Identifica todas as funções e calcula a complexidade de cada uma por tipos de dados e registros', 'Especificação completa'],
    ], legenda='Tabela 7 - Níveis de detalhe da contagem', larguras=[20, 52, 28], destaque_linhas=[1])
    d.p(f'O {sig} foi medido no nível **{cfg["nivel_contagem"]}**. Nesse nível, cada ALI contribui com 7 PF, cada AIE com '
        '5 PF, cada EE e cada CE com 4 PF e cada SE com 5 PF.')

    d.subsecao('4.3 Preço do ponto de função')
    d.p('O preço foi obtido na pesquisa de preços do inventário de 2026, registrada na Manifestação Técnica da pesquisa de preços. '
        'A pesquisa seguiu estas etapas: (1) definição do objeto de referência, o Contrato nº 014/2022/SEPLAG; (2) coleta de '
        'preços de serviços de desenvolvimento em Java medidos em pontos de função, no Compras.gov.br e no PNCP; (3) conferência '
        'de cada preço com o resultado homologado e os documentos da contratação; (4) atualização monetária pelo IPCA até a '
        'data-base; (5) identificação de valores atípicos pelo intervalo interquartil; (6) agrupamento dos preços em faixas '
        'pelo algoritmo K-Means, técnica de aprendizado de máquina que reúne valores próximos e separa valores distantes, '
        'sem impor faixas definidas previamente; (7) escolha e fundamentação do preço pela comissão.')
    d.p(cfg['preco_fundamento'])
    d.subsecao('4.4 Valor Institucional')
    d.tabela(['Valor Institucional', 'Conceituação (IN, art. 11, § 4º)', 'Índice'],
             [[r, c, num(i, 2)] for r, c, i in VI_TABELA], legenda='Tabela 8 - Escala do Valor Institucional',
             numericas=[2], larguras=[24, 62, 14], destaque_linhas=[i for i, (_, _, x) in enumerate(VI_TABELA) if abs(x - vi) < 1e-9])
    d.subsecao('4.5 Fórmula de valor')
    d.caixa('info', 'IN Conjunta nº 003/2022/SEPLAG/SEFAZ, art. 11, §§ 1º e 3º:',
            '**VA = VT + (VT x VI)**, em que VA é o Valor do Ativo Intangível, VI é o Valor Institucional e VT é o Valor do '
            'tamanho do ativo, igual à quantidade de pontos de função multiplicada pelo valor de mercado do ponto de função '
            'apurado no momento da avaliação.')

    # 5. Mensuração
    d.secao('📊', '5. Mensuração do tamanho funcional')
    d.tabela(['Item', 'Definição na contagem'], [
        ['Propósito', 'Criar a linha de base do produto para planejamento, acompanhamento, estimativa de custos e avaliação do ativo'],
        ['Tipo de contagem', cab['tipo']],
        ['Nível de detalhe', cab['nivel']],
        ['Versão do manual', f'IFPUG CPM {cab["guia"]}'],
        ['Responsável e revisor', f'{cab["responsavel"]} / {cab["revisor"]}'],
        ['Criação e última revisão', f'{cab["criacao"]:%d/%m/%Y} e {cab["revisao"]:%d/%m/%Y}'],
        ['Fronteira', 'Aplicação ' + sig + '. Os dados de outros sistemas apenas lidos foram contados como AIE (Tabela 3)'],
        ['Documentação', f'{len(cfg["documentos"])} histórias de usuário (Anexo I)'],
    ], legenda='Tabela 9 - Parâmetros da contagem', larguras=[28, 72])
    d.p('O escopo da contagem registrado na planilha é o seguinte:')
    d.lista([re.sub(r'^\d+\s*-\s*', '', l).rstrip(';') for l in cab['escopo'].splitlines() if l.strip()])
    total_func = sum(v[0] for v in por_tipo.values())
    d.tabela(['Tipo de função', 'Quantidade', 'PF por função', 'Total de PF', '% do total'],
             [[NOME_TIPO[t], num(q), num(p / q), num(p), pct(p / pf_total)] for t, (q, p) in por_tipo.items()] +
             [['Total', num(total_func), '', num(pf_total), '100,0%']],
             legenda=f'Tabela 10 - Tamanho funcional do {sig} por tipo de função', numericas=[1, 2, 3, 4],
             larguras=[38, 14, 16, 16, 16], destaque_linhas=[len(por_tipo)])
    d.figura(graf / 'G1_pf_por_tipo.png', f'Figura 1 - Tamanho funcional do {sig} por tipo de função')
    d.p(f'As funções de dados somam {num(dados_pf)} PF ({pct(dados_pf / pf_total)}) e as de transação, '
        f'{num(pf_total - dados_pf)} PF ({pct(1 - dados_pf / pf_total)}). A predominância das transações reflete um sistema '
        'orientado a fluxos de trabalho: emissão, aprovação, assinatura, movimentação e quitação de certidões.')
    d.figura(graf / 'G2_pf_por_modulo.png', f'Figura 2 - Tamanho funcional do {sig} por módulo')
    d.subsecao('5.1 Evolução das linhas de base')
    h = cfg['historico_medicoes']
    d.tabela(['Versão', 'Data', 'Nível', 'PF', 'Uso'], [[x['versao'], x['data'], x['nivel'], num(x['pf']), x['uso']] for x in h],
             legenda='Tabela 11 - Linhas de base do ' + sig, numericas=[3], larguras=[10, 14, 24, 12, 40], destaque_linhas=[len(h) - 1])
    d.figura(graf / 'G3_evolucao_baseline.png', f'Figura 3 - Evolução do tamanho funcional do {sig}')
    ant = h[-2]['pf']
    d.p(f'O tamanho passou de {num(ant)} PF na versão {h[-2]["versao"]} para {num(pf_total)} PF na versão {h[-1]["versao"]} '
        f'(+{pct(pf_total / ant - 1)}). O acréscimo corresponde às funcionalidades descritas nas histórias de usuário '
        f'revisadas entre 2025 e {cfg["exercicio"]}, sobretudo emissão digital, desmembramento e cessão, estorno, quitações e '
        'perfis de acesso, que não existiam nas linhas de base anteriores.')

    # 6. Valor
    d.secao('🧮', '6. Determinação do valor')
    d.subsecao('6.1 Valor Institucional do ' + sig)
    for par in cfg['vi_justificativa']:
        d.p(par)
    d.subsecao('6.2 Cálculo')
    d.tabela(['Componente', 'Fórmula', 'Valor'], [
        ['Tamanho funcional', 'Planilha de contagem, aba Funções', f'{num(pf_total)} PF'],
        ['Preço do ponto de função', 'Manifestação Técnica da pesquisa de preços (data-base 10/2026)', brl(preco)],
        ['Valor do tamanho do ativo (VT)', f'{num(pf_total)} x {brl(preco)}', brl(vt)],
        ['Valor Institucional (VI)', f'{rotulo_vi} (art. 11, § 4º)', num(vi, 2)],
        ['Parcela institucional', f'VT x VI = {brl(vt)} x {num(vi, 2)}', brl(round(vt * vi, 2))],
        ['Valor do ativo (VA)', 'VT + (VT x VI)', brl(va)],
    ], legenda='Tabela 12 - Cálculo do valor do ativo', numericas=[2], larguras=[30, 46, 24], destaque_linhas=[5])
    a = cfg.get('avaliacao_anterior')
    if a:
        vt0 = round(a['pf'] * a['preco_pf'], 2)
        va0 = round(vt0 + vt0 * a['vi'], 2)
        d.subsecao('6.3 Comparação com o inventário de ' + str(a['exercicio']))
        d.tabela(['Componente', f'Inventário {a["exercicio"]}', f'Inventário {cfg["exercicio"]}', 'Variação'], [
            ['Situação', a['situacao'], cfg['situacao'], '-'],
            ['Tamanho funcional (PF)', num(a['pf']), num(pf_total), pct(pf_total / a['pf'] - 1)],
            ['Preço do PF', brl(a['preco_pf']), brl(preco), pct(preco / a['preco_pf'] - 1)],
            ['Valor Institucional', num(a['vi'], 2), num(vi, 2), '-'],
            ['Valor do tamanho (VT)', brl(vt0), brl(vt), pct(vt / vt0 - 1)],
            ['Valor do ativo (VA)', brl(va0), brl(va), pct(va / va0 - 1)],
        ], legenda=f'Tabela 13 - Comparação entre as avaliações de {a["exercicio"]} e {cfg["exercicio"]}', numericas=[1, 2, 3],
            larguras=[30, 24, 24, 22], destaque_linhas=[5])
        d.p(f'A variação decorre de três fatores, todos documentados: o aumento do tamanho funcional (Seção 5.1), o novo preço '
            f'do ponto de função apurado na pesquisa de {cfg["exercicio"]} e a reclassificação do Valor Institucional, '
            f'de {num(a["vi"], 2)} para {num(vi, 2)}, com a entrada do sistema em produção.')

    # 7. Vida útil
    d.secao('📅', '7. Vida útil')
    d.p(f'A vida útil do {sig} é classificada como **{cfg["vida_util"].lower()}** (IN, arts. 14 e 15). Pelos fatores do '
        'art. 14, § 1º: o uso é contínuo e previsto por tempo indeterminado; o sistema é mantido pela equipe interna e pode '
        'ser gerido por outra equipe, pois o código-fonte pertence ao Estado; não há contrato de licença ou cessão que limite '
        'o uso; a tecnologia (Java) segue suportada; e o sistema continua em evolução. Não há limite previsível para o período '
        'em que o bem fornecerá potencial de serviços.')
    d.p('Por isso o bem não é amortizado (art. 17) e deve passar anualmente pelo teste de redução ao valor recuperável (art. 18). '
        'A vida útil remanescente exigida pelo art. 20, IV, não se aplica, por se tratar de vida útil indefinida.')

    # 8. Ressalvas
    d.secao('⚠️', '8. Limitações e ressalvas')
    d.lista([
        f'A contagem no nível {cfg["nivel_contagem"]} usa complexidades padronizadas. Uma contagem detalhada pode resultar '
        'em tamanho diferente, para mais ou para menos.',
        'O tamanho refere-se às funcionalidades descritas na documentação e em produção na data da contagem. Ficam fora do escopo: '
        + ' '.join(cfg['fora_do_escopo']),
        cfg['custo_incorrido'],
        'O conteúdo e a qualidade das histórias de usuário são de responsabilidade da equipe do projeto que as elaborou.'
        + (f' {txt_aprov}; nas demais ({", ".join(sem_aprov)}), a seção de aprovação está sem preenchimento. '
           'As funcionalidades correspondentes foram consideradas por estarem em produção.' if sem_aprov else ''),
        'O preço do ponto de função é referência de mercado para fins de inventário e registro contábil (IN, art. 13); '
        'não se destina a contratação.',
    ] + ([cfg['ressalva_comissao']] if cfg.get('ressalva_comissao') else []))

    # 9. Conclusão
    d.secao('✅', '9. Conclusão')
    d.caixa('conclusao', f'Valor do {sig} para o inventário de {cfg["exercicio"]}:',
            f'Com tamanho funcional de **{num(pf_total)} pontos de função** ({cfg["nivel_contagem"]}), preço de **{brl(preco)}** '
            f'por ponto de função e Valor Institucional de **{num(vi, 2)} ({rotulo_vi})**, o valor do ativo intangível '
            f'{nome} ({sig}) é de **{brl(va)}**, com vida útil {cfg["vida_util"].lower()}.')
    d.p('A planilha de contagem e as histórias de usuário que fundamentam este laudo acompanham o processo do inventário '
        'para conferência.')
    d.p('É o laudo.')
    d.assinatura('Responsável pela mensuração (IN, art. 20, V)', resp['nome'],
                 f'{resp["cargo"]}', f'{resp["portaria"]} - matrícula {resp["matricula"]}', cfg['cidade_data'])

    # Anexos
    d.quebra()
    d.secao('📎', 'Anexo I - Documentação utilizada na análise')
    d.p(f'{cfg["documentacao_fonte"]} Planilha de contagem: {cfg["baseline_nome"]}.')
    mod_de = {n: m for m, l in cfg['modulos'].items() for n in l}
    d.tabela(['Código', 'História de usuário', 'Módulo', 'Versão', 'Data', 'Aprovação'],
             [[f'[{x["codigo"]}]({x["link"]})' if x.get('link') else x['codigo'], x['nome'], mod_de.get(int(x['codigo'][2:]), ''), x['versao'], x['data'],
               x.get('aprovacao') or 'sem registro'] for x in docs],
             legenda='Tabela A1 - Histórias de usuário: última versão do histórico de revisões e data da aprovação pelas áreas de negócio',
             larguras=[10, 32, 26, 8, 11, 13])
    d.secao('📎', 'Anexo II - Funções contadas')
    d.p(f'Relação das {total_func} funções da aba Funções da planilha {cfg["baseline_nome"]}, agrupadas por módulo.')
    for m, itens in por_mod.items():
        d.subsecao(f'{m} ({num(sum(f["pf"] for f in itens))} PF)')
        d.tabela(['Linha', 'Função', 'Tipo', 'Complex.', 'PF'],
                 [[str(f['linha']), f['funcao'] + (f' ({f["obs"]})' if f['obs'] else ''), f['tipo'], f['complexidade'], num(f['pf'])]
                  for f in itens], numericas=[0, 4], larguras=[8, 66, 8, 10, 8])

    saidas = d.salvar(pasta / cfg['arquivo_saida'])
    resumo = {'sigla': sig, 'pf': pf_total, 'preco_pf': preco, 'vt': vt, 'vi': vi, 'va': va,
              'funcoes': total_func, 'por_tipo': {k: v for k, v in por_tipo.items()},
              'por_modulo': {m: sum(f['pf'] for f in v) for m, v in por_mod.items()}}
    (pasta / 'resultado_laudo.json').write_text(json.dumps(resumo, ensure_ascii=False, indent=1), encoding='utf-8')
    return saidas, resumo


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    s, r = gerar(sys.argv[1])
    print(json.dumps(r, ensure_ascii=False, indent=1))
    for x in s:
        print('ok', x)
