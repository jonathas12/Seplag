"""Executa o projeto do Inventário de Ativos Intangíveis 2026, etapa por etapa, na ordem certa.

Uso, na pasta 2026, com o ambiente ativado (.venv):
    python executar.py --tudo              refaz mapa, análise, fichas, planilha, manifestação e documentos (sem internet)
    python executar.py --mapa              só o mapa comparativo (CSV) a partir dos dados brutos gravados
    python executar.py --analise           só o notebook de análise estatística
    python executar.py --fichas            só a planilha e as fichas de evidência
    python executar.py --manifestacao      só a manifestação técnica
    python executar.py --documentos        só os documentos (atas, plano, notas) em HTML, PDF e Word
    python executar.py --pncp              baixa do PNCP os documentos oficiais de cada preço (internet)
    python executar.py --prints            tira prints das telas do PNCP e do Compras.gov.br (internet, navegador visível)
    python executar.py --atualizar-dados   consulta de novo as APIs (Compras.gov.br e Banco Central) antes do mapa

Por padrão nada é consultado na internet: os resultados são reproduzidos a partir dos dados gravados na data da pesquisa.
Use --atualizar-dados só quando quiser uma nova pesquisa; os números podem mudar, porque as APIs são atualizadas todo dia.
"""
import argparse, os, subprocess, sys, time
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
PRECOS = RAIZ / '2. Levantamento_Identificacao_Avaliacao' / '2.3 Mapa Comparativo de Preços'
COLETA, EVID, ANALISE, PARECER = PRECOS / '2. Coleta de Dados', PRECOS / '3. Evidências', PRECOS / '5. Análise Estatística', PRECOS / '6. Parecer Técnico'
AMB = dict(os.environ, PYTHONUTF8='1', MPLBACKEND='Agg', PYTHONIOENCODING='utf-8')


def rodar(titulo, comando, pasta, extra_env=None):
    print(f'\n=== {titulo} ===', flush=True)
    inicio = time.time()
    r = subprocess.run(comando, cwd=pasta, env=dict(AMB, **(extra_env or {})))
    if r.returncode:
        sys.exit(f'Falhou: {titulo} (código {r.returncode}). Veja a mensagem acima.')
    print(f'--- concluído em {time.time() - inicio:.0f}s', flush=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    for op in ('tudo', 'mapa', 'analise', 'fichas', 'manifestacao', 'documentos', 'pncp', 'prints', 'atualizar-dados'):
        ap.add_argument(f'--{op}', action='store_true')
    a = ap.parse_args()
    if not any(vars(a).values()):
        ap.print_help(); return
    py = [sys.executable]
    if a.atualizar_dados:
        rodar('Coleta de preços na API do Compras.gov.br', py + ['coleta_precos_compras_gov.py'], COLETA)
    if a.tudo or a.mapa or a.atualizar_dados:
        env = {'ATUALIZAR_DADOS': '1'} if a.atualizar_dados else None
        rodar('Mapa comparativo a partir dos dados brutos', py + ['gera_mapa_comparativo.py'], COLETA)
        rodar('Links do PNCP de cada compra', py + ['enriquece_links_referencias.py'], COLETA, env)
        rodar('Atualização monetária pelo IPCA', py + ['atualiza_ipca_rastreabilidade.py'], COLETA, env)
    if a.pncp:
        rodar('Documentos oficiais no PNCP', py + ['coleta_documentos_pncp.py'], EVID)
    if a.tudo or a.analise:
        rodar('Notebook de análise estatística', py + ['-m', 'nbconvert', '--to', 'notebook', '--execute', '--inplace', 'Analise_Precos_PF-2026.ipynb'], ANALISE)
        rodar('Notebook em HTML', py + ['-m', 'nbconvert', '--to', 'html', 'Analise_Precos_PF-2026.ipynb'], ANALISE)
    if a.tudo or a.fichas:
        rodar('Planilha e fichas de evidência', py + ['gera_planilha_e_fichas.py'], COLETA)
    if a.tudo or a.manifestacao:
        rodar('Manifestação técnica', py + ['gera_manifestacao.py'], PARECER)
    if a.tudo or a.documentos:
        rodar('Documentos no modelo institucional', py + [str(RAIZ / '_Modelo_Institucional' / 'gera_documentos.py')], RAIZ)
    if a.prints:
        rodar('Prints das telas dos portais', py + ['captura_telas_portais.py'], EVID)
    print('\nPronto.')


if __name__ == '__main__':
    main()
