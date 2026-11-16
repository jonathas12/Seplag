"""Captura, no SEU navegador, os prints e os arquivos oficiais de cada referência de preço.

Por que rodar no seu computador: o PNCP e o Compras.gov.br exigem verificação hCaptcha antes de mostrar os dados.
Com o navegador aberto e visível, a verificação acontece normalmente (se aparecer desafio, resolva-o na tela).

Preparação (uma vez):
    pip install playwright
    playwright install chromium

Execução, a partir desta pasta (3. Evidências):
    python captura_evidencias_pncp.py

Saída, por referência, em "Documentos PNCP/Ref_XX - <órgão>/":
    01_PNCP_pagina.png            print da página da compra no PNCP
    02_Compras_itens.png          print da tela de itens e valores homologados no Compras.gov.br
    arquivos/                     edital, anexos, ata e contrato publicados no PNCP
    atas.json / arquivos.json     relação devolvida pelo PNCP
"""
import csv, json, re, sys
from pathlib import Path
from playwright.sync_api import sync_playwright

AQUI = Path(__file__).resolve().parent
CSV = AQUI.parent / '4. Mapa Comparativo' / 'Precos_Ponto_Funcao_2025-2026.csv'
SAIDA = AQUI / 'Documentos PNCP'
API = 'https://pncp.gov.br/api/pncp/v1/orgaos/{cnpj}/compras/{ano}/{seq}'

def limpa(nome):
    return re.sub(r'[\\/:*?"<>|]+', '_', nome).strip()[:120]

def espera(page, texto):
    page.wait_for_load_state('networkidle', timeout=60000)
    try:
        page.wait_for_selector(f'text={texto}', timeout=45000)
    except Exception:
        input('  A página não carregou sozinha. Resolva a verificação na janela do navegador e tecle ENTER aqui... ')

refs = [r for r in csv.DictReader(open(CSV, encoding='utf-8-sig'), delimiter=';') if r['classificacao'].startswith('AMOSTRA A')]
with sync_playwright() as p:
    nav = p.chromium.launch(headless=False)
    ctx = nav.new_context(viewport={'width': 1600, 'height': 1000}, accept_downloads=True)
    page = ctx.new_page()
    for r in refs:
        pasta = SAIDA / limpa(Path(r['evidencia_ficha']).stem)
        (pasta / 'arquivos').mkdir(parents=True, exist_ok=True)
        cnpj, ano, seq = r['link_pncp'].rstrip('/').split('/')[-3:]
        print(f"Ref {r['id']}: {r['uasg_nome']}")
        try:
            page.goto(r['link_pncp']); espera(page, 'Id contratação PNCP')
            page.screenshot(path=str(pasta / '01_PNCP_pagina.png'), full_page=True)
            page.goto(r['link_compras_gov']); espera(page, 'Itens')
            page.screenshot(path=str(pasta / '02_Compras_itens.png'), full_page=True)
            base = API.format(cnpj=cnpj, ano=ano, seq=seq)
            for nome in ('arquivos', 'atas'):
                resp = ctx.request.get(f'{base}/{nome}')
                if not resp.ok:
                    print(f'  {nome}: HTTP {resp.status}'); continue
                lista = resp.json()
                (pasta / f'{nome}.json').write_text(json.dumps(lista, ensure_ascii=False, indent=1), encoding='utf-8')
                if nome != 'arquivos':
                    continue
                for a in lista:
                    url = a.get('url') or a.get('uri')
                    if not url:
                        continue
                    d = ctx.request.get(url)
                    if d.ok:
                        cd = d.headers.get('content-disposition', '')
                        m = re.search(r'filename\*?=(?:UTF-8\'\')?"?([^";]+)', cd)
                        arq = limpa(m.group(1) if m else f"{a.get('sequencialDocumento', '')}_{a.get('titulo', 'arquivo')}")
                        (pasta / 'arquivos' / arq).write_bytes(d.body())
                        print('  baixado:', arq)
        except Exception as e:
            print('  ERRO:', e, file=sys.stderr)
    nav.close()
print('Concluído. Confira a pasta "Documentos PNCP".')
