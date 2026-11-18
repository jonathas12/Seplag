"""Extrai de uma pasta de histórias de usuário (PDF) os dados usados no laudo e no quadro de documentação.

Para cada PDF: código da história, módulo, nome, texto "Eu, como... Quero... Para...", última versão e data
do histórico de revisões, datas e unidades da seção de aprovação.

Uso:
    python extrai_historias.py <pasta_com_pdfs> <saida.json>
"""
import json
import re
import sys
from pathlib import Path

import pymupdf

LIMPA = str.maketrans({'​': '', ' ': ' '})


def ler(pdf):
    with pymupdf.open(pdf) as d:
        return ''.join(p.get_text() for p in d).translate(LIMPA), d.page_count


def extrair(pdf):
    t, paginas = ler(pdf)
    m_cod = re.search(r'US-?0*(\d{2,4})', Path(pdf).stem) or re.search(r'US-?0*(\d{2,4})', t)
    modulo = re.search(r'Módulo:\s*(.+)', t)
    nome = re.search(r'Nome:\s*(.+)', t)
    plano = ' '.join(t.split())
    hist = re.search(r'(Eu,? (?:como|Como).{0,700}?)(?:\s\d\.\s*Crit|Critérios de [Aa]ceita|\s3\.\s)', plano)
    versoes = re.findall(r'\n(\d{2}/\d{2}/20\d{2})\s*\n\s*(\d+(?:\.\d+){1,3})\s*\n', t)
    aprov = t.split('Aprovação')[-1] if 'Aprovação' in t else ''
    return {
        'arquivo': Path(pdf).name,
        'codigo': f'US{int(m_cod.group(1)):04d}' if m_cod else None,
        'modulo': modulo.group(1).strip() if modulo else None,
        'nome_documento': nome.group(1).strip() if nome else None,
        'historia': hist.group(1).strip() if hist else None,
        'versao': versoes[-1][1] if versoes else None,
        'data': versoes[-1][0] if versoes else None,
        'qtde_versoes': len(versoes),
        'aprovacao_datas': sorted(set(re.findall(r'\d{2}/\d{2}/20\d{2}', aprov))),
        'paginas': paginas,
        'alertas': [a for a, c in [
            ('código do arquivo difere do nome no documento',
             m_cod and nome and f'{int(m_cod.group(1)):04d}' not in re.sub(r'\D', '', nome.group(1)).zfill(4)),
            ('módulo não preenchido', modulo and 'Insira' in modulo.group(1)),
            ('sem histórico de versões', not versoes),
            ('seção de aprovação sem data preenchida', not re.findall(r'\d{2}/\d{2}/20\d{2}', aprov))] if c],
    }


if __name__ == '__main__':
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    dados = [extrair(p) for p in sorted(Path(sys.argv[1]).glob('*.pdf'))]
    Path(sys.argv[2]).write_text(json.dumps(dados, ensure_ascii=False, indent=1), encoding='utf-8')
    for x in dados:
        print(x['codigo'], x['versao'], x['data'], '|', x['modulo'], '|', '; '.join(x['alertas']))
