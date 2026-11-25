"""Manifestação Técnica sobre reconhecimento de bem intangível (IN Conjunta nº 003/2022/SEPLAG/SEFAZ), no modelo
institucional (HTML, PDF e Word). Usada em consultas de áreas demandantes: a contratação, licença ou software é ativo
intangível? Como mensurar, qual a vida útil, como amortizar?

Uso (na pasta 2026):
    python _Modelo_Institucional/manifestacao_tecnica.py "5. Governança_Recomendações/Manifestacoes_Tecnicas/<caso>/manifestacao.json"

Campos do JSON (textos em português formal, sem travessão):
  titulo, assunto, arquivo_saida, cidade_data, setor (opcional), numero (opcional)
  cards: [[rótulo, valor, complemento], ...]
  identificacao: [[item, informação], ...]                  -> 1. Identificação da consulta
  consulta: [parágrafos]                                     -> 2. Objeto da consulta
  documentos: [[documento, identificação, data, uso], ...]   -> 3. Documentos analisados
  fundamentos: [parágrafos], criterios: [[ponto, dispositivo, aplicação, resultado], ...]
                                                             -> 4. Análise pela IN (tabela por critério)
  contrapontos: [[titulo, texto], ...]                       -> 5. Aspectos que afastam ou condicionam o registro
  alternativa: {texto: [...], tabela: [[item, tratamento], ...]}  -> 6. Tratamento contábil caso o registro seja adotado
  inconsistencias: [itens]                                   -> 7. Inconsistências do documento analisado (opcional)
  conclusao: {titulo, texto, recomendacoes: [itens]}         -> 8. Conclusão e recomendação
  limites: [parágrafos]                                      -> nota final sobre a natureza opinativa
  responsavel: {nome, funcao, linhas: [...]}, qualificacao: texto (opcional)
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from documento_seplag import Documento  # noqa: E402


def main(cfg_path):
    cfg_path = Path(cfg_path)
    c = json.load(open(cfg_path, encoding='utf-8'))
    for k, v in c.items():  # regra de estilo dos documentos da comissão
        if '—' in json.dumps(v, ensure_ascii=False):
            raise SystemExit(f'Campo "{k}" contém travessão longo; reescreva a frase.')
    sub = [c['assunto']] + ([c['numero']] if c.get('numero') else [])
    d = Documento(c['titulo'], sub, c['arquivo_saida'], **({'setor': c['setor']} if c.get('setor') else {}),
                  cidade_data=c.get('cidade_data'))
    if c.get('cards'):
        d.cards([tuple(x) for x in c['cards']])
    for par in c.get('abertura', []):
        d.p(par)

    n = 0

    def sec(icone, titulo):
        nonlocal n
        n += 1
        d.secao(icone, f'{n}. {titulo}')

    sec('📌', 'Identificação da consulta')
    d.tabela(['Item', 'Informação'], c['identificacao'], legenda='Tabela 1 - Identificação', larguras=[28, 72])

    sec('🔎', 'Objeto da consulta')
    for par in c['consulta']:
        d.p(par)

    sec('📎', 'Documentos analisados')
    d.tabela(['Documento', 'Identificação', 'Data', 'Uso na análise'], c['documentos'],
             legenda='Tabela 2 - Documentos analisados', larguras=[30, 26, 14, 30])

    sec('⚖️', 'Análise pela Instrução Normativa Conjunta nº 003/2022/SEPLAG/SEFAZ')
    for par in c.get('fundamentos', []):
        d.p(par)
    d.tabela(['Ponto', 'Dispositivo', 'Aplicação ao caso', 'Resultado'], c['criterios'],
             legenda='Tabela 3 - Critérios da IN aplicados ao caso', larguras=[16, 20, 48, 16])

    if c.get('contrapontos'):
        sec('🧩', 'Aspectos que afastam ou condicionam o registro')
        for titulo, texto in c['contrapontos']:
            d.p(f'**{titulo}** {texto}')

    if c.get('alternativa'):
        sec('📊', 'Tratamento contábil caso o registro seja adotado')
        for par in c['alternativa'].get('texto', []):
            d.p(par)
        if c['alternativa'].get('tabela'):
            d.tabela(['Item', 'Tratamento'], c['alternativa']['tabela'], legenda='Tabela 4 - Parâmetros de registro',
                     larguras=[28, 72])

    if c.get('inconsistencias'):
        sec('🔧', 'Inconsistências do documento analisado')
        d.p(c.get('texto_inconsistencias', 'Recomenda-se à área demandante corrigir os pontos abaixo antes do prosseguimento:'))
        d.lista(c['inconsistencias'])

    sec('✅', 'Conclusão e recomendação')
    cc = c['conclusao']
    d.caixa('conclusao', cc['titulo'], cc['texto'])
    if cc.get('recomendacoes'):
        d.lista(cc['recomendacoes'], numerada=True)
    for par in c.get('limites', []):
        d.p(par)
    if c.get('qualificacao'):
        d.p(c['qualificacao'])
    d.p(c.get('fecho', 'É a manifestação.'))

    r = c['responsavel']
    d.assinatura(r.get('rotulo', 'Responsável técnico'), r['nome'], *r['linhas'])
    out = cfg_path.parent / c['arquivo_saida']
    for arq in d.salvar(out):
        print('ok', arq)


if __name__ == '__main__':
    main(sys.argv[1])
