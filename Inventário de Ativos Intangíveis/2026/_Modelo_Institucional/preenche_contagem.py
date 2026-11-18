"""Preenche células da aba Contagem de uma planilha de APF sem regravar o arquivo pelo openpyxl.

A planilha de contagem tem gráfico, imagem e comentários, que o openpyxl descarta ao salvar.
Este script altera apenas o XML das células indicadas (texto inline), preservando o restante.

Uso:
    python preenche_contagem.py origem.xlsx destino.xlsx campos.json

campos.json: {"F7": "Estimativa (NESMA)", "A17": "texto...", "A22": "texto..."}
"""
import json
import re
import shutil
import sys
import zipfile
from xml.sax.saxutils import escape


def _caminho_aba(z, nome_aba):
    wb = z.read('xl/workbook.xml').decode('utf-8')
    rels = z.read('xl/_rels/workbook.xml.rels').decode('utf-8')
    m = re.search(r'<sheet [^>]*name="%s"[^>]*r:id="([^"]+)"' % re.escape(nome_aba), wb)
    if not m:
        raise SystemExit(f'Aba "{nome_aba}" não encontrada.')
    rid = m.group(1)
    alvo = re.search(r'<Relationship [^>]*Id="%s"[^>]*Target="([^"]+)"' % rid, rels) or \
        re.search(r'<Relationship [^>]*Target="([^"]+)"[^>]*Id="%s"' % rid, rels)
    alvo = alvo.group(1).lstrip('/')
    return alvo if alvo.startswith('xl/') else 'xl/' + alvo


def _troca_celula(xml, ref, texto):
    valor = escape(texto).replace('\n', '&#10;')
    nova_is = f'<is><t xml:space="preserve">{valor}</t></is>'
    padrao = re.compile(r'<c r="%s"(?P<attrs>[^>]*?)(?:/>|>(?P<corpo>.*?)</c>)' % ref, re.S)
    m = padrao.search(xml)
    if not m:
        raise SystemExit(f'Célula {ref} não existe na aba (crie-a no Excel antes).')
    attrs = re.sub(r'\s+t="[^"]*"', '', m.group('attrs'))
    return xml[:m.start()] + f'<c r="{ref}"{attrs} t="inlineStr">{nova_is}</c>' + xml[m.end():]


def preencher(origem, destino, campos, aba='Contagem'):
    tmp = str(destino) + '.tmp'
    with zipfile.ZipFile(origem) as zin:
        caminho = _caminho_aba(zin, aba)
        xml = zin.read(caminho).decode('utf-8')
        for ref, texto in campos.items():
            xml = _troca_celula(xml, ref, texto)
        with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                dados = xml.encode('utf-8') if item.filename == caminho else zin.read(item.filename)
                zout.writestr(item, dados)
    shutil.move(tmp, destino)


if __name__ == '__main__':
    if len(sys.argv) != 4:
        raise SystemExit(__doc__)
    preencher(sys.argv[1], sys.argv[2], json.load(open(sys.argv[3], encoding='utf-8')))
    print('ok', sys.argv[2])
