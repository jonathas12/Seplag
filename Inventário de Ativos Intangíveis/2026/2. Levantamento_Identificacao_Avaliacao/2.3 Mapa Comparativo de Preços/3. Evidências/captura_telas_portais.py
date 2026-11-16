"""Tira prints das telas do PNCP e do Compras.gov.br de cada referência de preço, no navegador do servidor.

Os documentos oficiais já são baixados pela API pública do PNCP (coleta_documentos_pncp.py). Este script complementa
com a imagem das telas, como evidência visual. Os portais exibem uma verificação hCaptcha: por isso o navegador abre
visível e, se a verificação aparecer, o servidor a resolve na tela; o script espera.

Uso, a partir desta pasta (3. Evidências), com o ambiente ativado:
    python captura_telas_portais.py
    python captura_telas_portais.py --ref 1 8      (só as referências 1 e 8)

Saída: Documentos PNCP/<referência>/telas/01_PNCP.png e 02_Compras_gov_br_itens.png (+ 03_item_<n>.png, se o item abrir)
"""
import argparse, csv, re, time
from pathlib import Path
from playwright.sync_api import sync_playwright

AQUI = Path(__file__).resolve().parent
CSV = AQUI.parent / '4. Mapa Comparativo' / 'Precos_Ponto_Funcao_2025-2026.csv'
COMPRAS = 'https://cnetmobile.estaleiro.serpro.gov.br/comprasnet-web/public/compras/acompanhamento-compra?compra={}'


def espera_conteudo(page, texto, limite=90):
    """Espera o texto aparecer. Se houver verificação na tela, o usuário resolve; o script aguarda até o limite."""
    fim = time.time() + limite
    avisou = False
    while time.time() < fim:
        try:
            if page.get_by_text(texto, exact=False).first.is_visible():
                page.wait_for_timeout(1500)
                return True
        except Exception:
            pass
        if not avisou and time.time() > fim - limite + 10:
            print('   aguardando a página... se aparecer uma verificação, resolva-a na janela do navegador')
            avisou = True
        page.wait_for_timeout(1000)
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ref', nargs='*', type=int)
    args = ap.parse_args()
    refs = [r for r in csv.DictReader(open(CSV, encoding='utf-8-sig'), delimiter=';') if r['classificacao'].startswith('AMOSTRA A')]
    if args.ref:
        refs = [r for r in refs if int(r['id']) in args.ref]
    with sync_playwright() as pw:
        nav = pw.chromium.launch(headless=False)
        ctx = nav.new_context(viewport={'width': 1500, 'height': 1000}, locale='pt-BR')
        page = ctx.new_page()
        for r in refs:
            pasta = AQUI / 'Documentos PNCP' / Path(r['evidencia_ficha']).stem / 'telas'
            pasta.mkdir(parents=True, exist_ok=True)
            print(f"Ref {r['id']}: {r['uasg_nome']}")
            page.goto(r['link_pncp'])
            ok = espera_conteudo(page, 'Id contratação PNCP')
            page.screenshot(path=str(pasta / '01_PNCP.png'), full_page=True)
            print('   PNCP:', 'ok' if ok else 'página incompleta (print salvo assim mesmo)')
            page.goto(COMPRAS.format(r['id_compra']))
            ok = espera_conteudo(page, 'Itens')
            page.screenshot(path=str(pasta / '02_Compras_gov_br_itens.png'), full_page=True)
            print('   Compras.gov.br:', 'ok' if ok else 'página incompleta (print salvo assim mesmo)')
            try:   # tenta abrir o detalhe do item do preço
                linha = page.locator('div, li, tr').filter(has_text=re.compile(rf"^\s*{r['item']}\s")).first
                linha.click(timeout=5000)
                page.wait_for_timeout(2500)
                page.screenshot(path=str(pasta / f"03_item_{r['item']}.png"), full_page=True)
                print(f"   item {r['item']}: ok")
            except Exception:
                print(f"   item {r['item']}: não abriu automaticamente; o print da lista de itens foi salvo")
        nav.close()
    print('Concluído. Prints em Documentos PNCP/<referência>/telas')


if __name__ == '__main__':
    main()
