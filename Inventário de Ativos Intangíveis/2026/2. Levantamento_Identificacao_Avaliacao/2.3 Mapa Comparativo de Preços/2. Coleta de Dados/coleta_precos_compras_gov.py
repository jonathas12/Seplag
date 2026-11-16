import json,urllib.request,urllib.parse,sys,time,datetime
B='https://dadosabertos.compras.gov.br'
log=[]
def get(path,**q):
    u=B+path+'?'+urllib.parse.urlencode(q)
    for i in range(4):
        try:
            r=urllib.request.Request(u,headers={'Accept':'application/json'})
            d=json.load(urllib.request.urlopen(r,timeout=120)); break
        except Exception as e:
            err=e; time.sleep(3*(i+1))
    else: raise err
    log.append({'url':u,'consultado_em':datetime.datetime.now(datetime.timezone.utc).isoformat(),'totalRegistros':d.get('totalRegistros')})
    return d
def allpages(path,**q):
    out=[];p=1
    while True:
        d=get(path,pagina=p,tamanhoPagina=500,**q); out+=d['resultado']
        if d.get('paginasRestantes',0)<=0: break
        p+=1
    return out
# catalogo grupo 111
cat=allpages('/modulo-servico/6_consultarItemServico',codigoGrupo=111)
json.dump(cat,open('Dados_Brutos/catser_grupo_111.json','w'),ensure_ascii=False,indent=1)
for c in cat: print(c['codigoServico'],c['codigoClasse'],c['nomeServico'],c['statusServico'],sep=' | ')
cods=[c['codigoServico'] for c in cat if c['statusServico']]
tot={}
for c in cods:
    try:
        pr=allpages('/modulo-pesquisa-preco/3_consultarServico',codigoItemCatalogo=c,dataCompraInicio='2025-01-01',dataCompraFim='2026-11-16')
    except Exception as e:
        print('ERR',c,e); continue
    json.dump(pr,open(f'Dados_Brutos/precos_praticados_catser_{c}.json','w'),ensure_ascii=False,indent=1)
    tot[c]=len(pr)
    try:
        arp=allpages('/modulo-arp/2_consultarARPItem',codigoItem=c,dataVigenciaInicialMin='2025-01-01',dataVigenciaInicialMax='2026-11-16')
        json.dump(arp,open(f'Dados_Brutos/arp_itens_catser_{c}.json','w'),ensure_ascii=False,indent=1)
        tot[c]=(len(pr),len(arp))
    except Exception as e: print('ERR arp',c,e)
print(tot)
json.dump(log,open('Dados_Brutos/_log_consultas.json','w'),ensure_ascii=False,indent=1)
