"""Gera a planilha do mapa comparativo (com rastreabilidade) e as fichas HTML de evidência de cada referência Java."""
import csv, json, html, os, datetime
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
RAIZ = '..'
rows = list(csv.DictReader(open(f'{RAIZ}/4. Mapa Comparativo/Precos_Ponto_Funcao_2025-2026.csv', encoding='utf-8-sig'), delimiter=';'))
res = json.load(open(f'{RAIZ}/5. Análise Estatística/resultados_analise.json', encoding='utf-8'))
log = json.load(open('Dados_Brutos/_log_consultas.json', encoding='utf-8'))
consulta = '/'.join(reversed(log[0]['consultado_em'][:10].split('-')))
APELIDO = {1: 'Casa da Moeda', 2: 'SESED-RN', 3: 'Marinha-PAPEM', 4: 'UFCA', 5: 'MP-PA', 6: 'INCRA-Serpro', 7: 'TJ-PA', 8: 'MDS', 9: 'SMED-Salvador'}
OBS = {1: 'Pregão com registro de preços. Fora da janela de 13 meses.',
       2: 'Inexigibilidade, sem disputa de preço. Fora da janela de 13 meses.',
       3: 'Pregão. Mesma contratação usada na pesquisa de 2025. Fora da janela de 13 meses.',
       4: 'Pregão.', 5: 'Inexigibilidade, fornecedor exclusivo de solução proprietária.',
       6: 'Dispensa, contratação direta de empresa pública. Outlier pelo teste IQR.',
       7: 'Pregão para fornecimento e implantação de solução; o ponto de função é item acessório.',
       8: 'Pregão.', 9: 'Inexigibilidade, sem disputa de preço.'}
