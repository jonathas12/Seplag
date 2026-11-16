"""Atualiza os preços pelo IPCA (série 433 do Banco Central) e acrescenta as colunas de rastreabilidade.
Método igual ao da ferramenta Atualização_Monetária_IPCA.py: produto dos fatores mensais do mês da compra
até o último mês publicado (data-base)."""
import csv, json, urllib.request, datetime
CSV = '../4. Mapa Comparativo/Precos_Ponto_Funcao_2025-2026.csv'
DATA_PESQUISA = datetime.date(2026, 11, 16)
u = 'https://api.bcb.gov.br/dados/serie/bcdata.sgs.433/dados?formato=json&dataInicial=01/01/2024&dataFinal=16/11/2026'
serie = json.load(urllib.request.urlopen(u, timeout=60))
json.dump({'url': u, 'consultado_em': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'dados': serie},
          open('Dados_Brutos/ipca_serie_433_bcb.json', 'w'), ensure_ascii=False, indent=1)
ipca = {(int(d['data'][6:]), int(d['data'][3:5])): float(d['valor']) for d in serie}
base = max(ipca)
def fator(ano, mes):
    f = 1.0
    for (a, m), v in sorted(ipca.items()):
        if (a, m) >= (ano, mes):
            f *= 1 + v / 100
    return f
def meses(d):
    return (DATA_PESQUISA.year - d.year) * 12 + DATA_PESQUISA.month - d.month - (1 if DATA_PESQUISA.day < d.day else 0)
rows = list(csv.DictReader(open(CSV, encoding='utf-8-sig'), delimiter=';'))
novos = ['mes_base_preco', 'fator_ipca', 'data_base_atualizacao', 'preco_atualizado_pf', 'meses_ate_pesquisa',
         'dentro_13_meses', 'disputa_de_preco', 'evidencia_ficha']
for r in rows:
    d = datetime.date.fromisoformat(r['data_compra'])
    f = fator(d.year, d.month)
    r['mes_base_preco'] = f'{d.month:02d}/{d.year}'
    r['fator_ipca'] = f'{f:.6f}'
    r['data_base_atualizacao'] = f'{base[1]:02d}/{base[0]}'
    r['preco_atualizado_pf'] = f"{float(r['preco_unitario_pf']) * f:.2f}"
    r['meses_ate_pesquisa'] = meses(d)
    r['dentro_13_meses'] = 'Sim' if meses(d) <= 13 else 'Não'
    m = r.get('modalidade_nome', '')
    r['disputa_de_preco'] = 'Sim' if m.startswith(('Pregão', 'Concorr')) else ('Não' if m else '')
    r['evidencia_ficha'] = f"3. Evidências/Fichas/Ref_{int(r['id']):02d}.pdf" if r['classificacao'].startswith('AMOSTRA A') else ''
campos = [k for k in rows[0] if k not in novos] + novos
w = csv.DictWriter(open(CSV, 'w', newline='', encoding='utf-8-sig'), fieldnames=campos, delimiter=';', lineterminator='\n')
w.writeheader(); w.writerows(rows)
print('data-base', base)
for r in rows:
    if r['classificacao'].startswith('AMOSTRA A'):
        print(r['id'], r['preco_unitario_pf'], r['mes_base_preco'], r['fator_ipca'], r['preco_atualizado_pf'], r['meses_ate_pesquisa'], r['dentro_13_meses'], r['disputa_de_preco'], sep=' | ')
