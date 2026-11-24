"""Gera a planilha de contagem indicativa (NESMA) de um sistema a partir de uma planilha modelo, sem perder gráficos,
imagens e fórmulas: limpa as funções da aba Funções, grava as funções de dados novas (ALI e AIE), preenche a aba Contagem,
recalcula pelo LibreOffice e confere o total indicativo ('Sumário 1'!G47 = 35 x ALI + 15 x AIE).

Uso (na pasta 2026):
    python _Modelo_Institucional/gera_contagem_indicativa.py modelo.xlsx destino.xlsx contagem.json

contagem.json:
{
  "grupos": [["Módulo ou grupo", [["Nome do ALI ou AIE", "ALI", "fonte/observação"], ...]], ...],
  "contagem": {"F5": "Aplicação", "F6": "Aplicação", "F7": "Indicativa (NESMA)", "R7": "PHP",
               "F9": "Responsável", "F10": "Revisor", "R9": "AAAA-MM-DD", "R10": "AAAA-MM-DD",
               "A17": "Escopo...", "A22": "Documentação..."},
  "limpar_linhas": [9, 140]        (opcional; faixa da aba Funções a limpar antes de gravar)
}
Modelo recomendado: APF-Recadastramento-v1.0.xlsx (pasta 11. Recadastramento de 2026), contagem indicativa com G47.
"""
import json
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

AQUI = Path(__file__).parent
PESO = {'ALI': 35, 'AIE': 15}


def _limpa(origem, destino, ini, fim):
    with zipfile.ZipFile(origem) as z:
        wb = z.read('xl/workbook.xml').decode()
        rels = z.read('xl/_rels/workbook.xml.rels').decode()
        rid = re.search(r'<sheet [^>]*name="Funções"[^>]*r:id="([^"]+)"', wb).group(1)
        alvo = 'xl/' + re.search(r'<Relationship [^>]*Id="%s"[^>]*Target="([^"]+)"' % rid, rels).group(1).replace('/xl/', '').lstrip('/')
        xml = z.read(alvo).decode()
        for r in range(ini, fim + 1):
            for col in 'ABCDEO':
                ref = f'{col}{r}'
                xml = re.sub(r'<c r="%s"([^>]*?)(?:/>|>.*?</c>)' % ref,
                             lambda m: '<c r="%s"%s/>' % (ref, re.sub(r'\s+t="[^"]*"', '', m.group(1))), xml, count=1, flags=re.S)
        with zipfile.ZipFile(destino, 'w', zipfile.ZIP_DEFLATED) as zo:
            for it in z.infolist():
                d = z.read(it.filename)
                if it.filename == alvo:
                    d = xml.encode()
                zo.writestr(it, d)


def main(modelo, destino, cfg_path):
    cfg = json.load(open(cfg_path, encoding='utf-8'))
    ini, fim = cfg.get('limpar_linhas', [9, 140])
    linhas, r, n, esperado = [], ini, {'ALI': 0, 'AIE': 0}, 0
    for grupo, funcoes in cfg['grupos']:
        linhas.append([r, {'A': grupo}])
        r += 1
        for nome, tipo, obs in funcoes:
            if tipo not in PESO:
                raise SystemExit(f'Contagem indicativa só tem ALI e AIE: {nome} ({tipo})')
            cel = {'A': nome, 'B': tipo, 'C': 'I'}
            if obs:
                cel['O'] = obs
            linhas.append([r, cel])
            r += 1
            n[tipo] += 1
            esperado += PESO[tipo]
        r += 1
    if r > fim:
        raise SystemExit(f'As funções passam da linha {fim}; aumente limpar_linhas.')
    tmp = Path(tempfile.mkdtemp())
    _limpa(modelo, tmp / 'a.xlsx', ini, fim)
    json.dump(linhas, open(tmp / 'linhas.json', 'w', encoding='utf-8'), ensure_ascii=False)
    py = sys.executable
    subprocess.run([py, '-I', str(AQUI / 'incrementa_baseline.py'), str(tmp / 'a.xlsx'), str(tmp / 'b.xlsx'), str(tmp / 'linhas.json')], check=True)
    subprocess.run(['soffice', '--headless', '--calc', '--convert-to', 'xlsx', '--outdir', str(tmp / 'out'), str(tmp / 'b.xlsx')],
                   check=True, capture_output=True)
    json.dump(cfg.get('contagem', {}), open(tmp / 'contagem.json', 'w', encoding='utf-8'), ensure_ascii=False)
    subprocess.run([py, '-I', str(AQUI / 'preenche_contagem.py'), str(tmp / 'out' / 'b.xlsx'), str(destino), str(tmp / 'contagem.json')], check=True)
    import openpyxl
    wb = openpyxl.load_workbook(destino, data_only=True)
    g47 = wb['Sumário 1']['G47'].value
    print(f"ALI {n['ALI']} x 35 + AIE {n['AIE']} x 15 = {esperado} PF; 'Sumário 1'!G47 = {g47}")
    if g47 != esperado:
        raise SystemExit('Total indicativo da planilha diverge do esperado; confira a faixa da fórmula de G47.')
    shutil.rmtree(tmp, ignore_errors=True)


if __name__ == '__main__':
    main(*sys.argv[1:4])
