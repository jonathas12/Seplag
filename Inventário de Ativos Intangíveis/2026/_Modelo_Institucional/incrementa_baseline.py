"""Acrescenta funções à aba Funções de uma baseline (ex.: melhoria medida em contagem estimativa), editando só o XML.

Uso: python incrementa_baseline.py origem.xlsx destino.xlsx linhas.json
linhas.json: [[linha, {"A": "texto", "B": "ALI", "C": "I", "O": "obs"}], ...]
As células são inseridas (ou substituídas) como texto inline na posição correta da linha; o restante do arquivo
(fórmulas, gráficos, imagens) é preservado. Marca o workbook para recalcular ao abrir (fullCalcOnLoad).
"""
import json, re, shutil, sys, zipfile
from xml.sax.saxutils import escape


def col_idx(ref):
    letras = re.match(r'[A-Z]+', ref).group(0)
    n = 0
    for ch in letras:
        n = n * 26 + ord(ch) - 64
    return n


def caminho_aba(z, nome):
    wb = z.read('xl/workbook.xml').decode('utf-8')
    rels = z.read('xl/_rels/workbook.xml.rels').decode('utf-8')
    rid = re.search(r'<sheet [^>]*name="%s"[^>]*r:id="([^"]+)"' % re.escape(nome), wb).group(1)
    alvo = (re.search(r'<Relationship [^>]*Id="%s"[^>]*Target="([^"]+)"' % rid, rels) or
            re.search(r'<Relationship [^>]*Target="([^"]+)"[^>]*Id="%s"' % rid, rels)).group(1).lstrip('/')
    return alvo if alvo.startswith('xl/') else 'xl/' + alvo


def estilo_de(xml, ref_modelo):
    m = re.search(r'<c r="%s"([^>]*?)(/>|>)' % ref_modelo, xml)
    s = re.search(r'\ss="(\d+)"', m.group(1)) if m else None
    return f' s="{s.group(1)}"' if s else ''


def poe_celula(xml, linha, col, texto, estilo):
    ref = f'{col}{linha}'
    nova = f'<c r="{ref}"{estilo} t="inlineStr"><is><t xml:space="preserve">{escape(texto)}</t></is></c>'
    m_row = re.search(r'<row r="%d"[^>]*?(?:/>|>(.*?)</row>)' % linha, xml, re.S)
    if not m_row:
        raise SystemExit(f'linha {linha} inexistente')
    bloco = m_row.group(0)
    if bloco.endswith('/>'):
        novo_bloco = bloco[:-2] + '>' + nova + '</row>'
    else:
        corpo = m_row.group(1)
        celulas = list(re.finditer(r'<c r="([A-Z]+)%d"[^>]*?(?:/>|>.*?</c>)' % linha, corpo, re.S))
        alvo = [c for c in celulas if c.group(1) == col]
        if alvo:
            c = alvo[0]
            corpo = corpo[:c.start()] + nova + corpo[c.end():]
        else:
            pos = len(corpo)
            for c in celulas:
                if col_idx(c.group(1)) > col_idx(col):
                    pos = c.start()
                    break
            corpo = corpo[:pos] + nova + corpo[pos:]
        novo_bloco = bloco[:m_row.start(1) - m_row.start()] + corpo + '</row>'
    return xml[:m_row.start()] + novo_bloco + xml[m_row.end():]


def main(origem, destino, linhas):
    tmp = destino + '.tmp'
    with zipfile.ZipFile(origem) as zin:
        aba = caminho_aba(zin, 'Funções')
        xml = zin.read(aba).decode('utf-8')
        estilos = {c: estilo_de(xml, f'{c}57') for c in 'ABCO'}
        estilo_grupo = estilo_de(xml, 'A49')
        for linha, celulas in linhas:
            for col, texto in celulas.items():
                est = estilo_grupo if (col == 'A' and 'B' not in celulas) else estilos[col]
                xml = poe_celula(xml, linha, col, texto, est)
        wb = zin.read('xl/workbook.xml').decode('utf-8')
        if '<calcPr' in wb:
            wb = re.sub(r'<calcPr([^>]*?)(/?)>', lambda m: '<calcPr' + re.sub(r'\sfullCalcOnLoad="[^"]*"', '', m.group(1)) + ' fullCalcOnLoad="1"' + m.group(2) + '>', wb, count=1)
        else:
            wb = wb.replace('</workbook>', '<calcPr fullCalcOnLoad="1"/></workbook>')
        with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                dados = zin.read(item.filename)
                if item.filename == aba:
                    dados = xml.encode('utf-8')
                elif item.filename == 'xl/workbook.xml':
                    dados = wb.encode('utf-8')
                zout.writestr(item, dados)
    shutil.move(tmp, destino)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], json.load(open(sys.argv[3], encoding='utf-8')))
    print('ok', sys.argv[2])
