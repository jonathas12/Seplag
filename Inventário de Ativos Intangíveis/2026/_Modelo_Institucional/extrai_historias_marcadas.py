"""Extrai o texto de histórias de usuário (.docx, também com extensão malformada, e .pdf) de uma pasta qualquer, marcando
as mudanças da versão: trechos destacados (realce/sombreamento amarelo ou outra cor) saem como {+ ... +} e trechos riscados
(tachado simples ou duplo, ou revisão excluída) saem como {- ... -}. Tabelas (inclusive o histórico de versões) saem como
linhas "| c1 | c2 |". Arquivos sem histórias (txt) são copiados como estão, para leitura (ex.: LEIA-ME).

Uso:
    python extrai_historias_marcadas.py <pasta> <saida.txt> [--resumo saida.json]

O resumo JSON traz, por arquivo: código da história (USnn, US_nn, US-nn), título, versão do nome, última linha do histórico
de versões, quantidade de trechos novos/alterados e removidos. Serve para a contagem estimativa (skill
contagem-estimativa-apf): o que está em {+ +} indica função nova ou alterada; o que está em {- -}, função ou campo retirado.
"""
import html
import json
import re
import subprocess
import sys
import zipfile
from pathlib import Path

NS = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'


def _marcas_run(run_xml):
    destaque = bool(re.search(r'<w:highlight w:val="(?!none)[^"]+"', run_xml) or
                    re.search(r'<w:shd [^>]*w:fill="(?!auto|FFFFFF|ffffff)[0-9A-Fa-f]{6}"', run_xml))
    risco = bool(re.search(r'<w:(d)?strike(?: w:val="(?:true|1|on)")?\s*/>', run_xml))
    return destaque, risco


def _texto_paragrafo(p_xml):
    partes, atual, buf = [], None, []

    def fecha():
        if buf:
            t = ''.join(buf)
            partes.append({'+': '{+' + t + '+}', '-': '{-' + t + '-}'}.get(atual, t))
            buf.clear()

    # revisões excluídas (w:del) contam como riscadas; inseridas (w:ins) como novas
    p_xml = re.sub(r'<w:del\b.*?</w:del>', lambda m: m.group(0).replace('<w:delText', '<w:t').replace('</w:delText>', '</w:t>')
                   .replace('<w:rPr>', '<w:rPr><w:strike/>', 1) if '<w:rPr>' in m.group(0) else
                   m.group(0).replace('<w:r>', '<w:r><w:rPr><w:strike/></w:rPr>').replace('<w:delText', '<w:t').replace('</w:delText>', '</w:t>'),
                   p_xml, flags=re.S)
    for run in re.findall(r'<w:r\b[^>]*>.*?</w:r>', p_xml, re.S):
        txt = ''.join(re.findall(r'<w:t\b[^>]*>([^<]*)</w:t>', run))
        if '<w:tab/>' in run:
            txt = txt or ' '
        if not txt:
            continue
        destaque, risco = _marcas_run(run)
        marca = '-' if risco else ('+' if destaque else None)
        if marca != atual:
            fecha()
            atual = marca
        buf.append(html.unescape(txt))
    fecha()
    return ''.join(partes).strip()


def extrai_docx(caminho):
    xml = zipfile.ZipFile(caminho).read('word/document.xml').decode('utf-8')
    corpo = re.search(r'<w:body>(.*)</w:body>', xml, re.S).group(1)
    linhas = []
    for bloco in re.finditer(r'<w:tbl>.*?</w:tbl>|<w:p\b[^>]*>.*?</w:p>|<w:p\b[^>]*/>', corpo, re.S):
        b = bloco.group(0)
        if b.startswith('<w:tbl>'):
            for tr in re.findall(r'<w:tr\b.*?</w:tr>', b, re.S):
                cels = []
                for tc in re.findall(r'<w:tc\b.*?</w:tc>', tr, re.S):
                    t = ' '.join(x for x in (_texto_paragrafo(p) for p in re.findall(r'<w:p\b[^>]*>.*?</w:p>', tc, re.S)) if x)
                    if not cels or cels[-1] != t:
                        cels.append(t)
                if any(cels):
                    linhas.append('| ' + ' | '.join(cels) + ' |')
        else:
            t = _texto_paragrafo(b)
            if t:
                linhas.append(t)
    return linhas


def extrai_pdf(caminho):
    r = subprocess.run(['pdftotext', '-layout', str(caminho), '-'], capture_output=True, text=True)
    return [x.rstrip() for x in r.stdout.splitlines() if x.strip()]


def resumo(nome, linhas):
    m = re.search(r'\bUS[ _-]?0*(\d{1,4})', nome, re.I)
    v = re.search(r'[vV]\.?\s?(\d+(?:\.\d+)*)', nome)
    hist = [l for l in linhas if l.startswith('|') and re.search(r'\d{2}/\d{2}/\d{4}', l)]
    texto = '\n'.join(linhas)
    return {'arquivo': nome, 'codigo': f'US{int(m.group(1)):02d}' if m else None,
            'versao_nome': v.group(1) if v else None, 'ultima_versao_historico': hist[-1] if hist else None,
            'novos_ou_alterados': texto.count('{+'), 'removidos': texto.count('{-')}


def main(pasta, saida, resumo_json=None):
    pasta = Path(pasta)
    arquivos = sorted(p for p in pasta.rglob('*') if p.is_file())
    out, res = [], []
    for p in arquivos:
        suf = p.name.lower()
        try:
            if zipfile.is_zipfile(p) and 'word/document.xml' in zipfile.ZipFile(p).namelist():
                linhas = extrai_docx(p)
            elif suf.endswith('.pdf'):
                linhas = extrai_pdf(p)
            elif suf.endswith(('.txt', '.md')):
                linhas = p.read_text(encoding='utf-8', errors='replace').splitlines()
            else:
                continue
        except Exception as e:  # arquivo corrompido ou formato inesperado
            linhas = [f'[erro ao ler: {e}]']
        out.append(f'\n===== {p.name}')
        out += linhas
        res.append(resumo(p.name, linhas))
    Path(saida).write_text('\n'.join(out), encoding='utf-8')
    if resumo_json:
        Path(resumo_json).write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding='utf-8')
    for r in res:
        print(r['arquivo'], '|', r['codigo'], '| +', r['novos_ou_alterados'], '| -', r['removidos'])


if __name__ == '__main__':
    args = sys.argv[1:]
    rj = None
    if '--resumo' in args:
        i = args.index('--resumo')
        rj = args[i + 1]
        args = args[:i] + args[i + 2:]
    main(args[0], args[1], rj)
