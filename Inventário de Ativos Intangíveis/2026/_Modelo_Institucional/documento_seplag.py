"""Modelo institucional de documentos técnicos da CPPTI/SEPLAG-MT.

Reproduz o padrão visual do "Relatório Técnico de APF" (2026): faixa azul com o logo SEPLAG / Governo de Mato Grosso,
títulos de seção com barra verde e ícone, caixas de destaque (informação, atenção, conclusão), cartões de indicador,
figuras emolduradas com legenda e rodapé com documento, página, setor e data de geração.

O mesmo conteúdo é gerado em três formatos:
    HTML  visual de referência (abre no navegador)
    PDF   impresso a partir do HTML pelo Chromium (Playwright)
    DOCX  versão editável no Word, com a mesma estrutura e cores

Uso:
    from documento_seplag import Documento
    d = Documento('MANIFESTAÇÃO TÉCNICA', ['Linha 1', 'Linha 2'], nome_arquivo='Manifestacao', setor='...')
    d.p('Texto com **negrito** e *itálico*.')
    d.secao('📊', '1. TÍTULO')
    d.caixa('info', 'Título:', 'Texto.')
    d.tabela(['Coluna A', 'Coluna B'], [['1', '2']], legenda='Tabela 1 - ...', numericas=[1])
    d.figura('grafico.png', 'Figura 1 - ...')
    d.salvar('pasta/Manifestacao')      # gera .html, .pdf e .docx
"""
import base64, datetime, html, mimetypes, re
from pathlib import Path

AQUI = Path(__file__).resolve().parent
LOGO = AQUI / 'logo_seplag_governo_mt.png'
FONTES = AQUI / 'fontes'

AZUL, AZUL2, VERDE, CINZA = '#0b3d91', '#1257b8', '#1e8e3e', '#5f6b7a'
CAIXAS = {
    'info': {'borda': '#0b3d91', 'fundo': '#ffffff', 'contorno': '#d9e1ec'},
    'atencao': {'borda': '#e0b100', 'fundo': '#fffbea', 'contorno': '#f1d877'},
    'conclusao': {'borda': '#1e8e3e', 'fundo': '#effaf3', 'contorno': '#bfe5cb'},
    'alerta': {'borda': '#c62828', 'fundo': '#fdf1f1', 'contorno': '#f1c0c0'},
}


def _b64(caminho):
    tipo = mimetypes.guess_type(str(caminho))[0] or 'application/octet-stream'
    return f'data:{tipo};base64,' + base64.b64encode(Path(caminho).read_bytes()).decode()


def _inline_html(texto):
    t = html.escape(texto)
    t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'(?<!\*)\*(?!\s)(.+?)(?<!\s)\*(?!\*)', r'<em>\1</em>', t)
    t = re.sub(r'\[([^\]]+)\]\((https?://[^)]+)\)', r'<a href="\2">\1</a>', t)
    t = re.sub(r'`([^`]+)`', r'<span class="pasta">\1</span>', t)
    return t.replace('\n', '<br>')


def _partes(texto):
    """Divide o texto em trechos (texto, negrito, itálico, link) para o Word."""
    padrao = re.compile(r'(\*\*.+?\*\*|(?<!\*)\*(?!\s).+?(?<!\s)\*(?!\*)|\[[^\]]+\]\(https?://[^)]+\))')
    saida = []
    texto = texto.replace('`', '')
    for pedaco in padrao.split(texto):
        if not pedaco:
            continue
        if pedaco.startswith('**'):
            saida.append((pedaco[2:-2], 'b', None))
        elif re.fullmatch(r'\[[^\]]+\]\(https?://[^)]+\)', pedaco):
            m = re.match(r'\[([^\]]+)\]\((.+)\)', pedaco)
            saida.append((m.group(1), 'a', m.group(2)))
        elif pedaco.startswith('*'):
            saida.append((pedaco[1:-1], 'i', None))
        else:
            saida.append((pedaco, '', None))
    return saida


