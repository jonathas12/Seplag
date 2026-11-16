"""Acrescenta ao mapa comparativo o número de controle PNCP, processo e links de cada referência.
Fonte: API de Dados Abertos do Compras.gov.br (módulo Contratações PNCP 14.133 e módulo Legado)."""
import csv, json, time, urllib.request, urllib.parse
B = 'https://dadosabertos.compras.gov.br'
CSV = '../4. Mapa Comparativo/Precos_Ponto_Funcao_2025-2026.csv'
def get(path, **q):
    u = B + path + '?' + urllib.parse.urlencode(q)
    for i in range(3):
        try:
            r = urllib.request.Request(u, headers={'Accept': 'application/json'})
            return json.load(urllib.request.urlopen(r, timeout=90))
        except Exception as e:
            err = e; time.sleep(2 * (i + 1))
    return {'resultado': [], 'erro': str(err)}
rows = list(csv.DictReader(open(CSV, encoding='utf-8-sig'), delimiter=';'))
cache = {}
for r in rows:
    if r['classificacao'].startswith('DESCARTE'):
        continue
    idc = r['id_compra']
    if idc not in cache:
        d = get('/modulo-contratacoes/1.1_consultarContratacoes_PNCP_14133_Id', tipo='idCompra', codigo=idc)
        cache[idc] = (d.get('resultado') or [None])[0]
json.dump(cache, open('Dados_Brutos/contratacoes_pncp_por_id_compra.json', 'w'), ensure_ascii=False, indent=1)
novos = ['numero_controle_pncp', 'processo', 'numero_compra', 'modalidade_nome', 'srp', 'amparo_legal',
         'valor_total_homologado', 'link_pncp', 'link_compras_gov', 'link_api_item']
for r in rows:
    c = cache.get(r['id_compra'])
    r['link_api_item'] = r.pop('fonte')
    r['link_compras_gov'] = ('https://cnetmobile.estaleiro.serpro.gov.br/comprasnet-web/public/landing'
                             f"?destino=acompanhamento-compra&compra={r['id_compra']}")
    if c:
        r.update(numero_controle_pncp=c['numeroControlePNCP'], processo=c.get('processo') or '',
                 numero_compra=c.get('numeroCompra') or '', modalidade_nome=c.get('modalidadeNome') or '',
                 srp='Sim' if c.get('srp') else 'Não', amparo_legal=c.get('amparoLegalNome') or '',
                 valor_total_homologado=c.get('valorTotalHomologado') or '',
                 link_pncp=f"https://pncp.gov.br/app/editais/{c['orgaoEntidadeCnpj']}/{c['anoCompraPncp']}/{c['sequencialCompraPncp']}")
    else:
        for k in novos[:8]:
            r.setdefault(k, '')
campos = [k for k in rows[0] if k not in novos] + novos
w = csv.DictWriter(open(CSV, 'w', newline='', encoding='utf-8-sig'), fieldnames=campos, delimiter=';', lineterminator='\n')
w.writeheader(); w.writerows(rows)
ok = sum(1 for r in rows if r['link_pncp']); tot = sum(1 for r in rows if not r['classificacao'].startswith('DESCARTE'))
print(f'{ok} de {tot} referências com número de controle PNCP')
for r in rows:
    if r['classificacao'].startswith('AMOSTRA A'):
        print(r['id'], r['numero_controle_pncp'] or 'SEM PNCP', r['processo'], r['modalidade_nome'], r['srp'], r['link_pncp'], sep=' | ')
