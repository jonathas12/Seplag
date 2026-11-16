"""Gera HTML, PDF e DOCX, no modelo institucional da SEPLAG, de todos os documentos .md da pasta 2026.

Uso, a partir da pasta 2026:
    python _Modelo_Institucional/gera_documentos.py              todos os .md (exceto README e LEIA-ME)
    python _Modelo_Institucional/gera_documentos.py arquivo.md   um arquivo
"""
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
from documento_seplag import de_markdown  # noqa: E402

RAIZ = AQUI.parent
IGNORAR = {'README.md', 'LEIA-ME.md'}
SUB = ['Inventário de Bens Intangíveis - Exercício 2026']

if __name__ == '__main__':
    alvos = [Path(a).resolve() for a in sys.argv[1:]] or sorted(p for p in RAIZ.rglob('*.md') if p.name not in IGNORAR and '.venv' not in p.parts)
    for md in alvos:
        doc = de_markdown(md, subtitulos=SUB)
        for s in doc.salvar(md.with_suffix('')):
            pass
        print('ok', md.relative_to(RAIZ))
