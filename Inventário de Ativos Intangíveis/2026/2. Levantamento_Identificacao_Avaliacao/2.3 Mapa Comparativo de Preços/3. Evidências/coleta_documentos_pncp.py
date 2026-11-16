"""Baixa do PNCP os documentos oficiais de cada referência de preço e gera os prints das páginas onde o preço aparece.

Fonte: API pública do Portal Nacional de Contratações Públicas (https://pncp.gov.br/api/pncp), sem login e sem captcha.

Para cada referência da Amostra A (preços Java em ponto de função):
  1. resultado_item.json     resultado homologado do item (preço unitário, quantidade, fornecedor, data)
  2. compra/                 arquivos da compra (edital, termo de referência, anexos)
  3. atas/                   atas de registro de preços e seus arquivos, quando houver
  4. contratos/              contratos vinculados à compra (Dados Abertos do Compras.gov.br) e seus arquivos no PNCP
  5. prints/                 imagem das páginas dos PDFs em que o preço unitário aparece, com o valor destacado
  6. _registro.json          URL, data e hora de cada consulta e de cada download

Uso, a partir desta pasta (3. Evidências):
    python coleta_documentos_pncp.py              baixa o que ainda não existe
    python coleta_documentos_pncp.py --refazer    baixa tudo de novo
"""
import csv, datetime, io, json, re, sys, time, urllib.parse, urllib.request, zipfile
from pathlib import Path

AQUI = Path(__file__).resolve().parent
CSV = AQUI.parent / '4. Mapa Comparativo' / 'Precos_Ponto_Funcao_2025-2026.csv'
SAIDA = AQUI / 'Documentos PNCP'
API = 'https://pncp.gov.br/api/pncp/v1'
DADOS = 'https://dadosabertos.compras.gov.br'
REFAZER = '--refazer' in sys.argv
AGORA = lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()


def http(url, binario=False, tentativas=4):
    erro = None
    for i in range(tentativas):
        try:
            req = urllib.request.Request(url, headers={'Accept': '*/*' if binario else 'application/json'})
            with urllib.request.urlopen(req, timeout=180) as r:
                corpo = r.read()
                if r.status == 204 or not corpo:
                    return None, dict(r.headers)
                return (corpo if binario else json.loads(corpo)), dict(r.headers)
        except urllib.error.HTTPError as e:
            if e.code in (204, 404):
                return None, {}
            erro = e
        except Exception as e:
            erro = e
        time.sleep(3 * (i + 1))
    raise RuntimeError(f'{url}: {erro}')


def nome_arquivo(cab, padrao):
    cd = cab.get('Content-Disposition') or cab.get('content-disposition') or ''
    m = re.search(r"filename\*=UTF-8''([^;]+)", cd) or re.search(r'filename="?([^";]+)"?', cd)
    nome = urllib.parse.unquote(m.group(1)) if m else padrao
    return re.sub(r'[\\/:*?"<>|]+', '_', nome).strip()[:150]


def baixa_lista(url_lista, pasta, registro):
    lista, _ = http(url_lista)
    registro.append({'consulta': url_lista, 'em': AGORA(), 'itens': len(lista or [])})
    if not lista:
        return []
    pasta.mkdir(parents=True, exist_ok=True)
    (pasta / '_lista.json').write_text(json.dumps(lista, ensure_ascii=False, indent=1), encoding='utf-8')
    salvos = []
    for a in lista:
        url = a.get('url') or a.get('uri')
        if not url or a.get('statusAtivo') is False:
            continue
        marcador = pasta / f".baixado_{a.get('sequencialDocumento', len(salvos))}"
        if marcador.exists() and not REFAZER:
            salvos += [pasta / n for n in marcador.read_text(encoding='utf-8').splitlines()]
            continue
        corpo, cab = http(url, binario=True)
        if corpo is None:
            continue
        nome = nome_arquivo(cab, f"{a.get('sequencialDocumento', '')}_{a.get('tipoDocumentoNome', 'documento')}")
        prefixo = f"{int(a.get('sequencialDocumento', 0)):02d} - {a.get('tipoDocumentoNome', 'Documento')} - "
        destino = pasta / (prefixo + nome)
        destino.write_bytes(corpo)
        gravados = [destino.name]
        registro.append({'download': url, 'arquivo': str(destino.relative_to(SAIDA)), 'bytes': len(corpo), 'em': AGORA()})
        if zipfile.is_zipfile(io.BytesIO(corpo)):
            dz = destino.with_suffix('')
            with zipfile.ZipFile(io.BytesIO(corpo)) as z:
                for info in z.infolist():
                    if info.is_dir():
                        continue
                    alvo = dz / re.sub(r'[\\:*?"<>|]+', '_', info.filename)
                    alvo.parent.mkdir(parents=True, exist_ok=True)
                    alvo.write_bytes(z.read(info))
                    gravados.append(str(alvo.relative_to(pasta)))
        marcador.write_text('\n'.join(gravados), encoding='utf-8')
        salvos += [pasta / g for g in gravados]
    return salvos


def codigo_orgao_siasg(id_compra, catser):
    bruto = AQUI.parent / '2. Coleta de Dados' / 'Dados_Brutos' / f'precos_praticados_catser_{catser}.json'
    for x in json.loads(bruto.read_text(encoding='utf-8')):
        if x.get('idCompra') == id_compra:
            return x.get('codigoOrgao')
    return None