brl = lambda v: ('R$ ' + f"{float(v):,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')) if v not in ('', None) else ''
qtd = lambda v: f"{float(v):,.0f}".replace(',', '.')
dt = lambda s: '/'.join(reversed(s[:10].split('-'))) if s else ''
grupo = {}
for k, g in res['kmeans_2026_atualizado']['atribuicao'].items():
    grupo[int(k)] = f'Grupo {g}'
grupo2 = {}
for g in res['cenarios_detalhe']['C2 - sem outlier IQR | Atualizado ' + res['data_base_ipca']]:
    for item in g['Preços do grupo'].split('; '):
        grupo2[int(item.split(' ')[1])] = g['Grupo'].split(' (')[0]
A = [r for r in rows if r['classificacao'].startswith('AMOSTRA A')]
DOCS = os.path.join(RAIZ, '3. Evidências', 'Documentos PNCP')
def pncp(r):
    pasta = os.path.join(DOCS, f"Ref_{int(r['id']):02d} - {APELIDO[int(r['id'])]} - PF {float(r['preco_unitario_pf']):,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
    info = {'pasta': os.path.relpath(pasta, RAIZ), 'resultado': None, 'registro': None, 'arquivos': [], 'prints': []}
    if os.path.exists(os.path.join(pasta, 'resultado_item.json')):
        res = json.load(open(os.path.join(pasta, 'resultado_item.json'), encoding='utf-8'))
        info['resultado'] = (res or [None])[0]
    if os.path.exists(os.path.join(pasta, '_registro.json')):
        info['registro'] = json.load(open(os.path.join(pasta, '_registro.json'), encoding='utf-8'))
    for raiz_, _, arqs in os.walk(pasta):
        for a in arqs:
            caminho = os.path.relpath(os.path.join(raiz_, a), pasta)
            if a.lower().endswith('.pdf'):
                info['arquivos'].append(caminho)
            if a.lower().endswith('.png') and 'prints' in raiz_:
                info['prints'].append(caminho)
    return info
for r in A:
    i = int(r['id']); p = f"{float(r['preco_unitario_pf']):,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    r['_nome'] = f"Ref_{i:02d} - {APELIDO[i]} - PF {p}"
# ---------------- planilha ----------------
wb = openpyxl.Workbook()
H = PatternFill('solid', fgColor='1F3864'); HF = Font(bold=True, color='FFFFFF', name='Arial', size=10)
borda = Border(*(Side(style='thin', color='BBBBBB'),) * 4)
def folha(ws, cab, linhas, larg, moeda=(), link=(), titulo=None, nota=None):
    l0 = 1
    if titulo:
        ws.cell(1, 1, titulo).font = Font(bold=True, name='Arial', size=12); l0 = 2
        if nota: ws.cell(2, 1, nota).font = Font(italic=True, name='Arial', size=9); l0 = 3
        l0 += 1
    for j, c in enumerate(cab, 1):
        x = ws.cell(l0, j, c); x.fill = H; x.font = HF; x.border = borda
        x.alignment = Alignment(wrap_text=True, vertical='center', horizontal='center')
        ws.column_dimensions[get_column_letter(j)].width = larg[j - 1]
    ws.row_dimensions[l0].height = 42
    for i, lin in enumerate(linhas, l0 + 1):
        for j, v in enumerate(lin, 1):
            x = ws.cell(i, j, v); x.font = Font(name='Arial', size=10); x.border = borda
            x.alignment = Alignment(wrap_text=True, vertical='top')
            if cab[j - 1] in moeda and isinstance(v, (int, float)): x.number_format = 'R$ #,##0.00'
            if cab[j - 1] in link and v: x.hyperlink = v; x.font = Font(name='Arial', size=10, color='0563C1', underline='single')
    ws.freeze_panes = ws.cell(l0 + 1, 1)
ws = wb.active; ws.title = 'Leia-me'
txt = ['MAPA COMPARATIVO DE PREÇOS DO PONTO DE FUNÇÃO - 2026', 'Inventário de Bens Intangíveis - SEPLAG/MT', '',
       f'Fonte: API de Dados Abertos do Compras.gov.br (dadosabertos.compras.gov.br), consultada em {consulta}.',
       'Período das compras: 01/01/2025 a 16/11/2026. Correção monetária: IPCA (série 433 do Banco Central), data-base 10/2026.', '',
       'COMO LER ESTA PLANILHA',
       'Aba 1 - Rastreabilidade Java: os 9 preços que compõem a amostra. Cada linha liga o preço unitário à compra de origem (órgão, processo, número de controle PNCP, links e arquivo de evidência).',
       'Aba 2 - Grupos K-Means: resultado do agrupamento em 3 grupos, em 4 cenários de amostra.',
       'Aba 3 - Outras linguagens: 52 preços em ponto de função de outras tecnologias. Servem para comparação, não compõem o preço.',
       'Aba 4 - Descartes: 31 registros em que a unidade "ponto de função" foi usada para item de outra natureza (mensalidade, sprint, valor global).',
       'Aba 5 - Pesquisa 2025: os 13 preços da pesquisa do ano anterior e a avaliação de reaproveitamento pelo critério de 13 meses.', '',
       'COMO CONFERIR UM PREÇO',
       '1. Na aba 1, clique no link do PNCP da linha. A página da compra traz edital, ata, contrato e demais arquivos.',
       '2. O link do Compras.gov.br abre o acompanhamento da compra, com os itens e os valores homologados.',
       '3. O link da API devolve o registro bruto usado na coleta. A ficha em PDF (pasta 3. Evidências) reproduz esses dados.']
for i, t in enumerate(txt, 1):
    c = ws.cell(i, 1, t); c.font = Font(name='Arial', size=11, bold=t.isupper() and bool(t)); c.alignment = Alignment(wrap_text=True, vertical='top')
ws.column_dimensions['A'].width = 140
ws1 = wb.create_sheet('1 Rastreabilidade Java')
cab = ['Ref.', 'Preço unitário na origem (R$/PF)', 'Quantidade (PF)', 'Data da compra', 'Mês-base', 'Fator IPCA até 10/2026', 'Preço atualizado (R$/PF)',
       'Órgão', 'Unidade compradora (UASG)', 'UF', 'Fornecedor', 'CNPJ do fornecedor', 'Modalidade', 'Registro de preços', 'Nº da compra', 'Processo',
       'Identificador da compra', 'Item', 'Nº de controle PNCP', 'Link PNCP', 'Link Compras.gov.br', 'Link API (registro bruto)', 'Arquivo de evidência',
       'Dentro de 13 meses', 'Houve disputa de preço', 'Grupo K-Means (9 preços)', 'Grupo K-Means (sem outlier)', 'Objeto da compra', 'Observação',
       'Preço homologado no PNCP (R$/PF)', 'Confere com o PNCP', 'Documentos oficiais baixados', 'Páginas com o preço destacado', 'Pasta dos documentos']
lin = [[int(r['id']), float(r['preco_unitario_pf']), float(r['quantidade_pf']), dt(r['data_compra']), r['mes_base_preco'], float(r['fator_ipca']), float(r['preco_atualizado_pf']),
        r['orgao'], f"{r['uasg']} - {r['uasg_nome']}", r['uf'], r['fornecedor'], r['cnpj_fornecedor'], r['modalidade_nome'], r['srp'], r['numero_compra'], r['processo'],
        r['id_compra'], int(r['item']), r['numero_controle_pncp'], r['link_pncp'], r['link_compras_gov'], r['link_api_item'], f"3. Evidências/Fichas/{r['_nome']}.pdf",
        r['dentro_13_meses'], r['disputa_de_preco'], grupo.get(int(r['id']), ''), grupo2.get(int(r['id']), 'Excluído (outlier)'), r['objeto'], OBS[int(r['id'])],
        *(lambda i: [float(i['resultado']['valorUnitarioHomologado']) if i['resultado'] else '',
                     ('Sim' if i['resultado'] and abs(float(i['resultado']['valorUnitarioHomologado']) - float(r['preco_unitario_pf'])) < 0.005 else 'Não conferido'),
                     len(i['arquivos']), len(i['prints']), i['pasta']])(pncp(r))] for r in A]
folha(ws1, cab, lin, [6, 14, 11, 12, 10, 11, 14, 30, 34, 5, 32, 17, 18, 10, 10, 22, 20, 6, 28, 30, 30, 30, 36, 10, 10, 20, 20, 60, 46, 14, 12, 12, 12, 40],
      moeda=('Preço unitário na origem (R$/PF)', 'Preço atualizado (R$/PF)', 'Preço homologado no PNCP (R$/PF)'), link=('Link PNCP', 'Link Compras.gov.br', 'Link API (registro bruto)'),
      titulo='Rastreabilidade dos 9 preços Java medidos em ponto de função', nota='Do preço unitário até a compra de origem. Preço atualizado = preço na origem x fator IPCA.')
CFG = json.load(open(f'{RAIZ}/config_pesquisa.json', encoding='utf-8'))['contrato_referencia']
wsc = wb.create_sheet('0 Contrato 014-2022')
folha(wsc, ['Ato', 'Preço por PF (R$)', 'Referência'], [[h['ato'], h['preco_pf'], h['referencia']] for h in CFG['historico']], [34, 16, 40],
      moeda=('Preço por PF (R$)',), titulo='Objeto de referência: Contrato nº 014/2022/SEPLAG',
      nota=f"{CFG['origem']}. Preço vigente: R$ {CFG['preco_vigente_pf']:.2f} ({CFG['ato_vigente']}, processo {CFG['processo_ato_vigente']}).".replace('.', ',', 0))
ws2 = wb.create_sheet('2 Grupos K-Means')
cab = ['Cenário', 'Base de preços', 'Grupo', 'Qtde no grupo', 'Preços do grupo', 'Mínimo', 'Mediana', 'Centroide (média)', 'Máximo']
lin = []
for nome, grupos in res['cenarios_detalhe'].items():
    cen, base = nome.split(' | ')
    for g in grupos:
        lin.append([cen, base, g['Grupo'], g['Qtde de preços'], g['Preços do grupo'], g['Mínimo'], g['Mediana'], g['Centroide (média)'], g['Máximo']])
folha(ws2, cab, lin, [32, 18, 24, 9, 70, 13, 13, 15, 13], moeda=('Mínimo', 'Mediana', 'Centroide (média)', 'Máximo'),
      titulo='Agrupamento K-Means em 3 grupos: preços originais e atualizados, em cada cenário', nota='Fonte: notebook Analise_Precos_PF-2026.ipynb (pasta 5. Análise Estatística).')
def simples(nome, cls, titulo, nota):
    w = wb.create_sheet(nome)
    cab = ['Ref.', 'Preço unitário (R$/PF)', 'Quantidade (PF)', 'Data da compra', 'Preço atualizado (R$/PF)', 'Tecnologia (CatSer)', 'Órgão / unidade', 'UF', 'Fornecedor', 'Modalidade',
           'Nº de controle PNCP', 'Link PNCP', 'Link Compras.gov.br', 'Descrição do item', 'Motivo da classificação']
    lin = [[int(r['id']), float(r['preco_unitario_pf']), float(r['quantidade_pf']), dt(r['data_compra']), float(r['preco_atualizado_pf']), f"{r['catser']} - {r['catser_nome']}",
            r['uasg_nome'], r['uf'], r['fornecedor'], r.get('modalidade_nome', ''), r.get('numero_controle_pncp', ''), r.get('link_pncp', ''), r['link_compras_gov'], r['descricao_item'], r['motivo']]
           for r in rows if r['classificacao'] == cls]
    folha(w, cab, lin, [6, 14, 11, 12, 14, 40, 36, 5, 32, 18, 28, 30, 30, 50, 50], moeda=('Preço unitário (R$/PF)', 'Preço atualizado (R$/PF)'), link=('Link PNCP', 'Link Compras.gov.br'), titulo=titulo, nota=nota)
simples('3 Outras linguagens', 'AMOSTRA B - AMPLIADA', 'Preços em ponto de função de outras tecnologias (comparação)', 'Não compõem o preço de referência.')
simples('4 Descartes', 'DESCARTE SUGERIDO', 'Registros descartados', 'Quantidade inferior a 100 PF, ou preço abaixo de R$ 100,00 ou acima de R$ 3.000,00.')
ws5 = wb.create_sheet('5 Pesquisa 2025')
cab = ['Nº', 'Fonte na pesquisa de 2025', 'Preço (R$/PF)', 'Data de referência', 'Meses até 16/11/2026', 'Dentro de 13 meses', 'Avaliação para 2026']
p25 = [('Banco de Preços - Contratação 1 (menor preço) - Marinha', 1060.00, '08/2025', 15, 'Não', 'Já consta da amostra de 2026 como Ref. 3, obtida da fonte oficial.'),
       ('Banco de Preços - Contratação 2 (mediana das 3 melhores propostas)', 650.00, 'não identificada', None, 'Verificar', 'Data não consta dos arquivos de 2025. Reaproveitar só se a compra for posterior a 10/2025.'),
       ('Banco de Preços - Contratação 3 (média saneada TCU)', 1182.09, 'não identificada', None, 'Verificar', 'Idem.'),
       ('ARP 33/2024 MGI, item 35 (apostilamento 06/2024)', 943.26, '09/2024', 26, 'Não', 'Fora da janela.'),
       ('ARP 32/2024 MGI, item 42 (apostilamento 05/2024)', 558.61, '09/2024', 26, 'Não', 'Fora da janela.'),
       ('ARP 31/2024 MGI, item 22 (apostilamento 01/2025)', 585.21, '09/2024', 26, 'Não', 'Fora da janela.'),
       ('ARP 30/2024 MGI, item 8 (apostilamento 04/2024)', 638.41, '09/2024', 26, 'Não', 'Fora da janela.'),
       ('ARP 29/2024 MGI, item 1 (apostilamento 03/2024)', 601.33, '09/2024', 26, 'Não', 'Fora da janela.'),
       ('Contrato 14/2024 - Serviço Florestal Brasileiro', 886.51, '08/2024', 27, 'Não', 'Fora da janela. Admissível apenas se comprovada a execução vigente e o preço reajustado.'),
       ('Contrato 024/2024 - ANTT', 886.51, '10/2024', 25, 'Não', 'Idem. Mesmo preço da ARP 33/2024: contar uma única vez.'),
       ('Contrato 21/2024 - SUFRAMA', 707.64, '09/2024', 26, 'Não', 'Fora da janela. Admissível apenas se comprovada a execução vigente e o preço reajustado.'),
       ('Contrato 45/2024 - ICMBio', 886.51, '09/2024', 26, 'Não', 'Idem. Mesmo preço da ARP 33/2024: contar uma única vez.'),
       ('Contrato 014/2022/SEPLAG (4º apostilamento)', 519.99, '05/2025', 18, 'Não', 'Contrato da própria SEPLAG. Usar como referência de comparação. Atualizar se houve reajuste em 2026.')]
folha(ws5, cab, [[i, *x] for i, x in enumerate(p25, 1)], [5, 58, 13, 16, 12, 12, 80], moeda=('Preço (R$/PF)',),
      titulo='Preços da pesquisa de 2025 e reaproveitamento em 2026', nota='Critério informado pela presidência: aproveitar preços com até 13 meses na data da pesquisa (a partir de 10/2025).')
wb.save(f'{RAIZ}/4. Mapa Comparativo/Mapa_Comparativo_Precos_PF_2026.xlsx')
# ---------------- fichas ----------------
css = """<style>@page{size:A4;margin:16mm}body{font-family:Arial,Helvetica,sans-serif;font-size:10pt;color:#111;margin:0;padding:18px;background:#fff}
h1{font-size:14pt;margin:0 0 2pt}h2{font-size:11pt;margin:12pt 0 4pt;border-bottom:1px solid #999}.sub{color:#444;font-size:9.5pt;margin-bottom:8pt}
table{border-collapse:collapse;width:100%}td,th{border:1px solid #bbb;padding:4pt 6pt;vertical-align:top;text-align:left}th{background:#eee;width:30%}
.p{font-size:15pt;font-weight:bold}a{color:#0b4f9e;word-break:break-all}.n{font-size:8.5pt;color:#444;margin-top:10pt}
.flow td{text-align:center;font-size:9pt;background:#f4f7fb}.flow b{display:block;font-size:10pt}</style>"""
L = lambda u: f'<a href="{html.escape(u)}">{html.escape(u)}</a>' if u else ''
os.makedirs('_fichas_html', exist_ok=True)
for r in A:
    i = int(r['id'])
    info = pncp(r); hr = info['resultado']
    eventos = (info['registro'] or {}).get('eventos', [])
    ev = next((e for e in eventos if 'resultados' in e.get('consulta', '')), {})
    if hr:
        confere = abs(float(hr['valorUnitarioHomologado']) - float(r['preco_unitario_pf'])) < 0.005
        conf = (f"<tr><th>Preço unitário homologado no PNCP</th><td class='p'>{brl(hr['valorUnitarioHomologado'])} "
                f"{'(confere com o mapa)' if confere else '(DIVERGE do mapa)'}</td></tr>"
                f"<tr><th>Quantidade e valor total homologados</th><td>{qtd(hr['quantidadeHomologada'])} PF / {brl(hr['valorTotalHomologado'])}</td></tr>"
                f"<tr><th>Fornecedor homologado</th><td>{html.escape(hr['nomeRazaoSocialFornecedor'])} - CNPJ {hr['niFornecedor']}</td></tr>"
                f"<tr><th>Data do resultado / situação</th><td>{dt(hr.get('dataResultado') or '')} / {html.escape(str(hr.get('situacaoCompraItemResultadoNome', '')))}</td></tr>"
                f"<tr><th>Consulta à API do PNCP</th><td>{L(ev.get('consulta', ''))}<br>em {ev.get('em', '')[:19].replace('T', ' ')} (UTC)</td></tr>"
                f"<tr><th>Documentos oficiais baixados</th><td>{len(info['arquivos'])} arquivo(s) PDF; {len(info['prints'])} página(s) com o preço destacado.<br>Pasta: {html.escape(info['pasta'])}</td></tr>")
    else:
        conf = '<tr><th>Resultado no PNCP</th><td>Ainda não coletado. Executar 3. Evidências/coleta_documentos_pncp.py</td></tr>'
    h = f"""<html><head><meta charset="utf-8"><title>{r['_nome']}</title>{css}</head><body>
<h1>Referência de preço nº {i:02d} - Ponto de Função</h1>
<div class="sub">Inventário de Bens Intangíveis 2026 - SEPLAG/MT - Mapa Comparativo de Preços</div>
<h2>Rastreabilidade do preço</h2>
<table class="flow"><tr><td><b>1. Compra de origem</b>{html.escape(r['modalidade_nome'])} nº {r['numero_compra']}<br>{html.escape(r['uasg_nome'])}</td>
<td><b>2. Item homologado</b>Item {r['item']}, CatSer {r['catser']}<br>{qtd(r['quantidade_pf'])} PF</td>
<td><b>3. Preço unitário na origem</b>{brl(r['preco_unitario_pf'])}<br>em {r['mes_base_preco']}</td>
<td><b>4. Correção pelo IPCA</b>fator {float(r['fator_ipca']):.6f}<br>até {r['data_base_atualizacao']}</td>
<td><b>5. Preço usado na análise</b><span class="p">{brl(r['preco_atualizado_pf'])}</span></td></tr></table>
<h2>Item</h2><table>
<tr><th>Preço unitário homologado</th><td class="p">{brl(r['preco_unitario_pf'])} por ponto de função</td></tr>
<tr><th>Quantidade</th><td>{qtd(r['quantidade_pf'])} PF</td></tr>
<tr><th>Item do catálogo (CatSer)</th><td>{r['catser']} - {html.escape(r['catser_nome'])}</td></tr>
<tr><th>Descrição do item</th><td>{html.escape(r['descricao_item'])}</td></tr></table>
<h2>Contratação</h2><table>
<tr><th>Órgão</th><td>{html.escape(r['orgao'])}</td></tr>
<tr><th>Unidade compradora (UASG)</th><td>{r['uasg']} - {html.escape(r['uasg_nome'])} - {r['uf']}</td></tr>
<tr><th>Modalidade</th><td>{html.escape(r['modalidade_nome'])} nº {r['numero_compra']}. Registro de preços: {r['srp']}. Disputa de preço: {r['disputa_de_preco']}</td></tr>
<tr><th>Amparo legal</th><td>{html.escape(r['amparo_legal'])}</td></tr>
<tr><th>Processo</th><td>{html.escape(r['processo'])}</td></tr>
<tr><th>Objeto</th><td>{html.escape(r['objeto'])}</td></tr>
<tr><th>Fornecedor</th><td>{html.escape(r['fornecedor'])} - CNPJ {r['cnpj_fornecedor']}</td></tr>
<tr><th>Data da compra / do resultado</th><td>{dt(r['data_compra'])} / {dt(r['data_resultado'])}</td></tr>
<tr><th>Valor total homologado da compra</th><td>{brl(r['valor_total_homologado'])}</td></tr></table>
<h2>Identificadores e links da origem</h2><table>
<tr><th>Número de controle PNCP</th><td>{r['numero_controle_pncp']}</td></tr>
<tr><th>Identificador da compra / item</th><td>{r['id_compra']} / item {r['item']}</td></tr>
<tr><th>PNCP (edital, ata, contrato e arquivos)</th><td>{L(r['link_pncp'])}</td></tr>
<tr><th>Compras.gov.br (itens e valores homologados)</th><td>{L(r['link_compras_gov'])}</td></tr>
<tr><th>API de dados abertos (registro bruto)</th><td>{L(r['link_api_item'])}</td></tr></table>
<h2>Conferência no PNCP (fonte oficial)</h2><table>
{conf}
</table>
<h2>Enquadramento na pesquisa</h2><table>
<tr><th>Observação</th><td>{html.escape(OBS[i])}</td></tr>
<tr><th>Dentro de 13 meses da pesquisa</th><td>{r['dentro_13_meses']} ({r['meses_ate_pesquisa']} meses)</td></tr>
<tr><th>Grupo K-Means (9 preços / sem outlier)</th><td>{grupo.get(i, '')} / {grupo2.get(i, 'Excluído (outlier)')}</td></tr></table>
<p class="n">Ficha gerada pela Comissão de Inventário e Avaliação de Bens Intangíveis da SEPLAG/MT a partir do retorno da API oficial de Dados Abertos do Compras.gov.br,
consultada em {consulta}. Reproduz os dados públicos do resultado da compra. Não substitui o edital, a ata de registro de preços ou o contrato, que devem ser obtidos no PNCP pelo link indicado.</p>
</body></html>"""
    open(f"_fichas_html/{r['_nome']}.html", 'w', encoding='utf-8').write(h)
for r in rows:
    r['evidencia_ficha'] = ''
for r in A:
    r['evidencia_ficha'] = f"3. Evidências/Fichas/{r['_nome']}.pdf"
campos = [k for k in rows[0] if not k.startswith('_')]
w = csv.DictWriter(open(f'{RAIZ}/4. Mapa Comparativo/Precos_Ponto_Funcao_2025-2026.csv', 'w', newline='', encoding='utf-8-sig'), fieldnames=campos, delimiter=';', lineterminator='\n', extrasaction='ignore')
w.writeheader(); w.writerows(rows)
print('planilha e', len(A), 'fichas geradas')

# ---------------- PDF e imagem de cada ficha (Playwright/Chromium) ----------------
import shutil
from pathlib import Path
from playwright.sync_api import sync_playwright
destino_pdf = Path(RAIZ) / '3. Evidências' / 'Fichas'
destino_png = Path(RAIZ) / '3. Evidências' / 'Prints'
destino_pdf.mkdir(parents=True, exist_ok=True); destino_png.mkdir(parents=True, exist_ok=True)
for antigo in list(destino_pdf.glob('Ref_*.pdf')) + list(destino_png.glob('Ref_*.png')):
    antigo.unlink()
with sync_playwright() as pw:
    nav = pw.chromium.launch()
    pg = nav.new_context(viewport={'width': 1000, 'height': 1300}, device_scale_factor=2).new_page()
    for h in sorted(Path('_fichas_html').glob('*.html')):
        pg.goto(h.resolve().as_uri())
        pg.pdf(path=str(destino_pdf / (h.stem + '.pdf')), prefer_css_page_size=True, print_background=True)
        pg.screenshot(path=str(destino_png / (h.stem + '.png')), full_page=True)
    nav.close()
shutil.rmtree('_fichas_html')
print('fichas em PDF e PNG gravadas em 3. Evidências')
