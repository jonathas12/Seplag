"""Cópia do gerador do SISPAT com o campo `excluir_grupos` (lista de expressões regulares sobre o nome do grupo): as funções
desses grupos ficam fora do tamanho adotado (ex.: histórias não entregues pela fábrica). A soma entregue + excluída é
conferida com o total da planilha. Usado no laudo do SIFSW.

Versão do gerador para o laudo do SISPAT (módulos por seção da planilha, códigos de história repetidos entre módulos).
Uso: python _Modelo_Institucional/laudo_apf_sispat.py "4. Relatório Final/Laudos Técnicos de Avaliação/3. SISPAT/laudo_SISPAT.json"

Laudo Técnico de Avaliação de software medido por pontos de função (IN Conjunta nº 003/2022/SEPLAG/SEFAZ).

Lê a planilha de contagem (abas Contagem e Funções), agrupa as funções por módulo, gera os gráficos e
monta o laudo no modelo institucional (HTML, PDF e Word), a partir de um arquivo de configuração por sistema.

Uso (na pasta 2026):
    python _Modelo_Institucional/laudo_apf.py "4. Relatório Final/Laudos Técnicos de Avaliação/14. SICC/laudo_SICC.json"

O valor segue o art. 11 da IN: VA = VT + (VT x VI), com VT = tamanho em PF x preço do PF.

Campos opcionais da configuração (além dos usados pelo SICC):
  medida            "PF IFPUG" (padrão, coluna H, total em Funções!L4) ou "PF Local da FS" (coluna L, total em L6)
  formato_us        formato do código das histórias, padrão "US{:04d}"
  documentos        histórias de usuário com versão, data e aprovação (opcional)
  outros_documentos lista de [documento, identificação, data, uso na análise]
  custo_projeto     custo incorrido com a contratada, para a análise custo x valor do intangível
  textos: beneficio, texto_tipos, texto_evolucao, exemplos_tipos, motivo_variacao
"""
import collections
import json
from decimal import Decimal, ROUND_HALF_UP
import re
import sys
import textwrap
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import openpyxl

sys.path.insert(0, str(Path(__file__).parent))
from documento_seplag import Documento  # noqa: E402

AZUL, CINZA, TINTA = '#0b3d91', '#8A94A3', '#1f2937'
TIPOS = ('ALI', 'AIE', 'EE', 'CE', 'SE')
PF_PADRAO = {  # IFPUG: (tipo, complexidade) -> PF; usado só se a planilha não tiver valores calculados
    ('ALI', 'Baixa'): 7, ('ALI', 'Média'): 10, ('ALI', 'Alta'): 15,
    ('AIE', 'Baixa'): 5, ('AIE', 'Média'): 7, ('AIE', 'Alta'): 10,
    ('EE', 'Baixa'): 3, ('EE', 'Média'): 4, ('EE', 'Alta'): 6,
    ('CE', 'Baixa'): 3, ('CE', 'Média'): 4, ('CE', 'Alta'): 6,
    ('SE', 'Baixa'): 4, ('SE', 'Média'): 5, ('SE', 'Alta'): 7}
NOME_TIPO = {'ALI': 'Arquivo Lógico Interno (ALI)', 'AIE': 'Arquivo de Interface Externa (AIE)',
             'EE': 'Entrada Externa (EE)', 'CE': 'Consulta Externa (CE)', 'SE': 'Saída Externa (SE)'}
NOME_MANUT = {'I': 'Inclusão', 'E': 'Exclusão', 'A': 'Alteração', 'COS': 'Manutenção cosmética',
              'A50': 'Alteração (50%)', 'A75': 'Alteração (75%)', 'A90': 'Alteração (90%)', 'COR': 'Corretiva'}
VI_TABELA = [('Imprescindível', 'Na hipótese de inoperância, provocará prejuízo de altíssimo impacto', 1.0),
             ('Muito importante', 'Na hipótese de inoperância, provocará prejuízo de alto impacto', 0.75),
             ('Importante', 'Na hipótese de inoperância, provocará prejuízo de médio impacto', 0.50),
             ('Relativa importância', 'Na hipótese de inoperância, provocará prejuízo de baixo impacto', 0.25)]
EXEMPLOS_PADRAO = ['Cadastros mantidos pelo sistema', 'Dados de outros sistemas lidos pelo sistema',
                   'Incluir, alterar ou excluir registros', 'Listar e pesquisar registros',
                   'Relatórios e telas com cálculo ou dado derivado']


def brl(v):
    return 'R$ ' + f'{v:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')


def num(v, casas=0):
    return f'{v:,.{casas}f}'.replace(',', 'X').replace('.', ',').replace('X', '.')


def npf(v):
    """Pontos de função: sem casas quando inteiro, com uma casa quando fracionário."""
    return num(v, 0 if abs(v - round(v)) < 1e-9 else 1)


def r2(v):
    """Arredonda para centavos (meio para cima), como o Excel."""
    return float(Decimal(repr(v)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))


def pct(v):
    return num(v * 100, 1) + '%'


def codigo_us(texto):
    m = re.search(r'US[-_ ]?0*(\d{2,4})', texto or '')
    return int(m.group(1)) if m else None


# ---------------------------------------------------------------- leitura da planilha
def _faixa_soma(formula, padrao):
    m = re.search(r'SUM\(([A-Z]+)(\d+):[A-Z]+(\d+)\)', formula or '')
    return (int(m.group(2)), int(m.group(3))) if m else padrao


