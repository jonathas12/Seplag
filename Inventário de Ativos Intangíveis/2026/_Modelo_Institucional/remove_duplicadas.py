"""Remove funções duplicadas da aba Funções (limpa A a E e registra nota em O), editando só o XML."""
import json, re, shutil, sys, zipfile
from xml.sax.saxutils import escape
origem, destino, cfg = sys.argv[1], sys.argv[2], json.load(open(sys.argv[3], encoding='utf-8'))
with zipfile.ZipFile(origem) as z:
    wb = z.read('xl/workbook.xml').decode(); rels = z.read('xl/_rels/workbook.xml.rels').decode()
    rid = re.search(r'<sheet [^>]*name="Funções"[^>]*r:id="([^"]+)"', wb).group(1)
    alvo = 'xl/' + re.search(r'<Relationship [^>]*Id="%s"[^>]*Target="([^"]+)"' % rid, rels).group(1).lstrip('/').replace('xl/', '')
    xml = z.read(alvo).decode()
    for linha, nota in cfg.items():
        for col in 'ABCDE':
            ref = f'{col}{linha}'
            xml = re.sub(r'<c r="%s"([^>]*?)(?:/>|>.*?</c>)' % ref,
                         lambda m: '<c r="%s"%s/>' % (ref, re.sub(r'\s+t="[^"]*"', '', m.group(1))), xml, count=1, flags=re.S)
        ref = f'O{linha}'
        nova = f'<c r="{ref}" t="inlineStr"><is><t xml:space="preserve">{escape(nota)}</t></is></c>'
        if re.search(r'<c r="%s"' % ref, xml):
            xml = re.sub(r'<c r="%s"([^>]*?)(?:/>|>.*?</c>)' % ref, lambda m: nova.replace(f'<c r="{ref}"', f'<c r="{ref}"' + re.sub(r'\s+t="[^"]*"', '', m.group(1)), 1), xml, count=1, flags=re.S)
        else:
            raise SystemExit(f'célula {ref} inexistente')
    wbx = re.sub(r'<calcPr([^>]*?)(/?)>', lambda m: '<calcPr' + re.sub(r'\sfullCalcOnLoad="[^"]*"', '', m.group(1)) + ' fullCalcOnLoad="1"' + m.group(2) + '>', wb, count=1)
    with zipfile.ZipFile(destino, 'w', zipfile.ZIP_DEFLATED) as zo:
        for it in z.infolist():
            d = z.read(it.filename)
            if it.filename == alvo: d = xml.encode()
            elif it.filename == 'xl/workbook.xml': d = wbx.encode()
            zo.writestr(it, d)
print('ok', destino)
