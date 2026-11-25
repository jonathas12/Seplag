"""Gera ou atualiza a planilha de contagem estimativa (NESMA) no modelo institucional, preservando gráficos e fórmulas.

Pesos NESMA estimativa (complexidade padrão): ALI 7 (baixa), AIE 5 (baixa), EE 4 (média), CE 4 (média), SE 5 (média).
A planilha calcula sozinha a complexidade padrão quando TD e AR/TR ficam vazios (colunas D e E).

Uso (na pasta 2026):
    python _Modelo_Institucional/gera_contagem_estimativa.py origem.xlsx destino.xlsx contagem.json

contagem.json (todas as chaves são opcionais, menos uma de "grupos" ou "acrescentar"):
{
  "grupos": [["Grupo/história", [["Nome da função", "EE", "fonte/observação"], ...]], ...],
        -> contagem NOVA: limpa A-E e O das linhas de "limpar_linhas" e grava a partir da primeira linha
  "limpar_linhas": [9, 140],
  "acrescentar": [["Grupo/história", [["Nome", "ALI", "obs"], ...]], ...],
        -> INCREMENTO: grava os grupos novos depois da última linha usada da aba Funções (uma linha em branco antes)
  "anotar": {"23": "Alterada em 2026 (US01 v2.1): ..."},
        -> grava observação na coluna O de linhas existentes (alterações sem mudança de tamanho)
  "renomear": {"70": "Páginas - Editar"},
        -> corrige o nome (coluna A) de linhas existentes
  "contagem": {"F6": "Aplicação", "F7": "Estimativa (NESMA)", "R10": "AAAA-MM-DD", "A17": "...", "A22": "..."}
}
Ao final recalcula no LibreOffice (só use quando a planilha não tiver referências a outras pastas de trabalho) e confere
Funções!L4 com o total esperado (funções existentes + novas, pelos pesos NESMA).
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
PESO = {'ALI': 7, 'AIE': 5, 'EE': 4, 'CE': 4, 'SE': 5}


def _aba_funcoes(z):
    wb = z.read('xl/workbook.xml').decode()
    rels = z.read('xl/_rels/workbook.xml.rels').decode()
    rid = re.search(r'<sheet [^>]*name="Funções"[^>]*r:id="([^"]+)"', wb).group(1)
    return 'xl/' + re.search(r'<Relationship [^>]*Id="%s"[^>]*Target="([^"]+)"' % rid, rels).group(1).replace('/xl/', '').lstrip('/')


def _limpa(origem, destino, ini, fim):
    with zipfile.ZipFile(origem) as z:
        alvo = _aba_funcoes(z)
        xml = z.read(alvo).decode()
        for r in range(ini, fim + 1):
            for col in 'ABCDEO':
                ref = f'{col}{r}'
                xml = re.sub(r'<c r="%s"([^>]*?)(?:/>|>.*?</c>)' % ref,
                             lambda m: '<c r="%s"%s/>' % (ref, re.sub(r'\s+t="[^"]*"', '', m.group(1))), xml, count=1, flags=re.S)
        with zipfile.ZipFile(destino, 'w', zipfile.ZIP_DEFLATED) as zo:
            for it in z.infolist():
                zo.writestr(it, xml.encode() if it.filename == alvo else z.read(it.filename))


def _linhas_grupos(grupos, inicio):
    linhas, r, total = [], inicio, 0
    for grupo, funcoes in grupos:
        linhas.append([r, {'A': grupo}])
        r += 1
        for nome, tipo, obs in funcoes:
            if tipo not in PESO:
                raise SystemExit(f'Tipo inválido em "{nome}": {tipo} (use ALI, AIE, EE, CE ou SE)')
            cel = {'A': nome, 'B': tipo, 'C': 'I'}
            if obs:
                cel['O'] = obs
            linhas.append([r, cel])
            r += 1
            total += PESO[tipo]
        r += 1
    return linhas, total


def main(origem, destino, cfg_path):
    import openpyxl
    cfg = json.load(open(cfg_path, encoding='utf-8'))
    tmp = Path(tempfile.mkdtemp(dir=str(Path(destino).parent)))
    base = Path(origem)
    wb = openpyxl.load_workbook(origem, data_only=True)
    f = wb['Funções']
    if cfg.get('grupos'):
        ini, fim = cfg.get('limpar_linhas', [9, 140])
        _limpa(origem, tmp / 'limpo.xlsx', ini, fim)
        base = tmp / 'limpo.xlsx'
        linhas, esperado = _linhas_grupos(cfg['grupos'], ini)
        if linhas[-1][0] > fim:
            raise SystemExit('As funções passam do fim de limpar_linhas.')
    else:
        ultima = max(r for r in range(8, f.max_row + 1) if any(f.cell(r, c).value not in (None, '') for c in (1, 2)))
        existente = sum(PESO.get(str(f.cell(r, 2).value).strip(), 0) for r in range(8, f.max_row + 1) if f.cell(r, 2).value)
        linhas, novo = _linhas_grupos(cfg.get('acrescentar', []), ultima + 2)
        esperado = existente + novo
        print(f'Última linha usada: {ultima}; existente {existente} PF; novas funções {novo} PF')
    for lin, nome in cfg.get('renomear', {}).items():
        tipo = f.cell(int(lin), 2).value  # repete o tipo para manter o estilo de linha de função
        linhas.append([int(lin), {'A': nome, 'B': str(tipo).strip()} if tipo else {'A': nome}])
    for lin, obs in cfg.get('anotar', {}).items():
        linhas.append([int(lin), {'O': obs}])
    json.dump(linhas, open(tmp / 'linhas.json', 'w', encoding='utf-8'), ensure_ascii=False)
    py = sys.executable
    subprocess.run([py, '-I', str(AQUI / 'incrementa_baseline.py'), str(base), str(tmp / 'b.xlsx'), str(tmp / 'linhas.json')], check=True)
    subprocess.run(['soffice', '--headless', '--calc', '--convert-to', 'xlsx', '--outdir', str(tmp / 'out'), str(tmp / 'b.xlsx')],
                   check=True, capture_output=True)
    json.dump(cfg.get('contagem', {}), open(tmp / 'contagem.json', 'w', encoding='utf-8'), ensure_ascii=False)
    subprocess.run([py, '-I', str(AQUI / 'preenche_contagem.py'), str(tmp / 'out' / 'b.xlsx'), str(destino), str(tmp / 'contagem.json')], check=True)
    wb2 = openpyxl.load_workbook(destino, data_only=True)
    l4 = wb2['Funções']['L4'].value
    print(f'Total esperado {esperado} PF; Funções!L4 = {l4}')
    shutil.rmtree(tmp, ignore_errors=True)
    if l4 != esperado:
        raise SystemExit('O total da planilha diverge do esperado: confira a faixa da fórmula de L4 e as linhas gravadas.')


if __name__ == '__main__':
    main(*sys.argv[1:4])
