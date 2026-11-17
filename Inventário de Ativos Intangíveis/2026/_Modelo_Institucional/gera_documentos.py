"""Gera HTML, PDF e DOCX, no modelo institucional da SEPLAG, de todos os documentos .md da pasta 2026.

Uso, a partir da pasta 2026:
    python _Modelo_Institucional/gera_documentos.py              todos os .md (exceto README e LEIA-ME)
    python _Modelo_Institucional/gera_documentos.py arquivo.md   um arquivo
    python _Modelo_Institucional/gera_documentos.py --observar   fica aberto e gera de novo cada .md assim que ele é salvo
"""
import sys, time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
from documento_seplag import de_markdown  # noqa: E402

RAIZ = AQUI.parent
IGNORAR = {'README.md', 'LEIA-ME.md'}
SUB = ['Inventário de Bens Intangíveis - Exercício 2026']

def todos():
    return sorted(p for p in RAIZ.rglob('*.md') if p.name not in IGNORAR and '.venv' not in p.parts)


def gera(md):
    try:
        de_markdown(md, subtitulos=SUB).salvar(md.with_suffix(''))
        print(f'{time.strftime("%H:%M:%S")} ok', md.relative_to(RAIZ), flush=True)
    except Exception as e:            # no modo observação, um erro de digitação não derruba o processo
        print(f'{time.strftime("%H:%M:%S")} ERRO em', md.relative_to(RAIZ), '->', e, flush=True)
        if '--observar' not in sys.argv:
            raise


def observar():
    print('Observando os documentos .md. Salve um arquivo para gerar HTML, PDF e Word. Ctrl+C encerra.', flush=True)
    vistos = {p: p.stat().st_mtime for p in todos()}
    while True:
        time.sleep(1.5)
        for p in todos():
            m = p.stat().st_mtime
            if vistos.get(p) != m:
                vistos[p] = m
                time.sleep(0.5)       # espera o editor terminar de gravar
                gera(p)


if __name__ == '__main__':
    if '--observar' in sys.argv:
        observar()
    else:
        for md in ([Path(a).resolve() for a in sys.argv[1:]] or todos()):
            gera(md)