def ler_baseline(caminho, medida='PF IFPUG', secoes=()):
    wb = openpyxl.load_workbook(caminho, data_only=True)
    wf = openpyxl.load_workbook(caminho)['Funções']
    c, f = wb['Contagem'], wb['Funções']
    cel_total, col = ('L6', 12) if medida == 'PF Local da FS' else ('L4', 8)
    ini, fim = _faixa_soma(wf[cel_total].value, (8, f.max_row))
    cab = {'empresa': c['F4'].value, 'aplicacao': c['F5'].value, 'tipo': c['F6'].value, 'nivel': c['F7'].value,
           'projeto': c['F8'].value, 'responsavel': c['F9'].value, 'revisor': c['F10'].value,
           'tecnologia': c['R7'].value, 'guia': c['R8'].value, 'criacao': c['R9'].value, 'revisao': c['R10'].value,
           'proposito': c['A12'].value, 'escopo': c['A17'].value, 'documentacao': c['A22'].value,
           'pf_planilha': f[cel_total].value, 'pf_ifpug': f['L4'].value, 'pf_fs': f['L6'].value,
           'faixa': (ini, fim)}
    funcoes, grupo, secao = [], None, None
    for r in range(8, f.max_row + 1):
        nome, tipo = f.cell(r, 1).value, f.cell(r, 2).value
        tipo = str(tipo).strip() if tipo else ''
        if nome and not tipo:
            if str(nome).strip() in secoes:  # linha de título de seção (módulo) da planilha
                secao = str(nome).strip()
            else:
                grupo = str(nome).strip()
            continue
        if tipo not in TIPOS or not (ini <= r <= fim):
            continue
        complexidade = f.cell(r, 6).value
        pf_ifpug = f.cell(r, 8).value
        if pf_ifpug in (None, ''):  # sem valor calculado: usa a tabela IFPUG; sem complexidade, a função não pontua
            pf_ifpug = PF_PADRAO.get((tipo, complexidade), 0)
        pf = f.cell(r, col).value
        if col == 8:
            pf = pf_ifpug
        manut = f.cell(r, 3).value
        manut = str(manut).strip() if manut and str(manut).strip() else ''
        funcoes.append({'linha': r, 'grupo': grupo, 'secao': secao, 'funcao': str(nome or '').strip(), 'tipo': tipo,
                        'manutencao': manut, 'complexidade': complexidade, 'pf_ifpug': float(pf_ifpug),
                        'pf': float(pf) if pf not in (None, '') else 0.0, 'obs': f.cell(r, 15).value})
    return cab, funcoes


def atribuir_modulos(funcoes, cfg):
    """Módulo de cada função: por expressão regular no nome do grupo (`modulos_grupo`, lista de [regex, módulo],
    na seção indicada ou em qualquer uma), pela seção da planilha (`secoes`) ou pelo número da história (`modulos`)."""
    por_us = {n: m for m, lista in cfg['modulos'].items() for n in lista} if isinstance(cfg.get('modulos'), dict) else {}
    regras = cfg.get('modulos_grupo', [])
    for fn in funcoes:
        us = codigo_us(fn['funcao']) or codigo_us(fn['grupo'])
        fn['us'] = us
        mod = None
        for regra in regras:
            padrao, modulo = regra[0], regra[1]
            secao = regra[2] if len(regra) > 2 else None
            if (secao is None or secao == fn.get('secao')) and re.search(padrao, fn['grupo'] or '', re.I):
                mod = modulo
                break
        mod = mod or cfg.get('secoes', {}).get(fn.get('secao') or '')
        fn['modulo'] = mod or por_us.get(us) or cfg.get('grupos_sem_historia', {}).get(fn['grupo'], 'Outros')
    return funcoes


# ---------------------------------------------------------------- gráficos
def _estilo():
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9.5, 'axes.edgecolor': '#d9e1ec',
                         'axes.labelcolor': TINTA, 'xtick.color': TINTA, 'ytick.color': TINTA,
                         'axes.spines.top': False, 'axes.spines.right': False, 'text.parse_math': False})


def grafico_barras_h(rotulos, valores, titulo, arquivo, sufixo=' PF', quebra=None):
    _estilo()
    pares = sorted(zip([textwrap.fill(r, quebra) if quebra else r for r in rotulos], valores), key=lambda x: x[1])
    linhas = sum(r.count('\n') + 1 for r, _ in pares)
    fig, ax = plt.subplots(figsize=(8.6, 0.42 * len(pares) + 0.14 * (linhas - len(pares)) + 1.1))
    ax.barh([p[0] for p in pares], [p[1] for p in pares], color=AZUL, height=0.62)
    total = sum(valores)
    for i, (_, v) in enumerate(pares):
        ax.text(v + total * 0.006, i, f'{npf(v)}{sufixo} ({pct(v / total)})', va='center', fontsize=8.8, color=TINTA)
    ax.set_xlim(0, max(valores) * 1.28)
    ax.xaxis.set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.tick_params(axis='y', length=0)
    ax.set_title(titulo, loc='left', fontweight='bold', color=TINTA, fontsize=10.5)
    fig.tight_layout()
    fig.savefig(arquivo, dpi=200)
    plt.close(fig)