def contratos_da_compra(r, registro):
    """Contratos vinculados à compra, pelo módulo de contratos dos Dados Abertos do Compras.gov.br (filtra pelo idCompra)."""
    orgao = codigo_orgao_siasg(r['id_compra'], r['catser'])
    if not orgao:
        return []
    achados = []
    ini, hoje = datetime.date.fromisoformat(r['data_compra']), datetime.date.today()
    while ini <= hoje:                                   # a API aceita no máximo 365 dias por consulta
        fim, pagina = min(ini + datetime.timedelta(days=364), hoje), 1
        while True:
            u = DADOS + '/modulo-contratos/1_consultarContratos?' + urllib.parse.urlencode({
                'pagina': pagina, 'tamanhoPagina': 500, 'codigoOrgao': orgao,
                'dataVigenciaInicialMin': ini.isoformat(), 'dataVigenciaInicialMax': fim.isoformat()})
            d, _ = http(u)
            registro.append({'consulta': u, 'em': AGORA()})
            if not d:
                break
            achados += [c for c in d.get('resultado', []) if c.get('idCompra') == r['id_compra'] and not c.get('contratoExcluido')]
            if not d.get('paginasRestantes'):
                break
            pagina += 1
        ini = fim + datetime.timedelta(days=1)
    return achados


def formatos_preco(v):
    v = float(v)
    br = f'{v:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
    return list(dict.fromkeys([br, br.replace('.', ''), f'{v:.2f}', f'{v:,.2f}']))


def prints_do_preco(arquivos, preco, pasta_prints, limite=4):
    try:
        import pymupdf
    except ImportError:
        import fitz as pymupdf
    pasta_prints.mkdir(parents=True, exist_ok=True)
    gerados = []
    for arq in arquivos:
        if arq.suffix.lower() != '.pdf' or len(gerados) >= limite:
            continue
        try:
            doc = pymupdf.open(arq)
        except Exception:
            continue
        for n, pag in enumerate(doc):
            achou = []
            for f in formatos_preco(preco):
                achou += pag.search_for(f)
            if not achou:
                continue
            for r in achou:
                a = pag.add_highlight_annot(r)
                a.set_colors(stroke=(1, 0.85, 0)); a.update()
            img = pasta_prints / f"{arq.stem[:70]} - pagina {n + 1}.png"
            pag.get_pixmap(dpi=130, annots=True).save(img)
            gerados.append(img)
            if len(gerados) >= limite:
                break
        doc.close()
    return gerados


def main():
    refs = [r for r in csv.DictReader(open(CSV, encoding='utf-8-sig'), delimiter=';') if r['classificacao'].startswith('AMOSTRA A')]
    resumo = []
    for r in refs:
        cnpj, ano, seq = r['link_pncp'].rstrip('/').split('/')[-3:]
        nome = Path(r['evidencia_ficha']).stem if r.get('evidencia_ficha') else f"Ref_{int(r['id']):02d}"
        pasta = SAIDA / nome
        pasta.mkdir(parents=True, exist_ok=True)
        registro = []
        print(f"Ref {r['id']}: {r['uasg_nome']} ({r['numero_controle_pncp']})")
        u = f"{API}/orgaos/{cnpj}/compras/{ano}/{seq}/itens/{r['item']}/resultados"
        res, _ = http(u)
        registro.append({'consulta': u, 'em': AGORA()})
        (pasta / 'resultado_item.json').write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding='utf-8')
        homologado = (res or [{}])[0].get('valorUnitarioHomologado')
        arquivos = baixa_lista(f"{API}/orgaos/{cnpj}/compras/{ano}/{seq}/arquivos", pasta / 'compra', registro)
        atas, _ = http(f"{API}/orgaos/{cnpj}/compras/{ano}/{seq}/atas")
        for ata in atas or []:
            arquivos += baixa_lista(f"{API}/orgaos/{cnpj}/compras/{ano}/{seq}/atas/{ata['sequencialAta']}/arquivos",
                                    pasta / 'atas' / f"Ata {ata.get('numeroAtaRegistroPreco', ata['sequencialAta']).replace('/', '-')}", registro)
        try:
            contratos = contratos_da_compra(r, registro)
        except Exception as e:
            print('   aviso: consulta de contratos falhou:', e)
            contratos = []
        (pasta / 'contratos_vinculados.json').write_text(json.dumps(contratos, ensure_ascii=False, indent=1), encoding='utf-8')
        for c in contratos:
            m = re.match(r'(\d{14})-2-(\d+)/(\d{4})', c.get('numeroControlePncpContrato') or '')
            if not m:
                continue
            cc, sq, an = m.groups()
            arquivos += baixa_lista(f"{API}/orgaos/{cc}/contratos/{an}/{int(sq)}/arquivos",
                                    pasta / 'contratos' / f"Contrato {str(c.get('numeroContrato', sq)).replace('/', '-')}", registro)
        prints = prints_do_preco(arquivos, r['preco_unitario_pf'], pasta / 'prints')
        confere = homologado is not None and abs(float(homologado) - float(r['preco_unitario_pf'])) < 0.005
        item = {'ref': int(r['id']), 'pasta': nome, 'preco_mapa': float(r['preco_unitario_pf']), 'preco_homologado_pncp': homologado,
                'preco_confere': confere, 'arquivos': len(arquivos), 'atas': len(atas or []), 'contratos': len(contratos),
                'paginas_com_preco': len(prints)}
        (pasta / '_registro.json').write_text(json.dumps({'resumo': item, 'eventos': registro}, ensure_ascii=False, indent=1), encoding='utf-8')
        resumo.append(item)
        print(f"   homologado no PNCP: {homologado} | confere com o mapa: {'sim' if confere else 'NÃO'} | arquivos: {len(arquivos)} | "
              f"atas: {len(atas or [])} | contratos: {len(contratos)} | páginas com o preço: {len(prints)}")
    (SAIDA / '_resumo_coleta.json').write_text(json.dumps({'gerado_em': AGORA(), 'referencias': resumo}, ensure_ascii=False, indent=1), encoding='utf-8')


if __name__ == '__main__':
    main()
