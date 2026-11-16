"""Converte os documentos .md do inventário em .docx no padrão dos documentos da SEPLAG usados em 2025
(Manifestação Técnica e Relatório Final): Arial 12, texto justificado, margens 3 cm / 2,5 cm,
título centralizado em negrito, data à direita, seções numeradas em negrito, tabelas com grade.

Uso, a partir da pasta 2026:
    python3 _Modelo_Institucional/gera_docx.py            (converte todos os .md, exceto README e LEIA-ME)
    python3 _Modelo_Institucional/gera_docx.py arquivo.md (converte um arquivo)
Requer pandoc e python-docx."""
import glob, os, subprocess, sys
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

AQUI = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(AQUI, 'modelo_seplag_referencia.docx')

def fonte(estilo, tam=12, negrito=None, cor=True):
    f = estilo.font; f.name = 'Arial'; f.size = Pt(tam)
    if negrito is not None: f.bold = negrito
    if cor: f.color.rgb = RGBColor(0, 0, 0)
    f.italic = False
    rpr = estilo.element.get_or_add_rPr(); rf = rpr.find(qn('w:rFonts'))
    if rf is None: rf = OxmlElement('w:rFonts'); rpr.append(rf)
    for a in ('w:ascii', 'w:hAnsi', 'w:cs', 'w:eastAsia'): rf.set(qn(a), 'Arial')
    for a in ('w:asciiTheme', 'w:hAnsiTheme', 'w:cstheme', 'w:eastAsiaTheme'):
        if rf.get(qn(a)) is not None: del rf.attrib[qn(a)]

def cria_referencia():
    open(REF, 'wb').write(subprocess.run(['pandoc', '--print-default-data-file', 'reference.docx'], capture_output=True, check=True).stdout)
    d = Document(REF)
    for s in d.sections:
        s.page_width, s.page_height = Cm(21), Cm(29.7)
        s.left_margin = s.right_margin = Cm(3); s.top_margin = s.bottom_margin = Cm(2.5)
    for nome in ('Normal', 'Body Text', 'First Paragraph', 'Compact', 'Block Text'):
        if nome in d.styles:
            e = d.styles[nome]; fonte(e)
            e.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            e.paragraph_format.space_after = Pt(5); e.paragraph_format.space_before = Pt(0); e.paragraph_format.line_spacing = 1.15
    for nome in ('Title', 'Heading 1', 'Heading 2', 'Heading 3', 'Heading 4'):
        if nome in d.styles:
            e = d.styles[nome]; fonte(e, 12, True)
            e.paragraph_format.space_before = Pt(10); e.paragraph_format.space_after = Pt(5)
            e.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER if nome in ('Title', 'Heading 1') else WD_ALIGN_PARAGRAPH.JUSTIFY
    for nome in ('Image Caption', 'Table Caption', 'Caption'):
        if nome in d.styles:
            e = d.styles[nome]; fonte(e, 10); e.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if 'Hyperlink' in d.styles: d.styles['Hyperlink'].font.name = 'Arial'
    d.save(REF)

def grade(tabela):
    tblPr = tabela._tbl.tblPr; b = OxmlElement('w:tblBorders')
    for lado in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'):
        x = OxmlElement(f'w:{lado}'); x.set(qn('w:val'), 'single'); x.set(qn('w:sz'), '4'); x.set(qn('w:space'), '0'); x.set(qn('w:color'), '808080'); b.append(x)
    tblPr.append(b)

def ajusta(caminho):
    d = Document(caminho)
    for p in d.paragraphs:
        t = p.text.strip()
        if p.style.name.startswith('Heading') or p.style.name == 'Title':
            for r in p.runs:
                r.font.name = 'Arial'; r.font.size = Pt(12); r.font.bold = True; r.font.color.rgb = RGBColor(0, 0, 0)
                rf = r._r.get_or_add_rPr().find(qn('w:rFonts'))
                if rf is not None:
                    for a in ('w:ascii', 'w:hAnsi', 'w:cs'): rf.set(qn(a), 'Arial')
        if p.style.name == 'Heading 1': p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        elif t.startswith('Cuiabá/MT'): p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        elif t.startswith('ANEXO '):
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        if p.style.name in ('Captioned Figure', 'Figure') or p._p.findall('.//' + qn('w:drawing')):
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for p in d.paragraphs:
        for r in p.runs:
            if r.font.name and r.font.name != 'Arial': r.font.name = 'Arial'   # trechos de código do Markdown
    for forma in d.inline_shapes:
        if forma.width > Cm(15):
            r = forma.height / forma.width; forma.width = Cm(15); forma.height = int(Cm(15) * r)
    for t in d.tables:
        grade(t)
        for i, lin in enumerate(t.rows):
            for c in lin.cells:
                for p in c.paragraphs:
                    p.alignment = WD_ALIGN_PARAGRAPH.LEFT; p.paragraph_format.space_after = Pt(2)
                    for r in p.runs:
                        r.font.size = Pt(9); r.font.name = 'Arial'
                        if i == 0: r.font.bold = True
    d.save(caminho)

def converte(md):
    saida = os.path.splitext(md)[0] + '.docx'
    pasta = os.path.dirname(os.path.abspath(md))
    subprocess.run(['pandoc', os.path.basename(md), '-o', os.path.basename(saida), f'--reference-doc={REF}', '--resource-path=.'], cwd=pasta, check=True)
    ajusta(saida); print('ok', saida)

if __name__ == '__main__':
    if not os.path.exists(REF): cria_referencia()
    alvos = sys.argv[1:] or [f for f in glob.glob('**/*.md', recursive=True) if os.path.basename(f) not in ('README.md', 'LEIA-ME.md')]
    for a in alvos: converte(a)
