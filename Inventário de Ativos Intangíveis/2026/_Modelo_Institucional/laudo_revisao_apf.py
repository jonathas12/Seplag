"""Laudo Técnico de Revisão de Contagem de Pontos de Função, no modelo institucional (HTML, PDF e Word), montado por blocos
descritos em JSON. Usado para revisar contagens apresentadas por contratadas (projetos de desenvolvimento ou de melhoria
medidos em PF) e registrar a contagem revisada e a conciliação.

Uso (na pasta 2026):
    python _Modelo_Institucional/laudo_revisao_apf.py "<pasta>/laudo_revisao.json"

laudo_revisao.json:
{
  "titulo": "Laudo Técnico de Revisão de Pontos de Função", "subtitulos": ["...", "..."],
  "arquivo_saida": "LAUDO_REVISAO_PF_...", "cidade_data": "Cuiabá/MT, ...", "setor": "..." (opcional),
  "cards": [[rótulo, valor, complemento], ...],
  "blocos": [
    ["secao", "📌", "1. Título"], ["subsecao", "1.1 ..."], ["p", "texto com **negrito**"],
    ["tabela", ["Col1", "Col2"], [[...], ...], "legenda", [larguras], [colunas numéricas], [linhas destacadas]],
    ["lista", ["item", ...]], ["lista_num", ["item", ...]], ["caixa", "conclusao|info|atencao", "Título:", "texto"],
    ["quebra"]
  ],
  "responsavel": {"rotulo": "...", "nome": "...", "linhas": ["...", ...]}
}
Os textos não podem conter travessão longo (o script recusa).
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from documento_seplag import Documento  # noqa: E402


def main(cfg_path):
    cfg_path = Path(cfg_path)
    c = json.load(open(cfg_path, encoding='utf-8'))
    if '—' in json.dumps(c, ensure_ascii=False):
        raise SystemExit('O JSON contém travessão longo; reescreva a frase.')
    d = Documento(c['titulo'], c['subtitulos'], c['arquivo_saida'],
                  **({'setor': c['setor']} if c.get('setor') else {}), cidade_data=c.get('cidade_data'))
    if c.get('cards'):
        d.cards([tuple(x) for x in c['cards']])
    for b in c['blocos']:
        tipo = b[0]
        if tipo == 'secao':
            d.secao(b[1], b[2])
        elif tipo == 'subsecao':
            d.subsecao(b[1])
        elif tipo == 'p':
            d.p(b[1])
        elif tipo == 'tabela':
            extra = b[3:] + [None] * (7 - len(b))
            d.tabela(b[1], b[2], legenda=extra[0], larguras=extra[1], numericas=extra[2] or (), destaque_linhas=extra[3] or ())
        elif tipo == 'lista':
            d.lista(b[1])
        elif tipo == 'lista_num':
            d.lista(b[1], numerada=True)
        elif tipo == 'caixa':
            d.caixa(b[1], b[2], *b[3:])
        elif tipo == 'quebra':
            d.quebra()
        else:
            raise SystemExit(f'Bloco desconhecido: {tipo}')
    r = c['responsavel']
    d.assinatura(r.get('rotulo', 'Responsável técnico'), r['nome'], *r['linhas'])
    for arq in d.salvar(cfg_path.parent / c['arquivo_saida']):
        print('ok', arq)


if __name__ == '__main__':
    main(sys.argv[1])
