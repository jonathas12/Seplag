import json,glob,csv,sys
nomes={c['codigoServico']:c['nomeServico'] for c in json.load(open('Dados_Brutos/catser_grupo_111.json', encoding='utf-8'))}
rows=[]
for f in sorted(glob.glob('Dados_Brutos/precos_praticados_catser_*.json')): rows+=json.load(open(f, encoding='utf-8'))
pf=[r for r in rows if 'PONTO' in (r['nomeUnidadeMedida'] or '').upper()]
out=[]
for r in pf:
    java=r['codigoItemCatalogo'] in (25852,25925)
    q=r['quantidade'] or 0; p=r['precoUnitario'] or 0
    if q<100 or p>3000 or p<100:
        st='DESCARTE SUGERIDO'; mot='Quantidade/preço incompatível com contratação por PF (indício de unidade lançada incorretamente ou escopo atípico)'
    elif java: st='AMOSTRA A - ADERENTE'; mot='Mesma tecnologia (Java) e unidade (PF) do Contrato 014/2022/SEPLAG'
    else: st='AMOSTRA B - AMPLIADA'; mot='Unidade PF, tecnologia distinta de Java; usar apenas para sensibilidade'
    out.append({'id':None,'classificacao':st,'motivo':mot,'catser':r['codigoItemCatalogo'],'catser_nome':nomes.get(r['codigoItemCatalogo'],''),
     'preco_unitario_pf':round(p,2),'quantidade_pf':q,'data_compra':r['dataCompra'],'data_resultado':r.get('dataResultado'),
     'orgao':r['nomeOrgao'],'uasg':r['codigoUasg'],'uasg_nome':r['nomeUasg'],'uf':r['estado'],'esfera':r['esfera'],'poder':r['poder'],
     'modalidade':r['modalidade'],'forma':r['forma'],'fornecedor':r['nomeFornecedor'],'cnpj_fornecedor':r['niFornecedor'],
     'id_compra':r['idCompra'],'item':r['numeroItemCompra'],'objeto':(r.get('objetoCompra') or '').replace('\n',' ').strip(),
     'descricao_item':(r.get('descricaoDetalhadaItem') or '').replace('\n',' ').strip()[:400],
     'fonte':f"https://dadosabertos.compras.gov.br/modulo-pesquisa-preco/3_consultarServico?codigoItemCatalogo={r['codigoItemCatalogo']}&idCompra={r['idCompra']}"})
ordem={'AMOSTRA A - ADERENTE':0,'AMOSTRA B - AMPLIADA':1,'DESCARTE SUGERIDO':2}
out.sort(key=lambda o:(ordem[o['classificacao']],o['data_compra']))
for i,o in enumerate(out,1): o['id']=i
w=csv.DictWriter(open('../4. Mapa Comparativo/Precos_Ponto_Funcao_2025-2026.csv','w',newline='',encoding='utf-8-sig'),fieldnames=list(out[0]),delimiter=';'); w.writeheader(); w.writerows(out)
import collections,statistics as st
print(collections.Counter(o['classificacao'] for o in out))
for o in out:
    if o['classificacao'].startswith('AMOSTRA A'):
        print(o['id'],o['catser'],o['data_compra'],o['preco_unitario_pf'],o['quantidade_pf'],o['uasg_nome'][:40],o['uf'],o['fornecedor'][:30],o['id_compra'],o['item'],o['objeto'][:110],sep=' | ')
for k in ordem:
    v=[o['preco_unitario_pf'] for o in out if o['classificacao']==k]
    if v: print(k,len(v),'min',min(v),'med',st.median(v),'media',round(st.mean(v),2),'max',max(v))