def grafico_valores(rotulos, valores, cores, titulo, arquivo):
    _estilo()
    fig, ax = plt.subplots(figsize=(8.6, 0.55 * len(rotulos) + 1.1))
    y = list(range(len(rotulos)))[::-1]
    ax.barh(y, valores, color=cores, height=0.6)
    for yi, v in zip(y, valores):
        ax.text(v + max(valores) * 0.01, yi, brl(v), va='center', fontsize=8.8, color=TINTA)
    ax.set_yticks(y, rotulos)
    ax.set_xlim(0, max(valores) * 1.25)
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
    rot = [(f"Inventário {h['inventario']}" if h.get('inventario') else f"v{h['versao']}") + f"\n{h['data']}" for h in historico]
    val = [h['pf'] for h in historico]
    ax.bar(rot, val, color=[CINZA] * (len(val) - 1) + [AZUL], width=0.5)
    for i, v in enumerate(val):
        ax.text(i, v + max(val) * 0.02, f'{npf(v)} PF', ha='center', fontsize=9, color=TINTA, fontweight='bold')
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
    medida = cfg.get('medida', 'PF IFPUG')
    comps = []
    if cfg.get('composicao'):  # tamanho composto por partes (ex.: medição indicativa + projetos medidos em planilha)
        funcoes = []
        for comp in cfg['composicao']:
            if comp.get('planilha'):
                cab_i, f_i = ler_baseline(pasta / comp['planilha'], comp.get('medida', 'PF IFPUG'))
                soma = round(sum(f['pf'] for f in f_i), 2)
                if cab_i['pf_planilha'] not in (None, '') and abs(float(cab_i['pf_planilha']) - soma) > 0.01:
                    raise SystemExit(f'{comp["nome"]}: soma das funções ({soma}) difere do total da planilha ({cab_i["pf_planilha"]}).')
                for f in f_i:
                    f['modulo'], f['us'] = comp['nome'], None
                funcoes += f_i
                comps.append(dict(comp, pf=soma, cab=cab_i, _funcoes=f_i))
            else:
                comps.append(dict(comp, cab=None))
        cab = next(c['cab'] for c in reversed(comps) if c['cab'])
    else:
        cab, funcoes = ler_baseline(pasta / cfg['baseline'], medida, tuple(cfg.get('secoes', {})))
        excl = [re.compile(x) for x in cfg.get('excluir_grupos', [])]
        excluidas = [f for f in funcoes if any(x.search(f['grupo'] or '') for x in excl)]
        funcoes = [f for f in funcoes if f not in excluidas]
        cfg['_pf_excluido'] = round(sum(f['pf'] for f in excluidas), 2)
        atribuir_modulos(funcoes, cfg)
    graf = pasta / 'graficos'
    graf.mkdir(exist_ok=True)
    fus = cfg.get('formato_us', 'US{:04d}')

    sig, nome = cfg['sigla'], cfg['nome']
    pf_total = round(sum(c['pf'] for c in comps), 2) if comps else round(sum(f['pf'] for f in funcoes), 2)
    if not comps and cab['pf_planilha'] not in (None, '') and abs(float(cab['pf_planilha']) - pf_total - cfg.get('_pf_excluido', 0)) > 0.01:
        raise SystemExit(f'Soma das funções ({pf_total}) difere do total da planilha ({cab["pf_planilha"]}).')
    preco, vi = cfg['preco_pf'], cfg['vi']
    vt_bruto = pf_total * preco  # sem arredondamento intermediário, como na planilha de avaliação
    vt = r2(vt_bruto)
    va = r2(vt_bruto * vi + vt_bruto)
    rotulo_vi = next(r for r, _, i in VI_TABELA if abs(i - vi) < 1e-9)
    docs = cfg.get('documentos', [])
    tem_aprov = any('aprovacao' in x for x in docs)
    n_aprov = sum(1 for x in docs if x.get('aprovacao'))
    sem_aprov = [x['codigo'] for x in docs if tem_aprov and not x.get('aprovacao')]
    txt_aprov = ''
    if docs and tem_aprov:
        txt_aprov = (f'{n_aprov} das {len(docs)} histórias de usuário têm aprovação datada pelas áreas de negócio'
                     if sem_aprov else f'As {len(docs)} histórias de usuário têm aprovação datada pelas áreas de negócio')
    detalhada = 'Detalhada' in cfg['nivel_contagem']

    por_tipo = collections.OrderedDict((t, [0, 0.0]) for t in TIPOS)
    for f in funcoes:
        por_tipo[f['tipo']][0] += 1
        por_tipo[f['tipo']][1] += f['pf']
    por_tipo = {k: v for k, v in por_tipo.items() if v[0]}
    por_mod = collections.OrderedDict()
    ordem_mod = list(cfg['ordem_modulos']) if cfg.get('ordem_modulos') else list(cfg.get('modulos', {}))
    for m in ([c['nome'] for c in comps if c['cab']] if comps else ordem_mod) + ['Outros']:
        itens = [f for f in funcoes if f['modulo'] == m]
        if itens:
            por_mod[m] = itens
    dados_pf = sum(v[1] for k, v in por_tipo.items() if k in ('ALI', 'AIE'))
    manuts = collections.OrderedDict()
    for f in funcoes:
        k = f['manutencao'] or 'sem tipo'
        manuts.setdefault(k, [0, 0.0, 0.0])
        manuts[k][0] += 1
        manuts[k][1] += f['pf_ifpug']
        manuts[k][2] += f['pf']
    so_inclusao = list(manuts) == ['I']
    total_func = sum(v[0] for v in por_tipo.values())
    comps_planilha = [c for c in comps if c['cab']]
    n_hist = (10 + 2 * len(comps_planilha)) if comps else 11 + (not so_inclusao)

    if comps:
        grafico_barras_h([c.get('rotulo', c['nome']) for c in comps], [c['pf'] for c in comps],
                         f'Composição do tamanho funcional do {sig}', graf / 'G1_composicao.png')
    else:
        grafico_barras_h([NOME_TIPO[t] for t in por_tipo], [v[1] for v in por_tipo.values()],
                         f'Tamanho funcional do {sig} por tipo de função', graf / 'G1_pf_por_tipo.png')
        grafico_barras_h(list(por_mod), [sum(f['pf'] for f in v) for v in por_mod.values()],
                         f'Tamanho funcional do {sig} por módulo', graf / 'G2_pf_por_modulo.png',
                         quebra=cfg.get('quebrar_rotulos_grafico'))
    grafico_evolucao(cfg['historico_medicoes'], graf / 'G3_evolucao_baseline.png',
                     f'Evolução do tamanho funcional do {sig} nos inventários' if cfg['historico_medicoes'][0].get('inventario') else f'Evolução do tamanho funcional do {sig} nas medições')

    resp = cfg['responsavel']
    d = Documento(f'Laudo Técnico de Avaliação - {sig}',
                  [f'Inventário de Bens Intangíveis - Exercício {cfg["exercicio"]}', nome],
                  cfg['arquivo_saida'], setor='Comissão de Inventário e Avaliação de Bens Intangíveis (CIABI/SEPLAG)',
                  cidade_data=cfg['cidade_data'])
    d.cards([('Tamanho funcional', f'{npf(pf_total)} PF', cfg['nivel_contagem']),
             ('Preço do ponto de função', brl(preco), 'data-base 10/2026'),
             ('Valor Institucional', num(vi, 2), rotulo_vi),
             ('Valor do ativo (VA)', brl(va), 'IN 03/2022, art. 11')])
    d.p(f'Este Laudo Técnico de Avaliação determina o valor do {nome} ({sig}), bem intangível da Secretaria de Estado '
        f'de Planejamento e Gestão de Mato Grosso, para fins de inventário e registro contábil do exercício de '
        f'{cfg["exercicio"]}, nos termos dos arts. 5º, VI, 11 e 20 da Instrução Normativa Conjunta nº 003/2022/SEPLAG/SEFAZ.')

    # 1. Identificação
    d.secao('📌', '1. Identificação do bem')
    revisao = cab['revisao'] or cab['criacao']
    d.tabela(['Item', 'Informação'], [
        ['Sigla e nome', f'{sig} - {nome}'],
        ['Tipo de bem', cfg['tipo_bem']],
        ['Situação', cfg['situacao']],
        ['Tecnologia predominante', cfg['tecnologia']],
        ['Desenvolvimento', cfg['unidade_desenvolvimento']],
        ['Áreas de negócio', cfg['areas_negocio']],
        ['Perfis de usuário', cfg['perfis']],
        ['Base legal de uso', cfg['base_legal']] if cfg.get('base_legal') else None,
        ['Identificação contábil (IN, art. 20, II)', 'Ativo intangível, grupo Softwares (PCASP 1.2.4.1). Conta detalhada conforme a Instrução de Serviço nº 022/2020-SACE/SEFAZ, item 4.7, a confirmar pelo setor contábil'],
        ['Vida útil', cfg['vida_util']],
        ['Planilha de contagem', cfg.get('planilha_identificacao') or f'{cfg["baseline_nome"]} ({"revisão" if cab["revisao"] else "criação"} de {revisao:%d/%m/%Y})'],
    ], legenda='Tabela 1 - Identificação do bem avaliado', larguras=[30, 70])
    d.blocos[-1] = d.blocos[-1][:2] + ([l for l in d.blocos[-1][2] if l],) + d.blocos[-1][3:]

    # 2. Descrição
    d.secao('🧩', '2. Descrição detalhada do bem')
    for par in cfg['finalidade']:
        d.p(par)
    d.subsecao('2.1 Módulos e funcionalidades')
    if cfg.get('modulos_tabela'):
        d.tabela(['Módulo', 'Funcionalidades'], cfg['modulos_tabela'], legenda='Tabela 2 - Módulos do sistema', larguras=[28, 72])
    else:
        linhas = []
        for m, itens in por_mod.items():
            if cfg.get('descricao_modulos'):  # descrição do módulo e número de histórias (códigos repetidos entre módulos)
                n_h = len({f['grupo'] for f in itens})
                txt = f'{cfg["descricao_modulos"].get(m, "")} ({n_h} {"história" if n_h == 1 else "histórias"})'
            else:
                uss = sorted({f['us'] for f in itens if f['us']})
                txt = ', '.join(fus.format(u) for u in uss) or 'Funções sem história de usuário associada'
            linhas.append([m, txt, num(len(itens)), npf(sum(f['pf'] for f in itens))])
        d.tabela(['Módulo', 'Funcionalidades e histórias de usuário' if cfg.get('descricao_modulos') else 'Histórias de usuário', 'Funções', 'PF'], linhas,
                 legenda='Tabela 2 - Módulos do sistema, histórias de usuário e tamanho funcional', numericas=[2, 3],
                 larguras=[30, 50, 10, 10])
    d.subsecao('2.2 Integrações e fronteira da aplicação')
    d.tabela(['Sistema ou serviço', 'Uso pelo ' + sig, 'Tratamento na contagem'], cfg['integracoes'],
             legenda='Tabela 3 - Sistemas com que o bem se relaciona', larguras=[28, 44, 28])
    if cfg.get('contratos'):
        d.subsecao('2.3 Contratos e direitos sobre o bem')
        for par in cfg.get('texto_contratos_antes', []):
            d.p(par)
        d.tabela(['Instrumento', 'Objeto', 'Vigência ou data', 'Valor'], cfg['contratos'],
                 legenda='Tabela 3A - Contratos relacionados ao bem', larguras=[20, 46, 16, 18])
        for par in cfg.get('texto_contratos', []):
            d.p(par)

    # 3. Enquadramento
    d.secao('⚖️', '3. Reconhecimento como ativo intangível')
    d.p('Antes da mensuração, a comissão verificou se o bem atende aos critérios de reconhecimento da IN. O resultado está na Tabela 4.')
    d.tabela(['Critério', 'Base na IN', 'Verificação'], [
        ['Código-fonte de propriedade do Estado', 'art. 2º, § 1º', cfg.get('propriedade', 'Software desenvolvido internamente pela SEPLAG/MT')],
        [cfg.get('rotulo_uso', 'Em uso, sem obsolescência'), 'art. 2º, § 2º, II', cfg.get('uso', f'{cfg["situacao"]}, com histórias de usuário revisadas em {cfg["exercicio"]}')],
        ['Gerador de benefícios ou potencial de serviços', 'art. 6º, parágrafo único, I', cfg['beneficio']],
        ['Mensuração confiável', 'art. 6º, parágrafo único, II', f'Tamanho funcional de {npf(pf_total)} PF medido por método normatizado (ISO/IEC 20926{"" if detalhada else " e ISO/IEC 24570"})'],
        [cfg.get('rotulo_fase', 'Fase de desenvolvimento, não de pesquisa'), 'arts. 8º e 9º', cfg.get('fase_texto', 'Funcionalidades especificadas e em produção.' + (f' {txt_aprov}' if txt_aprov else ''))],
        ['Documentação de custos insuficiente', 'art. 11', cfg['custo_incorrido']],
    ], legenda='Tabela 4 - Critérios de reconhecimento e enquadramento na metodologia do art. 11', larguras=[28, 20, 52])
    d.caixa('conclusao', 'Conclusão do reconhecimento:',
            cfg.get('conclusao_reconhecimento', f'O {sig} atende aos critérios de reconhecimento e é avaliado pela metodologia do art. 11 da IN, '
            'com base no tamanho funcional em pontos de função e no Valor Institucional.'))

    # 4. Metodologia
    d.secao('🔎', '4. Metodologia de identificação, mensuração e avaliação')
    d.p('A avaliação seguiu as etapas do art. 5º da IN, detalhadas no fluxo abaixo. Cada etapa tem um registro que permite refazê-la.')
    d.tabela(['Etapa', 'O que foi feito', 'Registro'], [
        ['1. Levantamento', 'Inclusão do bem na relação de sistemas da SEPLAG para o exercício', 'Relação de sistemas (aba Avaliação 2026)'],
        ['2. Reconhecimento', 'Verificação dos critérios dos arts. 2º, 6º, 8º, 9º e 11 da IN', 'Tabela 4 deste laudo'],
        ['3. Análise documental', cfg.get('analise_documental', f'Leitura das {len(docs)} histórias de usuário: premissas, critérios de aceitação, regras de negócio, protótipos, histórico de versões e aprovações'), 'Anexo I'],
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
    ex = cfg.get('exemplos_tipos', EXEMPLOS_PADRAO)
    d.tabela(['Tipo de função', 'O que representa', 'Exemplo no ' + sig], [
        ['Arquivo Lógico Interno (ALI)', 'Grupo de dados mantido pela aplicação', ex[0]],
        ['Arquivo de Interface Externa (AIE)', 'Grupo de dados de outra aplicação, apenas lido', ex[1]],
        ['Entrada Externa (EE)', 'Processo que recebe dados e altera um ALI', ex[2]],
        ['Consulta Externa (CE)', 'Processo que apresenta dados sem cálculo', ex[3]],
        ['Saída Externa (SE)', 'Processo que apresenta dados com cálculo ou dado derivado', ex[4]],
    ], legenda='Tabela 6 - Tipos de função da APF', larguras=[26, 40, 34])
    d.p('A contagem percorre os passos do IFPUG: (1) definir o propósito da contagem; (2) definir o tipo de contagem '
        '(aplicação, projeto de desenvolvimento ou de melhoria); (3) definir o escopo e a fronteira da aplicação, '
        'separando o que é do sistema do que pertence a outros sistemas; (4) identificar as funções de dados (ALI e AIE); '
        '(5) identificar as funções de transação (EE, CE e SE) a partir dos processos elementares descritos na documentação; '
        '(6) classificar a complexidade de cada função; (7) somar as contribuições em pontos de função.')
    d.subsecao('4.2 Nível de detalhe da contagem')
    niveis = ['Indicativa', 'Estimativa', 'Detalhada']
    d.tabela(['Nível', 'Como é feito', 'Quando se usa'], [
        ['Indicativa (NESMA)', 'Considera só as funções de dados: 35 PF por ALI e 15 PF por AIE (IN, art. 11, § 2º)', 'Visão inicial, poucos requisitos conhecidos'],
        ['Estimativa (NESMA)', 'Identifica todas as funções de dados e de transação; atribui complexidade baixa às funções de dados e média às de transação', 'Funcionalidades conhecidas, sem detalhe de campos e registros'],
        ['Detalhada (IFPUG)', 'Identifica todas as funções e calcula a complexidade de cada uma por tipos de dados e registros', 'Especificação completa'],
    ], legenda='Tabela 7 - Níveis de detalhe da contagem', larguras=[20, 52, 28],
        destaque_linhas=[i for i, n in enumerate(niveis) if n in cfg['nivel_contagem']])
    if cfg.get('texto_nivel'):
        d.p(cfg['texto_nivel'])
    elif detalhada:
        d.p(f'O {sig} foi medido no nível **{cfg["nivel_contagem"]}**. Nesse nível, a complexidade de cada função (baixa, média '
            'ou alta) é determinada pelas tabelas do IFPUG: nas funções de dados, pela quantidade de tipos de dados (TD) e de '
            'tipos de registro (TR); nas funções de transação, pela quantidade de tipos de dados e de arquivos referenciados (AR). '
            'A contribuição varia de 7 a 15 PF por ALI, de 5 a 10 PF por AIE, de 3 a 6 PF por EE e CE e de 4 a 7 PF por SE.')
    else:
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
    if comps:
        _secao5_composta(d, cfg, comps, pf_total, graf, sig)
    else:
        _secao5_simples(d, cfg, cab, medida, sig, docs, por_tipo, total_func, pf_total, dados_pf, so_inclusao, manuts, graf)
    sec = (len([c for c in comps if c['cab']]) + 1) if comps else (2 if not so_inclusao else 1)
    d.subsecao(f'5.{sec} Evolução das medições')
    h = cfg['historico_medicoes']
    if h[0].get('inventario'):
        d.tabela(['Inventário', 'Data da mensuração', 'Situação', 'Nível', 'PF', 'Observação'],
                 [[str(x['inventario']), x['data'], x.get('situacao', ''), x['nivel'], npf(x['pf']), x.get('uso', '')] for x in h],
                 legenda=f'Tabela {n_hist} - Medições do {sig} por inventário', numericas=[4],
                 larguras=[11, 13, 15, 17, 10, 34], destaque_linhas=[len(h) - 1], fonte=cfg.get('fonte_historico'))
    else:
        d.tabela(['Versão', 'Data', 'Nível', 'PF', 'Uso'], [[x['versao'], x['data'], x['nivel'], npf(x['pf']), x['uso']] for x in h],
                 legenda=f'Tabela {n_hist} - Medições do ' + sig, numericas=[3], larguras=[10, 14, 24, 12, 40], destaque_linhas=[len(h) - 1])
    d.figura(graf / 'G3_evolucao_baseline.png', f'Figura 3 - Evolução do tamanho funcional do {sig}')
    ant = h[-2]['pf']
    if h[0].get('inventario'):
        d.p(f'O tamanho passou de {npf(h[0]["pf"])} PF no inventário de {h[0]["inventario"]} para {npf(pf_total)} PF no de '
            f'{h[-1]["inventario"]} ({pct(pf_total / h[0]["pf"] - 1)}), e de {npf(ant)} PF no inventário anterior '
            f'({"+" if pf_total >= ant else ""}{pct(pf_total / ant - 1)}). ' + cfg.get('texto_evolucao', ''))
    else:
        d.p(f'O tamanho passou de {npf(ant)} PF na versão {h[-2]["versao"]} para {npf(pf_total)} PF na versão {h[-1]["versao"]} '
            f'(+{pct(pf_total / ant - 1)}). ' + cfg.get('texto_evolucao', ''))

    # 6. Valor
    nt = n_hist + 1
    d.secao('🧮', '6. Determinação do valor')
    d.subsecao('6.1 Valor Institucional do ' + sig)
    for par in cfg['vi_justificativa']:
        d.p(par)
    d.subsecao('6.2 Cálculo')
    d.tabela(['Componente', 'Fórmula', 'Valor'], [
        ['Tamanho funcional', cfg.get('formula_tamanho', f'Planilha de contagem, aba Funções ({medida})'), f'{npf(pf_total)} PF'],
        ['Preço do ponto de função', cfg.get('fonte_preco_curta', 'Manifestação Técnica da pesquisa de preços (data-base 10/2026)'), brl(preco)],
        ['Valor do tamanho do ativo (VT)', f'{npf(pf_total)} x {brl(preco)}', brl(vt)],
        ['Valor Institucional (VI)', f'{rotulo_vi} (art. 11, § 4º)', num(vi, 2)],
        ['Parcela institucional', f'VT x VI = {brl(vt)} x {num(vi, 2)}', brl(r2(vt_bruto * vi))],
        ['Valor do ativo (VA)', 'VT + (VT x VI)', brl(va)],
    ], legenda=f'Tabela {nt} - Cálculo do valor do ativo', numericas=[2], larguras=[30, 46, 24], destaque_linhas=[5],
        fonte='Cálculo sem arredondamento intermediário, como na planilha de avaliação: os valores exibidos são arredondados '
              'para centavos só no fim, por isso a soma das parcelas exibidas pode diferir do VA em um centavo.' if r2(vt) + r2(vt_bruto * vi) != va else None)
    nt += 1
    a = cfg.get('avaliacao_anterior')
    sub = 3
    if a:
        vt0_bruto = a['pf'] * a['preco_pf']
        vt0 = r2(vt0_bruto)
        va0 = r2(vt0_bruto * a['vi'] + vt0_bruto)
        d.subsecao(f'6.{sub} Comparação com o inventário de ' + str(a['exercicio']))
        sub += 1
        d.tabela(['Componente', f'Inventário {a["exercicio"]}', f'Inventário {cfg["exercicio"]}', 'Variação'], [
            ['Situação', a['situacao'], cfg['situacao'], '-'],
            ['Tamanho funcional (PF)', npf(a['pf']), npf(pf_total), pct(pf_total / a['pf'] - 1)],
            ['Preço do PF', brl(a['preco_pf']), brl(preco), pct(preco / a['preco_pf'] - 1)],
            ['Valor Institucional', num(a['vi'], 2), num(vi, 2), '-'],
            ['Valor do tamanho (VT)', brl(vt0), brl(vt), pct(vt / vt0 - 1)],
            ['Valor do ativo (VA)', brl(va0), brl(va), pct(va / va0 - 1)],
        ], legenda=f'Tabela {nt} - Comparação entre as avaliações de {a["exercicio"]} e {cfg["exercicio"]}', numericas=[1, 2, 3],
            larguras=[30, 24, 24, 22], destaque_linhas=[5])
        nt += 1
        d.p(cfg.get('motivo_variacao', f'A variação decorre de três fatores, todos documentados: o aumento do tamanho funcional, '
            f'o novo preço do ponto de função apurado na pesquisa de {cfg["exercicio"]} e a reclassificação do Valor Institucional, '
            f'de {num(a["vi"], 2)} para {num(vi, 2)}, com a entrada do sistema em produção.'))

    cp = cfg.get('custo_projeto')
    if cp:
        nt = _secao_custo(d, cp, sig, pf_total, preco, vt, va, sub, nt, graf)

    # 7. Vida útil
    d.secao('📅', '7. Vida útil')
    if cfg.get('texto_vida_util'):
        for par in cfg['texto_vida_util']:
            d.p(par)
    else:
      d.p(f'A vida útil do {sig} é classificada como **{cfg["vida_util"].lower()}** (IN, arts. 14 e 15). Pelos fatores do '
        'art. 14, § 1º: o uso é contínuo e previsto por tempo indeterminado; o sistema é mantido pela SEPLAG e pode '
        'ser gerido por outra equipe, pois o código-fonte pertence ao Estado; não há contrato de licença ou cessão que limite '
        f'o uso; a tecnologia ({cfg["tecnologia"]}) segue suportada; e o sistema continua em evolução. Não há limite previsível '
        'para o período em que o bem fornecerá potencial de serviços.')
      d.p('Por isso o bem não é amortizado (art. 17) e deve passar anualmente pelo teste de redução ao valor recuperável (art. 18). '
        'A vida útil remanescente exigida pelo art. 20, IV, não se aplica, por se tratar de vida útil indefinida.')

    # 8. Ressalvas
    d.secao('⚠️', '8. Limitações e ressalvas')
    ress = []
    if not detalhada:
        ress.append(f'A contagem no nível {cfg["nivel_contagem"]} usa complexidades padronizadas. Uma contagem detalhada pode '
                    'resultar em tamanho diferente, para mais ou para menos.')
    ress.append(cfg.get('texto_tamanho_ref', 'O tamanho refere-se às funcionalidades descritas na documentação e em produção na data da contagem.') + ' Ficam fora do escopo: '
                + ' '.join(cfg['fora_do_escopo']))
    ress.append(cfg['custo_incorrido'])
    ress.append(cfg.get('ressalva_documentacao', 'O conteúdo e a qualidade das histórias de usuário são de responsabilidade da equipe do projeto que as elaborou.')
                + (f' {txt_aprov}; nas demais ({", ".join(sem_aprov)}), a seção de aprovação está sem preenchimento. '
                   'As funcionalidades correspondentes foram consideradas por estarem em produção.' if sem_aprov else ''))
    ress.append('O preço do ponto de função é referência de mercado para fins de inventário e registro contábil (IN, art. 13); '
                'não se destina a contratação.')
    ress += cfg.get('ressalvas_extras', [])
    if cfg.get('ressalva_comissao'):
        ress.append(cfg['ressalva_comissao'])
    d.lista(ress)

    # 9. Conclusão
    d.secao('✅', '9. Conclusão')
    d.caixa('conclusao', f'Valor do {sig} para o inventário de {cfg["exercicio"]}:',
            f'Com tamanho funcional de **{npf(pf_total)} pontos de função** ({cfg["nivel_contagem"]}), preço de **{brl(preco)}** '
            f'por ponto de função e Valor Institucional de **{num(vi, 2)} ({rotulo_vi})**, o valor do ativo intangível '
            f'{nome} ({sig}) é de **{brl(va)}**, com vida útil {cfg["vida_util"].lower()}.')
    d.p(cfg.get('texto_acompanham', 'A planilha de contagem e as histórias de usuário que fundamentam este laudo acompanham o '
                'processo do inventário para conferência.'))
    d.p('É o laudo.')
    d.assinatura('Responsável pela mensuração (IN, art. 20, V)', resp['nome'], resp['cargo'],
                 *([resp['funcao']] if resp.get('funcao') else []),
                 f'{resp["portaria"]} - matrícula {resp["matricula"]}', cfg['cidade_data'])

    # Anexos
    d.quebra()
    d.secao('📎', 'Anexo I - Documentação utilizada na análise')
    d.p(f'{cfg["documentacao_fonte"]} Planilha de contagem: {cfg["baseline_nome"]}.')
    if cfg.get('outros_documentos'):
        d.tabela(['Documento', 'Identificação', 'Data', 'Uso na análise'], cfg['outros_documentos'],
                 legenda='Tabela A1 - Documentos analisados', larguras=[30, 24, 12, 34])
    if docs:
        mod_de = {n: m for m, l in cfg['modulos'].items() for n in l} if isinstance(cfg.get('modulos'), dict) else {}
        cab_d = ['Código', 'História de usuário', 'Módulo', 'Versão', 'Data'] + (['Aprovação'] if tem_aprov else [])
        d.tabela(cab_d,
                 [[f'[{x["codigo"]}]({x["link"]})' if x.get('link') else x['codigo'], x['nome'],
                   x.get('modulo') or mod_de.get(codigo_us(x['codigo']), ''), x.get('versao', ''), x.get('data', '')] +
                  ([x.get('aprovacao') or 'sem registro'] if tem_aprov else []) for x in docs],
                 legenda='Tabela A2 - Histórias de usuário' + (': última versão do histórico de revisões e data da aprovação pelas áreas de negócio' if tem_aprov else ''),
                 larguras=[10, 32, 26, 8, 11, 13] if tem_aprov else [10, 40, 30, 9, 11])
    d.secao('📎', 'Anexo II - Funções contadas')
    d.p(cfg.get('texto_anexo2') or f'Relação das {total_func} funções da aba Funções da planilha {cfg["baseline_nome"]}, agrupadas por módulo, '
        f'com a contribuição de cada uma na medida adotada ({medida}).')
    for m, itens in por_mod.items():
        d.subsecao(f'{m} ({npf(sum(f["pf"] for f in itens))} PF)')
        if so_inclusao:
            d.tabela(['Linha', 'Função', 'Tipo', 'Complex.', 'PF'],
                     [[str(f['linha']), f['funcao'] + (f' ({f["obs"]})' if f['obs'] else ''), f['tipo'], f['complexidade'], npf(f['pf'])]
                      for f in itens], numericas=[0, 4], larguras=[8, 66, 8, 10, 8])
        else:
            d.tabela(['Linha', 'Função', 'Tipo', 'Complex.', 'Manut.', 'PF'],
                     [[str(f['linha']), f['funcao'] + (f' ({f["obs"]})' if f['obs'] else ''), f['tipo'], f['complexidade'],
                       f['manutencao'] or '-', npf(f['pf'])] for f in itens],
                     numericas=[0, 5], larguras=[8, 58, 7, 10, 9, 8])

    saidas = d.salvar(pasta / cfg['arquivo_saida'])
    resumo = {'sigla': sig, 'medida': medida, 'pf': pf_total, 'preco_pf': preco, 'vt': vt, 'vi': vi, 'va': va,
              'funcoes': total_func, 'por_tipo': {k: v for k, v in por_tipo.items()},
              'por_manutencao': {k: v for k, v in manuts.items()},
              'por_modulo': {m: round(sum(f['pf'] for f in v), 2) for m, v in por_mod.items()}}
    (pasta / 'resultado_laudo.json').write_text(json.dumps(resumo, ensure_ascii=False, indent=1), encoding='utf-8')
    return saidas, resumo


def _secao5_simples(d, cfg, cab, medida, sig, docs, por_tipo, total_func, pf_total, dados_pf, so_inclusao, manuts, graf):
    d.tabela(['Item', 'Definição na contagem'], [
        ['Propósito', cfg.get('proposito', 'Criar a linha de base do produto para planejamento, acompanhamento, estimativa de custos e avaliação do ativo')],
        ['Tipo de contagem', cab['tipo']],
        ['Nível de detalhe', cab['nivel']],
        ['Medida adotada', cfg.get('medida_descricao', f'{medida} (total da aba Funções)')],
        ['Versão do manual', f'IFPUG CPM {cab["guia"]}'],
        ['Responsável e revisor', f'{cab["responsavel"]} / {cab["revisor"] or "não informado"}'],
        ['Criação e última revisão', f'{cab["criacao"]:%d/%m/%Y}' + (f' e {cab["revisao"]:%d/%m/%Y}' if cab['revisao'] else ' (sem data de revisão)')],
        ['Fronteira', 'Aplicação ' + sig + '. Os dados de outros sistemas apenas lidos foram contados como AIE (Tabela 3)'],
        ['Documentação', cfg.get('documentacao_resumo', f'{len(docs)} histórias de usuário (Anexo I)')],
    ], legenda='Tabela 9 - Parâmetros da contagem', larguras=[28, 72])
    d.p('O escopo da contagem registrado na planilha é o seguinte:')
    d.lista([re.sub(r'^\d+\s*-\s*', '', l).rstrip(';') for l in cab['escopo'].splitlines() if l.strip()])
    d.tabela(['Tipo de função', 'Quantidade', 'PF por função', 'Total de PF', '% do total'],
             [[NOME_TIPO[t], num(q), num(p / q, 1), npf(p), pct(p / pf_total)] for t, (q, p) in por_tipo.items()] +
             [['Total', num(total_func), '', npf(pf_total), '100,0%']],
             legenda=f'Tabela 10 - Tamanho funcional do {sig} por tipo de função', numericas=[1, 2, 3, 4],
             larguras=[38, 14, 16, 16, 16], destaque_linhas=[len(por_tipo)])
    d.figura(graf / 'G1_pf_por_tipo.png', f'Figura 1 - Tamanho funcional do {sig} por tipo de função')
    d.p(f'As funções de dados somam {npf(dados_pf)} PF ({pct(dados_pf / pf_total)}) e as de transação, '
        f'{npf(pf_total - dados_pf)} PF ({pct(1 - dados_pf / pf_total)}).' + (' ' + cfg['texto_tipos'] if cfg.get('texto_tipos') else ''))
    if not so_inclusao:
        d.subsecao('5.1 Composição do tamanho por tipo de manutenção')
        d.p(cfg.get('texto_manutencao', 'A planilha registra, para cada função, o tipo de manutenção. A medida adotada aplica os '
                    'deflatores do Roteiro de Métricas do SISP a cada tipo:'))
        d.tabela(['Tipo de manutenção', 'Funções', 'PF IFPUG', medida],
                 [[NOME_MANUT.get(k, k), num(q), npf(pi), npf(pm)] for k, (q, pi, pm) in manuts.items()] +
                 [['Total', num(sum(v[0] for v in manuts.values())), npf(sum(v[1] for v in manuts.values())), npf(pf_total)]],
                 legenda='Tabela 11 - Tamanho por tipo de manutenção', numericas=[1, 2, 3], larguras=[40, 16, 22, 22],
                 destaque_linhas=[len(manuts)])
    d.figura(graf / 'G2_pf_por_modulo.png', f'Figura 2 - Tamanho funcional do {sig} por módulo')


def _secao5_composta(d, cfg, comps, pf_total, graf, sig):
    """Tamanho composto: tabela de componentes e, para cada componente com planilha, parâmetros e tipos de função."""
    for par in cfg.get('texto_composicao', []):
        d.p(par)
    d.tabela(['Componente', 'Fonte', 'Nível', 'Medida', 'PF'],
             [[c['nome'], c['fonte'], c['nivel'], c.get('medida', 'PF IFPUG') if c['cab'] else c.get('medida', 'Indicativa'), npf(c['pf'])] for c in comps] +
             [['Total', '', '', '', npf(pf_total)]],
             legenda=f'Tabela 9 - Composição do tamanho funcional do {sig}', numericas=[4], larguras=[30, 30, 15, 13, 12],
             destaque_linhas=[len(comps)])
    d.figura(graf / 'G1_composicao.png', f'Figura 1 - Composição do tamanho funcional do {sig}')
    nt, k = 10, 1
    for c in comps:
        if not c['cab']:
            continue
        cab = c['cab']
        d.subsecao(f'5.{k} {c["nome"]}')
        k += 1
        d.tabela(['Item', 'Definição na contagem'], [
            ['Projeto', cab['projeto']],
            ['Tipo de contagem', cab['tipo']],
            ['Nível de detalhe', cab['nivel']],
            ['Medida adotada', f'{c.get("medida", "PF IFPUG")} (total da aba Funções: {npf(c["pf"])} PF; PF IFPUG: {npf(float(cab["pf_ifpug"] or 0))})'],
            ['Responsável e revisor', f'{cab["responsavel"]} / {cab["revisor"] or "não informado"}'],
            ['Criação e última revisão', f'{cab["criacao"]:%d/%m/%Y}' + (f' e {cab["revisao"]:%d/%m/%Y}' if cab['revisao'] else ' (sem data de revisão)')],
            ['Escopo registrado', '; '.join(l.strip() for l in (cab['escopo'] or '').splitlines() if l.strip())],
            ['Planilha', c['planilha'].split('/')[-1]],
        ], legenda=f'Tabela {nt} - Parâmetros da contagem: {c["nome"]}', larguras=[26, 74])
        nt += 1
        for par in c.get('texto', []):
            d.p(par)
        man = collections.OrderedDict()
        for f in c['_funcoes']:
            key = (f['tipo'], f['manutencao'] or 'sem tipo')
            man.setdefault(key, [0, 0.0, 0.0])
            man[key][0] += 1
            man[key][1] += f['pf_ifpug']
            man[key][2] += f['pf']
        d.tabela(['Tipo de função', 'Manutenção', 'Funções', 'PF IFPUG', c.get('medida', 'PF IFPUG')],
                 [[NOME_TIPO[t], NOME_MANUT.get(m, m), num(q), npf(pi), npf(pm)] for (t, m), (q, pi, pm) in man.items()] +
                 [['Total', '', num(sum(v[0] for v in man.values())), npf(sum(v[1] for v in man.values())), npf(c['pf'])]],
                 legenda=f'Tabela {nt} - Funções por tipo e manutenção: {c["nome"]}', numericas=[2, 3, 4],
                 larguras=[34, 22, 12, 16, 16], destaque_linhas=[len(man)])
        nt += 1


def _secao_custo(d, cp, sig, pf_total, preco, vt, va, sub, nt, graf):
    """Custo incorrido com a contratada x valor do intangível."""
    comp = cp['componentes']  # [[nome, valor], ...]
    total = round(sum(v for _, v in comp), 2)
    if abs(total - cp['custo_total']) > 0.05:
        raise SystemExit(f'Componentes do custo ({total}) não somam o custo total ({cp["custo_total"]}).')
    construcao = round(sum(v for n, v in comp if n in cp['componentes_construcao']), 2)
    fator = cp.get('fator_grupo_contratado')
    equivalente = round(construcao / fator, 2) if fator else None
    d.subsecao(f'6.{sub} Custo do projeto e valor do intangível')
    d.p(cp['contexto'])
    d.tabela(['Componente do custo', 'Valor', '% do custo'],
             [[n, brl(v), pct(v / total)] for n, v in comp] + [['Custo total com a contratada', brl(total), '100,0%']],
             legenda=f'Tabela {nt} - Custo do projeto com a contratada ({cp["fonte"]})', numericas=[1, 2],
             larguras=[50, 28, 22], destaque_linhas=[len(comp)])
    nt += 1
    linhas = [
        ['PF faturados no projeto', f'{npf(cp["pf_faturado"])} PF', 'Soma das entregas medidas nas ordens de serviço'],
        ['Tamanho funcional do ativo', f'{npf(pf_total)} PF', 'Seção 5'],
        ['PF faturados por PF do ativo', num(cp['pf_faturado'] / pf_total, 2), 'Entregas sucessivas, alterações e testes medidos ao longo do projeto'],
        ['Custo médio por PF faturado', brl(total / cp['pf_faturado']), 'Custo total / PF faturados'],
        ['Custo da contratada por PF do ativo', brl(total / pf_total), 'Custo total / tamanho funcional'],
        ['Preço do PF no contrato (vigente)', brl(cp['preco_contrato']), cp.get('nota_preco_contrato', 'Contrato nº 014/2022/SEPLAG')],
        ['Preço de mercado do PF (avaliação)', brl(preco), 'Seção 4.3'],
    ]
    d.tabela(['Indicador', 'Valor', 'Observação'], linhas, legenda=f'Tabela {nt} - Indicadores do custo do projeto',
             numericas=[1], larguras=[34, 20, 46])
    nt += 1
    rot = ['Custo com a contratada', 'Valor do tamanho (VT)', 'Valor do ativo (VA)']
    val = [total, vt, va]
    cores = [CINZA, AZUL, AZUL]
    if equivalente:
        rot.insert(1, 'Custo de construção equivalente (estimado)')
        val.insert(1, equivalente)
        cores.insert(1, CINZA)
    grafico_valores(rot, val, cores, f'{sig}: custo do projeto e valor do intangível', graf / 'G4_custo_x_valor.png')
    d.figura(graf / 'G4_custo_x_valor.png', f'Figura 4 - Custo do projeto com a contratada e valor do intangível do {sig}')
    pars = [f'O custo pago à contratada ({brl(total)}) corresponde a {pct(total / vt)} do valor do tamanho do ativo (VT) e a '
            f'{pct(total / va)} do valor do ativo (VA).']
    if equivalente:
        pars.append(f'{cp.get("fonte_fator", "Nas ordens de serviço")}, a contratada executa apenas parte das atividades de cada ponto de função '
                    f'({pct(fator)} do esforço, Grupo II: construção, testes e homologação); a outra parte (requisitos, análise e '
                    f'projeto) é feita pela equipe da SEPLAG. Dividindo o custo de construção ({brl(construcao)}) por {num(fator, 2)}, '
                    f'o custo equivalente da construção completa, a preços do contrato, seria de cerca de {brl(equivalente)}, '
                    'sem incluir infraestrutura, banco de dados e DevOps. É uma estimativa, não um custo apurado.')
    pars += cp.get('interpretacao', [])
    for p_ in pars:
        d.p(p_)
    d.caixa('atencao', 'Por que o custo não substitui o valor:', cp['conclusao'])
    return nt


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    s, r = gerar(sys.argv[1])
    print(json.dumps(r, ensure_ascii=False, indent=1))
    for x in s:
        print('ok', x)
