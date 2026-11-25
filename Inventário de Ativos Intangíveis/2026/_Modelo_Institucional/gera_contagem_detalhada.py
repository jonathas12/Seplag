"""Gera a planilha de contagem DETALHADA (IFPUG) no modelo institucional, com tipos de dados (TD) e arquivos ou registros
referenciados (AR/TR) por função e tipo de manutenção (deflatores da aba Deflatores), preservando gráficos e fórmulas.

Diferenças em relação a gera_contagem_estimativa.py:
- cada função informa TD (coluna D) e AR/TR (coluna E), gravados como NÚMEROS, para que a planilha calcule a
  complexidade (Baixa, Média, Alta) pela tabela IFPUG; TD ou AR vazios fazem a planilha assumir a complexidade padrão
  (ALI/AIE baixa; transações média), o que deve ser registrado na observação;
- o tipo de manutenção (coluna C) é qualquer sigla da aba Deflatores (I, A, A50, A75, E, COR, PFT...);
- confere Funções!L4 (PF IFPUG, bruto) e Funções!L6 (PF Local da FS, com os deflatores).

Uso (na pasta 2026):
    python _Modelo_Institucional/gera_contagem_detalhada.py modelo.xlsx destino.xlsx contagem.json

contagem.json:
{
  "grupos": [["Grupo", [["Nome da função", "EE", "A50", 20, 6, "observação"], ...]], ...],
  "limpar_linhas": [9, 260],
  "contagem": {"F5": "...", "F6": "Projeto de Melhoria", "F7": "Detalhada (IFPUG)", ...}
}
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
sys.path.insert(0, str(AQUI))
import gera_contagem_estimativa as est  # noqa: E402

# Tabela IFPUG (CPM 4.3.1): contribuição por tipo e complexidade
PF = {'ALI': {'L': 7, 'A': 10, 'H': 15}, 'AIE': {'L': 5, 'A': 7, 'H': 10},
      'EE': {'L': 3, 'A': 4, 'H': 6}, 'CE': {'L': 3, 'A': 4, 'H': 6}, 'SE': {'L': 4, 'A': 5, 'H': 7}}


def complexidade(tipo, td, ar):
    """Mesma regra da coluna I da aba Funções."""
    if td in (None, '') or ar in (None, ''):
        return 'L' if tipo in ('ALI', 'AIE') else 'A'
    if tipo == 'EE':
        if ar >= 3:
            return 'H' if td >= 5 else 'A'
        if ar >= 2:
            return 'H' if td >= 16 else ('L' if td <= 4 else 'A')
        return 'L' if td <= 15 else 'A'
    if tipo in ('SE', 'CE'):
        if ar >= 4:
            return 'H' if td >= 6 else 'A'
        if ar >= 2:
            return 'H' if td >= 20 else ('L' if td <= 5 else 'A')
        return 'L' if td <= 19 else 'A'
    if ar >= 6:
        return 'H' if td >= 20 else 'A'
    if ar >= 2:
        return 'H' if td >= 51 else ('L' if td <= 19 else 'A')
    return 'L' if td <= 50 else 'A'


def _numeros(xlsx, valores):
    """Grava TD e AR como células numéricas (o incrementa_baseline só grava texto nas colunas A, B, C e O)."""
    import incrementa_baseline as inc
    tmp = Path(str(xlsx) + '.tmp')
    with zipfile.ZipFile(xlsx) as z:
        alvo = est._aba_funcoes(z)
        xml = z.read(alvo).decode()
        estilos = {c: inc.estilo_de(xml, f'{c}57') for c in 'DE'}
        for ref, v in valores:
            col, lin = ref[0], int(ref[1:])
            xml = inc.poe_celula(xml, lin, col, str(v), estilos[col])
            xml = re.sub(r'<c r="%s"([^>]*?) t="inlineStr"><is><t xml:space="preserve">([0-9.]+)</t></is></c>' % ref,
                         r'<c r="%s"\1><v>\2</v></c>' % ref, xml, count=1)
        with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zo:
            for it in z.infolist():
                zo.writestr(it, xml.encode() if it.filename == alvo else z.read(it.filename))
    shutil.move(tmp, xlsx)


def main(origem, destino, cfg_path):
    import openpyxl
    cfg = json.load(open(cfg_path, encoding='utf-8'))
    defl = {}
    wbm = openpyxl.load_workbook(origem, data_only=True)['Deflatores']
    for r in range(4, 39):
        sig, pct = wbm.cell(r, 7).value, wbm.cell(r, 8).value
        if sig and isinstance(pct, (int, float)):
            defl[str(sig).strip()] = float(pct)
    tmp = Path(tempfile.mkdtemp(dir=str(Path(destino).parent)))
    ini, fim = cfg.get('limpar_linhas', [9, 260])
    est._limpa(origem, tmp / 'limpo.xlsx', ini, fim)
    linhas, refs_num, r = [], [], ini
    bruto = local = 0.0
    for grupo, funcoes in cfg['grupos']:
        linhas.append([r, {'A': grupo}])
        r += 1
        for nome, tipo, manut, td, ar, obs in funcoes:
            if tipo not in PF or manut not in defl:
                raise SystemExit(f'Tipo ou manutenção inválidos em "{nome}": {tipo}/{manut}')
            cel = {'A': nome, 'B': tipo, 'C': manut}
            for col, v in (('D', td), ('E', ar)):
                if v not in (None, ''):
                    refs_num.append((f'{col}{r}', v))
            if obs:
                cel['O'] = obs
            linhas.append([r, cel])
            pf = PF[tipo][complexidade(tipo, td, ar)]
            bruto += pf
            local += pf * defl[manut]
            r += 1
        r += 1
    if r > fim:
        raise SystemExit('As funções passam do fim de limpar_linhas.')
    json.dump(linhas, open(tmp / 'linhas.json', 'w', encoding='utf-8'), ensure_ascii=False)
    py = sys.executable
    subprocess.run([py, '-I', str(AQUI / 'incrementa_baseline.py'), str(tmp / 'limpo.xlsx'), str(tmp / 'b.xlsx'),
                    str(tmp / 'linhas.json')], check=True)
    _numeros(tmp / 'b.xlsx', refs_num)
    perfil = tmp / 'perfil' / 'user'
    perfil.mkdir(parents=True)
    (perfil / 'registrymodifications.xcu').write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<oor:items xmlns:oor="http://openoffice.org/2001/registry" '
        'xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">\n'
        '<item oor:path="/org.openoffice.Office.Calc/Formula/Load"><prop oor:name="OOXMLRecalcMode" oor:op="fuse">'
        '<value>0</value></prop></item>\n</oor:items>\n', encoding='utf-8')
    subprocess.run(['soffice', f'-env:UserInstallation={(tmp / "perfil").as_uri()}', '--headless', '--calc',
                    '--convert-to', 'xlsx', '--outdir', str(tmp / 'out'), str(tmp / 'b.xlsx')], check=True, capture_output=True)
    json.dump(cfg.get('contagem', {}), open(tmp / 'contagem.json', 'w', encoding='utf-8'), ensure_ascii=False)
    subprocess.run([py, '-I', str(AQUI / 'preenche_contagem.py'), str(tmp / 'out' / 'b.xlsx'), str(destino),
                    str(tmp / 'contagem.json')], check=True)
    f = openpyxl.load_workbook(destino, data_only=True)['Funções']
    l4, l6 = f['L4'].value, f['L6'].value
    shutil.rmtree(tmp, ignore_errors=True)
    print(f'Esperado: PF IFPUG {bruto:g}, PF Local da FS {local:g}; planilha: L4 = {l4}, L6 = {l6}')
    if abs((l4 or 0) - bruto) > 1e-6 or abs((l6 or 0) - local) > 1e-6:
        raise SystemExit('A planilha diverge do esperado: confira TD/AR (números), siglas de manutenção e a faixa das fórmulas.')


if __name__ == '__main__':
    main(*sys.argv[1:4])
