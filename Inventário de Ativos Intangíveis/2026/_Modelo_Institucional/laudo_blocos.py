"""Cópia de laudo_revisao_apf.py para laudos e relatórios genéricos montados por blocos (ex.: laudos de softwares adquiridos e do SEAP),
com o bloco extra ["figura", "caminho relativo ao JSON", "legenda", largura_cm].

Original: Laudo Técnico de Revisão de Contagem de Pontos de Função, no modelo institucional (HTML, PDF e Word), montado por blocos
descritos em JSON. Usado para revisar contagens apresentadas por contratadas (projetos de desenvolvimento ou de melhoria
medidos em PF) e registrar a contagem revisada e a conciliação.

Uso (na pasta 2026):
    python _Modelo_Institucional/laudo_blocos.py "<pasta>/laudo.json"

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

Estilo sóbrio de documento pericial (padrão): títulos de seção e quadros sem a barra de destaque à esquerda, no PDF e no
Word; use "" como ícone das seções e evite emojis no conteúdo ("estilo_sobrio": false volta ao visual dos laudos de avaliação).
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from documento_seplag import Documento  # noqa: E402
import re  # noqa: E402
import zipfile  # noqa: E402
import shutil  # noqa: E402

CSS_SOBRIO = ('h2 { border-left: none !important; padding-left: 0 !important; background: none !important; '
              'border-bottom: 1px solid #c9d3e0; } .caixa { border-left-width: 1px !important; }')


class DocumentoSobrio(Documento):
    """Mesmo modelo institucional, sem a barra lateral dos títulos e dos quadros."""

    def html(self):
        return super().html().replace('</style>', CSS_SOBRIO + '</style>', 1)

    def salvar_docx(self, caminho):
        super().salvar_docx(caminho)
        tmp = Path(str(caminho) + '.tmp')
        with zipfile.ZipFile(caminho) as z:
            xml = z.read('word/document.xml').decode('utf-8')
            # barra verde dos títulos (borda esquerda de parágrafo) e sombreamento cinza
            xml = re.sub(r'<w:pBdr>.*?</w:pBdr>', lambda m: re.sub(r'<w:left [^>]*/>', '', m.group(0)), xml, flags=re.S)
            # borda esquerda grossa dos quadros (célula): afina para a espessura do contorno
            xml = re.sub(r'(<w:left [^>]*?)w:sz="36"', r'\1w:sz="6"', xml)
            with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zo:
                for it in z.infolist():
                    zo.writestr(it, xml.encode('utf-8') if it.filename == 'word/document.xml' else z.read(it.filename))
        shutil.move(tmp, caminho)


def main(cfg_path):
    cfg_path = Path(cfg_path)
    c = json.load(open(cfg_path, encoding='utf-8'))
    if '—' in json.dumps(c, ensure_ascii=False):
        raise SystemExit('O JSON contém travessão longo; reescreva a frase.')
    classe = DocumentoSobrio if c.get('estilo_sobrio', True) else Documento
    d = classe(c['titulo'], c['subtitulos'], c['arquivo_saida'],
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
        elif tipo == 'figura':
            d.figura(str(cfg_path.parent / b[1]), b[2], *(b[3:4] or []))
        else:
            raise SystemExit(f'Bloco desconhecido: {tipo}')
    r = c['responsavel']
    d.assinatura(r.get('rotulo', 'Responsável técnico'), r['nome'], *r['linhas'])
    for arq in d.salvar(cfg_path.parent / c['arquivo_saida']):
        print('ok', arq)


if __name__ == '__main__':
    main(sys.argv[1])