class Documento:
    def __init__(self, titulo, subtitulos, nome_arquivo, setor='Coordenadoria de Planejamento e Projetos de TI (CPPTI/SEPLAG)',
                 cidade_data=None):
        self.titulo, self.subtitulos, self.nome_arquivo, self.setor = titulo, subtitulos, nome_arquivo, setor
        self.cidade_data = cidade_data
        self.blocos = []
        self.gerado_em = datetime.datetime.now()

    # ---------- conteúdo ----------
    def p(self, texto, alinhar='justify'):
        self.blocos.append(('p', texto, alinhar))

    def secao(self, icone, titulo):
        self.blocos.append(('secao', icone, titulo))

    def subsecao(self, titulo):
        self.blocos.append(('subsecao', titulo))

    def caixa(self, tipo, titulo, *paragrafos):
        self.blocos.append(('caixa', tipo, titulo, paragrafos))

    def cards(self, itens):
        """itens: lista de (rótulo, valor, complemento opcional)."""
        self.blocos.append(('cards', itens))

    def tabela(self, cabecalho, linhas, legenda=None, numericas=(), larguras=None, destaque_linhas=(), fonte=None):
        self.blocos.append(('tabela', cabecalho, linhas, legenda, set(numericas), larguras, set(destaque_linhas), fonte))

    def figura(self, caminho, legenda, largura_cm=16):
        self.blocos.append(('figura', Path(caminho), legenda, largura_cm))

    def lista(self, itens, numerada=False):
        self.blocos.append(('lista', itens, numerada))

    def quebra(self):
        self.blocos.append(('quebra',))

    def assinatura(self, rotulo, nome, *linhas):
        self.blocos.append(('assinatura', rotulo, nome, linhas))

    # ---------- HTML / PDF ----------
    def html(self):
        f = lambda n: _b64(FONTES / n) if (FONTES / n).exists() else ''
        fontes = ''.join(f"@font-face{{font-family:'Open Sans';src:url({f(n)}) format('woff2');font-weight:{w};font-style:{s}}}"
                         for n, w, s in [('open-sans-latin-400-normal.woff2', 400, 'normal'), ('open-sans-latin-600-normal.woff2', 600, 'normal'),
                                         ('open-sans-latin-700-normal.woff2', 700, 'normal'), ('open-sans-latin-400-italic.woff2', 400, 'italic')])
        css = f"""{fontes}
@page {{ size: A4; margin: 14mm 0 16mm 0; }}
* {{ box-sizing: border-box; }}
html {{ background: #eef2f7; }}
body {{ font-family: 'Open Sans', 'Segoe UI', Arial, sans-serif; font-size: 10pt; color: #1f2937; line-height: 1.55; margin: 0; }}
.folha {{ max-width: 210mm; margin: 0 auto; background: #fff; padding: 0 0 8mm 0; }}
.topo {{ background: linear-gradient(135deg, {AZUL} 0%, {AZUL2} 100%); padding: 7mm 9mm; display: flex; align-items: center; justify-content: space-between; gap: 6mm; }}
.topo img {{ height: 23mm; background: #fff; padding: 1.5mm 2.5mm; border-radius: 1mm; }}
.topo .t {{ text-align: right; color: #fff; }}
.topo .t h1 {{ font-size: 13pt; margin: 0 0 1.5mm 0; letter-spacing: .4px; font-weight: 700; }}
.topo .t div {{ font-size: 8.3pt; font-weight: 600; opacity: .95; }}
.corpo {{ padding: 6mm 18mm 0 18mm; }}
p {{ margin: 0 0 3mm 0; text-align: justify; }}
.data {{ text-align: right; color: {CINZA}; font-size: 9pt; }}
h2 {{ font-size: 10.5pt; color: {AZUL}; background: #f3f5f8; border-left: 5px solid {VERDE}; padding: 2.2mm 3.5mm; margin: 7mm 0 3.5mm 0; text-transform: uppercase; font-weight: 700; break-after: avoid; }}
h3 {{ font-size: 10pt; color: {AZUL}; margin: 5mm 0 2mm 0; font-weight: 700; break-after: avoid; }}
.caixa {{ border: 1px solid; border-left-width: 5px; border-radius: 2.5mm; padding: 3.5mm 4.5mm; margin: 3.5mm 0 4.5mm 0; break-inside: avoid; }}
.caixa p:last-child {{ margin-bottom: 0; }}
.cards {{ display: flex; gap: 4mm; margin: 4mm 0 5mm 0; break-inside: avoid; }}
.card {{ flex: 1; border: 1.3px solid #1f2937; border-radius: 2.5mm; padding: 3mm 3mm 3.5mm 3mm; text-align: center; }}
.card .r {{ font-size: 6.8pt; text-transform: uppercase; color: {CINZA}; letter-spacing: .3px; }}
.card .v {{ font-size: 15pt; font-weight: 700; color: {AZUL}; line-height: 1.25; margin-top: 1mm; }}
.card .c {{ font-size: 7.6pt; color: {CINZA}; margin-top: .8mm; }}
table {{ width: 100%; border-collapse: collapse; font-size: 8.4pt; margin: 2mm 0 1.5mm 0; break-inside: auto; }}
thead {{ display: table-header-group; }}
tr {{ break-inside: avoid; }}
th {{ background: {AZUL}; color: #fff; font-weight: 600; padding: 1.8mm 2mm; text-align: left; vertical-align: bottom; }}
td {{ padding: 1.6mm 2mm; border-bottom: 1px solid #e3e8ef; vertical-align: top; }}
tbody tr:nth-child(even) td {{ background: #f7f9fc; }}
tr.dest td {{ background: #fff6d6 !important; font-weight: 600; }}
td.n, th.n {{ text-align: right; white-space: nowrap; }}
.leg {{ font-size: 8pt; font-style: italic; color: {CINZA}; text-align: center; margin: 1mm 0 4.5mm 0; }}
.fonte {{ font-size: 7.5pt; color: {CINZA}; margin: -3mm 0 4.5mm 0; }}
figure {{ border: 1px solid #d9e1ec; border-radius: 2.5mm; padding: 3mm; margin: 3.5mm 0 4.5mm 0; text-align: center; break-inside: avoid; }}
figure img {{ max-width: 100%; }}
figcaption {{ font-size: 8pt; font-style: italic; color: {CINZA}; margin-top: 1.5mm; }}
ul, ol {{ margin: 0 0 3mm 0; padding-left: 6mm; }}
li {{ margin-bottom: 1.4mm; text-align: justify; }}
.assin {{ margin-top: 9mm; break-inside: avoid; }}
.assin .nome {{ font-weight: 700; margin-top: 4mm; }}
.quebra {{ break-after: page; }}
a {{ color: {AZUL2}; word-break: break-all; }}
.pasta {{ font-family: Consolas, 'Courier New', monospace; font-size: 8.8pt; background: #f1f4f8; padding: 0 1mm; border-radius: 1mm; }}
@media print {{ html {{ background: #fff; }} .folha {{ max-width: none; }} }}
"""
        h = [f'<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>{html.escape(self.nome_arquivo)}</title><style>{css}</style></head><body><div class="folha">',
             f'<div class="topo"><img src="{_b64(LOGO)}" alt="SEPLAG - Governo de Mato Grosso"><div class="t"><h1>{html.escape(self.titulo)}</h1>'
             + ''.join(f'<div>{html.escape(s)}</div>' for s in self.subtitulos) + '</div></div><div class="corpo">']
        if self.cidade_data:
            h.append(f'<p class="data">{html.escape(self.cidade_data)}</p>')
        for b in self.blocos:
            k = b[0]
            if k == 'p':
                h.append(f'<p style="text-align:{b[2]}">{_inline_html(b[1])}</p>')
            elif k == 'secao':
                h.append(f'<h2>{b[1]} {html.escape(b[2])}</h2>')
            elif k == 'subsecao':
                h.append(f'<h3>{html.escape(b[1])}</h3>')
            elif k == 'caixa':
                c = CAIXAS[b[1]]
                corpo = ''.join(f'<p>{"<strong>" + html.escape(b[2]) + "</strong> " if i == 0 and b[2] else ""}{_inline_html(t)}</p>' for i, t in enumerate(b[3]))
                h.append(f'<div class="caixa" style="background:{c["fundo"]};border-color:{c["contorno"]};border-left-color:{c["borda"]}">{corpo}</div>')
            elif k == 'cards':
                h.append('<div class="cards">' + ''.join(
                    f'<div class="card"><div class="r">{html.escape(i[0])}</div><div class="v">{html.escape(i[1])}</div>'
                    + (f'<div class="c">{html.escape(i[2])}</div>' if len(i) > 2 and i[2] else '') + '</div>' for i in b[1]) + '</div>')
            elif k == 'tabela':
                _, cab, linhas, leg, num, larg, dest, fonte = b
                col = ''.join(f'<col style="width:{w}%">' for w in larg) if larg else ''
                th = ''.join(f'<th class="{"n" if j in num else ""}">{html.escape(c)}</th>' for j, c in enumerate(cab))
                tr = ''.join(f'<tr class="{"dest" if i in dest else ""}">' + ''.join(
                    f'<td class="{"n" if j in num else ""}">{_inline_html(str(v))}</td>' for j, v in enumerate(l)) + '</tr>' for i, l in enumerate(linhas))
                h.append(f'<table><colgroup>{col}</colgroup><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table>')
                if leg:
                    h.append(f'<div class="leg">{html.escape(leg)}</div>')
                if fonte:
                    h.append(f'<div class="fonte">{_inline_html(fonte)}</div>')
            elif k == 'figura':
                h.append(f'<figure><img src="{_b64(b[1])}" alt=""><figcaption>{html.escape(b[2])}</figcaption></figure>')
            elif k == 'lista':
                tag = 'ol' if b[2] else 'ul'
                h.append(f'<{tag}>' + ''.join(f'<li>{_inline_html(i)}</li>' for i in b[1]) + f'</{tag}>')
            elif k == 'quebra':
                h.append('<div class="quebra"></div>')
            elif k == 'assinatura':
                h.append(f'<div class="assin"><div>{html.escape(b[1])}</div><div class="nome">{html.escape(b[2])}</div>'
                         + ''.join(f'<div>{html.escape(x)}</div>' for x in b[3]) + '</div>')
        h.append('</div></div></body></html>')
        return ''.join(h)

    def _rodape_pdf(self):
        g = self.gerado_em.strftime('%d/%m/%Y às %H:%M')
        return (f'<div style="width:100%;font-family:Arial,sans-serif;font-size:6.5pt;color:#8a94a3;padding:0 18mm;display:flex;justify-content:space-between;">'
                f'<div><b>Documento:</b> {html.escape(self.nome_arquivo)} | <b>Página:</b> <span class="pageNumber"></span> de <span class="totalPages"></span><br>'
                f'<b>Setor:</b> {html.escape(self.setor)}</div><div style="text-align:right"><b>Gerado em:</b> {g}</div></div>')

    def salvar_pdf(self, caminho_html, caminho_pdf):
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            nav = pw.chromium.launch()
            pg = nav.new_page()
            pg.goto(Path(caminho_html).resolve().as_uri())
            pg.wait_for_timeout(400)
            pg.pdf(path=str(caminho_pdf), format='A4', print_background=True, display_header_footer=True,
                   header_template='<div></div>', footer_template=self._rodape_pdf(),
                   margin={'top': '12mm', 'bottom': '18mm', 'left': '0', 'right': '0'})
            nav.close()

    # ---------- DOCX ----------
    def salvar_docx(self, caminho):
        from docx import Document as Docx
        from docx.enum.section import WD_ORIENT
        from docx.enum.table import WD_TABLE_ALIGNMENT
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        from docx.oxml import OxmlElement
        from docx.oxml.ns import qn
        from docx.shared import Cm, Pt, RGBColor

        FONTE = 'Segoe UI'
        rgb = lambda h: RGBColor.from_string(h.lstrip('#').upper())

        def sombra(celula_ou_par, cor, par=False):
            el = celula_ou_par._p.get_or_add_pPr() if par else celula_ou_par._tc.get_or_add_tcPr()
            s = OxmlElement('w:shd'); s.set(qn('w:val'), 'clear'); s.set(qn('w:color'), 'auto'); s.set(qn('w:fill'), cor.lstrip('#'))
            el.append(s)

        def bordas_celula(celula, cores):
            tcPr = celula._tc.get_or_add_tcPr(); b = OxmlElement('w:tcBorders')
            for lado, (cor, sz) in cores.items():
                e = OxmlElement(f'w:{lado}'); e.set(qn('w:val'), 'single' if sz else 'nil'); e.set(qn('w:sz'), str(sz)); e.set(qn('w:color'), cor.lstrip('#'))
                b.append(e)
            tcPr.append(b)

        def borda_par(par, lado, cor, sz):
            pPr = par._p.get_or_add_pPr(); b = pPr.find(qn('w:pBdr'))
            if b is None:
                b = OxmlElement('w:pBdr'); pPr.append(b)
            e = OxmlElement(f'w:{lado}'); e.set(qn('w:val'), 'single'); e.set(qn('w:sz'), str(sz)); e.set(qn('w:space'), '6'); e.set(qn('w:color'), cor.lstrip('#'))
            b.append(e)

        def link(par, texto, url):
            r_id = par.part.relate_to(url, 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink', is_external=True)
            hl = OxmlElement('w:hyperlink'); hl.set(qn('r:id'), r_id)
            r = OxmlElement('w:r'); rPr = OxmlElement('w:rPr')
            c = OxmlElement('w:color'); c.set(qn('w:val'), '1257B8'); rPr.append(c)
            u = OxmlElement('w:u'); u.set(qn('w:val'), 'single'); rPr.append(u)
            r.append(rPr); t = OxmlElement('w:t'); t.text = texto; t.set(qn('xml:space'), 'preserve'); r.append(t); hl.append(r)
            par._p.append(hl)

        def escreve(par, texto, tam=10, cor=None, negrito=False, italico=False):
            for t, estilo, url in _partes(texto):
                if estilo == 'a':
                    link(par, t, url); continue
                r = par.add_run(t); r.font.size = Pt(tam); r.font.name = FONTE
                r.bold = negrito or estilo == 'b'; r.italic = italico or estilo == 'i'
                if cor: r.font.color.rgb = rgb(cor)
            return par

        def espaco(par, antes=0, depois=4, linha=1.15):
            pf = par.paragraph_format; pf.space_before = Pt(antes); pf.space_after = Pt(depois); pf.line_spacing = linha

        doc = Docx()
        st = doc.styles['Normal']; st.font.name = FONTE; st.font.size = Pt(10)
        st.element.rPr.rFonts.set(qn('w:eastAsia'), FONTE)
        sec = doc.sections[0]
        sec.page_width, sec.page_height = Cm(21), Cm(29.7)
        sec.left_margin = sec.right_margin = Cm(2); sec.top_margin = Cm(1.5); sec.bottom_margin = Cm(1.8)
        largura = 17.0

        # rodapé com página
        rp = sec.footer.paragraphs[0]
        escreve(rp, f'Documento: {self.nome_arquivo} | Setor: {self.setor} | Gerado em: {self.gerado_em:%d/%m/%Y às %H:%M} | Página ', 7, '#8A94A3')
        for campo in ('PAGE', ' de ', 'NUMPAGES'):
            if campo == ' de ':
                escreve(rp, ' de ', 7, '#8A94A3'); continue
            r = rp.add_run(); r.font.size = Pt(7)
            for tipo, txt in (('begin', None), (None, campo), ('end', None)):
                if tipo:
                    e = OxmlElement('w:fldChar'); e.set(qn('w:fldCharType'), tipo); r._r.append(e)
                else:
                    e = OxmlElement('w:instrText'); e.set(qn('xml:space'), 'preserve'); e.text = txt; r._r.append(e)

        # faixa de topo
        t = doc.add_table(rows=1, cols=2); t.alignment = WD_TABLE_ALIGNMENT.CENTER; t.autofit = False
        t.columns[0].width = Cm(7); t.columns[1].width = Cm(largura - 7)
        for c in t.rows[0].cells:
            sombra(c, AZUL); bordas_celula(c, {x: ('#FFFFFF', 0) for x in ('top', 'left', 'bottom', 'right')})
        c0, c1 = t.rows[0].cells
        c0.width, c1.width = Cm(7), Cm(largura - 7)
        p0 = c0.paragraphs[0]; espaco(p0, 6, 6); p0.add_run().add_picture(str(LOGO), width=Cm(6.2))
        p1 = c1.paragraphs[0]; p1.alignment = WD_ALIGN_PARAGRAPH.RIGHT; espaco(p1, 8, 2)
        escreve(p1, self.titulo, 12.5, '#FFFFFF', negrito=True)
        for s in self.subtitulos:
            q = c1.add_paragraph(); q.alignment = WD_ALIGN_PARAGRAPH.RIGHT; espaco(q, 0, 1); escreve(q, s, 8, '#FFFFFF', negrito=True)

        if self.cidade_data:
            q = doc.add_paragraph(); q.alignment = WD_ALIGN_PARAGRAPH.RIGHT; espaco(q, 8, 4); escreve(q, self.cidade_data, 9, CINZA)

        n_fig = 0
        for b in self.blocos:
            k = b[0]
            if k == 'p':
                q = doc.add_paragraph(); q.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY if b[2] == 'justify' else WD_ALIGN_PARAGRAPH.LEFT
                espaco(q, 0, 6); escreve(q, b[1])
            elif k == 'secao':
                q = doc.add_paragraph(); espaco(q, 14, 6); sombra(q, '#F3F5F8', par=True); borda_par(q, 'left', VERDE, 36)
                q.paragraph_format.keep_with_next = True
                escreve(q, f'{b[1]} {b[2].upper()}', 10.5, AZUL, negrito=True)
            elif k == 'subsecao':
                q = doc.add_paragraph(); espaco(q, 8, 3); q.paragraph_format.keep_with_next = True; escreve(q, b[1], 10, AZUL, negrito=True)
            elif k == 'caixa':
                c = CAIXAS[b[1]]
                tb = doc.add_table(rows=1, cols=1); tb.alignment = WD_TABLE_ALIGNMENT.CENTER
                cel = tb.rows[0].cells[0]; cel.width = Cm(largura); sombra(cel, c['fundo'])
                bordas_celula(cel, {'top': (c['contorno'], 6), 'right': (c['contorno'], 6), 'bottom': (c['contorno'], 6), 'left': (c['borda'], 36)})
                for i, txt in enumerate(b[3]):
                    q = cel.paragraphs[0] if i == 0 else cel.add_paragraph(); q.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY; espaco(q, 4 if i == 0 else 0, 4)
                    if i == 0 and b[2]:
                        escreve(q, b[2] + ' ', 9.5, negrito=True)
                    escreve(q, txt, 9.5)
                doc.add_paragraph().paragraph_format.space_after = Pt(2)
            elif k == 'cards':
                tb = doc.add_table(rows=1, cols=len(b[1])); tb.alignment = WD_TABLE_ALIGNMENT.CENTER
                for cel, it in zip(tb.rows[0].cells, b[1]):
                    bordas_celula(cel, {x: ('#1F2937', 10) for x in ('top', 'left', 'bottom', 'right')})
                    q = cel.paragraphs[0]; q.alignment = WD_ALIGN_PARAGRAPH.CENTER; espaco(q, 4, 1); escreve(q, it[0].upper(), 6.5, CINZA)
                    q = cel.add_paragraph(); q.alignment = WD_ALIGN_PARAGRAPH.CENTER; espaco(q, 0, 1); escreve(q, it[1], 13, AZUL, negrito=True)
                    if len(it) > 2 and it[2]:
                        q = cel.add_paragraph(); q.alignment = WD_ALIGN_PARAGRAPH.CENTER; espaco(q, 0, 4); escreve(q, it[2], 7, CINZA)
                doc.add_paragraph().paragraph_format.space_after = Pt(2)
            elif k == 'tabela':
                _, cab, linhas, leg, num, larg, dest, fonte = b
                tb = doc.add_table(rows=1 + len(linhas), cols=len(cab)); tb.alignment = WD_TABLE_ALIGNMENT.CENTER
                larg = larg or [100 / len(cab)] * len(cab)
                for i, linha in enumerate([cab] + [[str(v) for v in l] for l in linhas]):
                    for j, v in enumerate(linha):
                        cel = tb.rows[i].cells[j]; cel.width = Cm(largura * larg[j] / 100)
                        bordas_celula(cel, {'top': ('#FFFFFF', 0), 'left': ('#FFFFFF', 0), 'right': ('#FFFFFF', 0), 'bottom': ('#E3E8EF', 4)})
                        if i == 0:
                            sombra(cel, AZUL)
                        elif (i - 1) in dest:
                            sombra(cel, '#FFF6D6')
                        elif i % 2 == 0:
                            sombra(cel, '#F7F9FC')
                        q = cel.paragraphs[0]; espaco(q, 2, 2, 1.0)
                        q.alignment = WD_ALIGN_PARAGRAPH.RIGHT if j in num else WD_ALIGN_PARAGRAPH.LEFT
                        escreve(q, v, 8, '#FFFFFF' if i == 0 else None, negrito=(i == 0 or (i - 1) in dest))
                    if i == 0:
                        trPr = tb.rows[0]._tr.get_or_add_trPr(); e = OxmlElement('w:tblHeader'); e.set(qn('w:val'), 'true'); trPr.append(e)
                if leg:
                    q = doc.add_paragraph(); q.alignment = WD_ALIGN_PARAGRAPH.CENTER; espaco(q, 3, 2); escreve(q, leg, 8, CINZA, italico=True)
                if fonte:
                    q = doc.add_paragraph(); espaco(q, 0, 8); escreve(q, fonte, 7.5, CINZA)
                if not leg and not fonte:
                    doc.add_paragraph().paragraph_format.space_after = Pt(2)
            elif k == 'figura':
                q = doc.add_paragraph(); q.alignment = WD_ALIGN_PARAGRAPH.CENTER; espaco(q, 6, 2)
                q.add_run().add_picture(str(b[1]), width=Cm(min(b[3], largura)))
                q = doc.add_paragraph(); q.alignment = WD_ALIGN_PARAGRAPH.CENTER; espaco(q, 0, 10); escreve(q, b[2], 8, CINZA, italico=True)
            elif k == 'lista':
                for n, it in enumerate(b[1], 1):
                    q = doc.add_paragraph(style='List Number' if b[2] else 'List Bullet'); q.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                    espaco(q, 0, 3); escreve(q, it)
            elif k == 'quebra':
                doc.add_page_break()
            elif k == 'assinatura':
                q = doc.add_paragraph(); espaco(q, 18, 6); escreve(q, b[1])
                q = doc.add_paragraph(); espaco(q, 6, 0); escreve(q, b[2], negrito=True)
                for x in b[3]:
                    q = doc.add_paragraph(); espaco(q, 0, 0); escreve(q, x)
        doc.save(str(caminho))

    def salvar(self, base):
        """Grava base.html, base.pdf e base.docx."""
        base = Path(base)
        base.parent.mkdir(parents=True, exist_ok=True)
        h = base.with_suffix('.html'); h.write_text(self.html(), encoding='utf-8')
        self.salvar_pdf(h, base.with_suffix('.pdf'))
        self.salvar_docx(base.with_suffix('.docx'))
        return h, base.with_suffix('.pdf'), base.with_suffix('.docx')


# ---------------------------------------------------------------- Markdown -> Documento
ICONES = ['📌', '📊', '🔎', '🧩', '📅', '⚖️', '🔧', '📎', '🗂️', '✅']


def de_markdown(caminho_md, setor=None, subtitulos=None):
    """Lê um .md simples (títulos, parágrafos, listas, tabelas, citações e imagens) e devolve um Documento no modelo institucional.

    Convenções: a primeira linha '# ' é o título; '## ' vira seção; '### ' vira subseção; '> ' vira caixa de informação
    ('> **Atenção:**' vira caixa amarela); a linha que começa com 'Cuiabá/MT' vira a data.
    """
    caminho_md = Path(caminho_md)
    linhas = caminho_md.read_text(encoding='utf-8').splitlines()
    titulo, i = caminho_md.stem.replace('_', ' '), 0
    if linhas and linhas[0].startswith('# '):
        titulo, i = linhas[0][2:].strip(), 1
    partes = [p.strip() for p in re.split(r'\s+-\s+', titulo, maxsplit=1)]
    doc = Documento(partes[0].upper(), (subtitulos or []) + ([partes[1]] if len(partes) > 1 else []) or ['SEPLAG/MT'],
                    nome_arquivo=caminho_md.stem, **({'setor': setor} if setor else {}))
    n_sec, par, n_fig = 0, [], 0

    def fecha_par():
        if par:
            doc.p(' '.join(par)); par.clear()

    while i < len(linhas):
        l = linhas[i].rstrip()
        s = l.strip()
        if not s or s == '---':
            fecha_par(); i += 1; continue
        if s.startswith('Cuiabá/MT') and not doc.blocos:
            doc.cidade_data = s; i += 1; continue
        if s.startswith('## '):
            fecha_par(); doc.secao(ICONES[n_sec % len(ICONES)], s[3:].strip()); n_sec += 1; i += 1; continue
        if s.startswith('### ') or s.startswith('#### '):
            fecha_par(); doc.subsecao(s.lstrip('#').strip()); i += 1; continue
        if s.startswith('>'):
            fecha_par(); bloco = []
            while i < len(linhas) and linhas[i].strip().startswith('>'):
                bloco.append(linhas[i].strip()[1:].strip()); i += 1
            texto = ' '.join(b for b in bloco if b)
            tipo = 'atencao' if re.match(r'\*\*(Aten|Ressalv|Cuidado)', texto) else 'info'
            doc.caixa(tipo, '', texto); continue
        if s.startswith('|'):
            fecha_par(); tab = []
            while i < len(linhas) and linhas[i].strip().startswith('|'):
                tab.append(linhas[i].strip()); i += 1
            celulas = [[c.strip() for c in t.strip('|').split('|')] for t in tab if not re.match(r'^\|[\s:|-]+\|$', t)]
            cab, corpo = celulas[0], celulas[1:]
            numericas = [j for j in range(len(cab)) if corpo and all(re.match(r'^[-+R$\s\d.,%()]*$', r[j] if j < len(r) else '') for r in corpo)
                         and any(re.search(r'\d', r[j] if j < len(r) else '') for r in corpo)]
            doc.tabela(cab, [r + [''] * (len(cab) - len(r)) for r in corpo], numericas=numericas)
            continue
        m = re.match(r'!\[([^\]]*)\]\(([^)]+)\)', s)
        if m:
            fecha_par(); n_fig += 1
            img = (caminho_md.parent / m.group(2)).resolve()
            if img.exists():
                doc.figura(img, m.group(1) or f'Figura {n_fig}')
            i += 1; continue
        if re.match(r'^([-*]|\d+\.)\s', s):
            fecha_par(); numerada = bool(re.match(r'^\d+\.', s)); itens = []
            while i < len(linhas) and re.match(r'^\s*([-*]|\d+\.)\s', linhas[i]):
                itens.append(re.sub(r'^\s*([-*]|\d+\.)\s+', '', linhas[i]).strip()); i += 1
            doc.lista(itens, numerada); continue
        if s.startswith('```'):
            fecha_par(); i += 1; codigo = []
            while i < len(linhas) and not linhas[i].strip().startswith('```'):
                codigo.append(linhas[i]); i += 1
            i += 1
            doc.caixa('info', '', '`' + '`\n`'.join(c for c in codigo if c.strip()) + '`'); continue
        par.append(s); i += 1
    fecha_par()
    return doc
