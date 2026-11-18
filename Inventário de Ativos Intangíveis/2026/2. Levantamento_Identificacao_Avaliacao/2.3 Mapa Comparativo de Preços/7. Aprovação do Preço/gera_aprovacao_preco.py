"""Gera a Manifestação Técnica de Aprovação do Preço do Ponto de Função (HTML, PDF e Word) no modelo institucional.

A decisão (cenário, base e grupo) e os códigos do Sigadoc ficam em aprovacao_preco.json. Todos os números vêm dos
mesmos arquivos da pesquisa de preços: 5. Análise Estatística/resultados_analise.json, config_pesquisa.json e
4. Mapa Comparativo/Precos_Ponto_Funcao_2025-2026.csv. Se a pesquisa for refeita, este documento acompanha.

Uso, a partir desta pasta:  python gera_aprovacao_preco.py
"""
import csv
import json
import re
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
sys.path.insert(0, str(RAIZ.parents[1] / '_Modelo_Institucional'))
from documento_seplag import Documento  # noqa: E402

DEC = json.loads((AQUI / 'aprovacao_preco.json').read_text(encoding='utf-8'))
CFG = json.loads((RAIZ / 'config_pesquisa.json').read_text(encoding='utf-8'))
R = json.loads((RAIZ / '5. Análise Estatística' / 'resultados_analise.json').read_text(encoding='utf-8'))
MAPA = {r['id']: r for r in csv.DictReader(open(RAIZ / '4. Mapa Comparativo' / 'Precos_Ponto_Funcao_2025-2026.csv',
                                                 encoding='utf-8-sig'), delimiter=';')}


def brl(v):
    return 'R$ ' + f'{float(v):,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')


def pct(v, sinal=False, casas=1):
    s = f'{v:+.{casas}f}' if sinal else f'{v:.{casas}f}'
    return s.replace('.', ',') + '%'


def refs(texto):
    return sorted(int(x) for x in re.findall(r'Ref (\d+)', texto))


# ---------------------------------------------------------------- dados da decisão
chave = f"{DEC['cenario']} | {DEC['base']}"
grupos = R['cenarios_detalhe'][chave]
G = grupos[DEC['grupo'] - 1]
preco = round(G['Centroide (média)'], 2)
ids = refs(G['Preços do grupo'])
AM = {a['Ref']: a for a in R['amostra_2026']}
membros = [AM[i] for i in ids]
DA = R['descritiva']['Preço atualizado']
C = R['contrato']['preco_vigente']
P25 = R['preco_2025']
F25 = R['fator_ipca_2025_para_base']
P25_base = round(P25 * F25, 2)
data_base = R['data_base_ipca']
comp = {c['Grupo'][:7]: c for c in R['comparacao_2025_2026']}

# estabilidade: em quais cenários o mesmo conjunto de preços forma um grupo
estab = []
for k, gs in R['cenarios_detalhe'].items():
    if not k.endswith(DEC['base']):
        continue
    for i, g in enumerate(gs, 1):
        if refs(g['Preços do grupo']) == ids:
            estab.append([k.split(' | ')[0], f'Grupo {i}', brl(g['Centroide (média)'])])
            break
    else:
        conj = [f"Grupo {i}: {', '.join(f'Ref {r}' for r in refs(g['Preços do grupo'])) or 'contrato'}"
                for i, g in enumerate(gs, 1) if set(refs(g['Preços do grupo'])) & set(ids)]
        estab.append([k.split(' | ')[0], 'Não forma o mesmo grupo', '; '.join(conj)])

outros = [g for i, g in enumerate(grupos, 1) if i != DEC['grupo']]
sem_disputa = [a['Ref'] for a in R['amostra_2026'] if a['Disputa de preço'] == 'Não']
fora_13 = [a['Ref'] for a in R['amostra_2026'] if a['Dentro de 13 meses'] == 'Não']
G1 = grupos[0]
g1_ids = refs(G1['Preços do grupo'])
inv = CFG['inventario_2025']
efeito = inv['valor_grupo_desenvolvidos_internamente'] * preco / P25
tam25 = f"{inv['tamanho_funcional_pf']:,.0f}".replace(',', '.')

# ---------------------------------------------------------------- documento
d = Documento('Manifestação Técnica - Aprovação do Preço do Ponto de Função',
              ['Inventário de Bens Intangíveis - Exercício 2026', 'Escolha e fundamentação do preço de referência'],
              'MANIFESTACAO_TECNICA_Aprovacao_Preco_PF_2026',
              setor='Comissão de Inventário e Avaliação de Bens Intangíveis (CIABI/SEPLAG)', cidade_data=DEC['cidade_data'])
d.cards([('Preço aprovado', brl(preco), 'por ponto de função'),
         ('Origem', f"Grupo {DEC['grupo']}", DEC['cenario'].split(' - ')[0] + ', preços atualizados'),
         ('Data-base', data_base, 'IPCA, série 433 do Banco Central'),
         ('Preços que formam o grupo', str(len(membros)), 'pregões eletrônicos com disputa')])
d.p('Esta manifestação registra a escolha, pela Comissão de Inventário e Avaliação de Bens Intangíveis (CIABI), do preço '
    'do ponto de função que valora os softwares medidos por pontos de função no inventário de 2026, e os fundamentos dessa '
    'escolha. Ela complementa a Manifestação Técnica da pesquisa de preços, que reúne os dados, as análises e as limitações '
    'e não indica preço. A separação entre a análise e a decisão é intencional: a análise é reproduzível por qualquer pessoa; '
    'a decisão é da comissão e fica fundamentada aqui.')

# 1
d.secao('📌', '1. Objeto e fundamento normativo')
d.p('A IN Conjunta nº 003/2022/SEPLAG/SEFAZ, art. 11, § 3º, define o valor do tamanho do ativo (VT) como a quantidade de '
    'pontos de função multiplicada pelo **valor de mercado** do ponto de função **apurado no momento da avaliação**. '
    'O preço aprovado aqui é esse valor de mercado e se aplica, de forma uniforme, a todos os softwares do inventário de 2026 '
    'avaliados pela metodologia do art. 11.')
d.tabela(['Norma', 'Dispositivo', 'Aplicação nesta escolha'], [
    ['IN Conjunta nº 003/2022/SEPLAG/SEFAZ', 'art. 11, §§ 1º e 3º; art. 13', 'Valor de mercado do PF no momento da avaliação, para fins de inventário e registro contábil'],
    ['Lei nº 14.133/2021', 'art. 23, § 1º, II', 'Uso de contratações similares da Administração Pública, observado o índice de atualização de preços correspondente'],
    ['Decreto Estadual nº 1.525/2022', 'regulamento da Lei nº 14.133/2021 em MT', 'Pesquisa de preços em contratações similares e sistemas oficiais'],
    ['Portaria nº 124/2026/SEPLAG', 'designação da comissão', 'Competência da CIABI para o inventário e a avaliação'],
], legenda='Tabela 1 - Fundamentos normativos', larguras=[30, 24, 46])

# 2
d.secao('🗂️', '2. Documentos de referência')
d.p('Os documentos abaixo estão registrados no Sigadoc, juntados no processo da pesquisa de preços (SEPLAG-DIC-2026/59836-A). Os laudos técnicos de avaliação de cada software citam estes códigos, '
    'o que liga cada valor do inventário ao preço aprovado e à pesquisa que o originou.')
d.tabela(['Documento', 'Arquivo', 'Código Sigadoc'],
         [[x['documento'], x['arquivo'], x['codigo'] or '[a registrar]'] for x in DEC['documentos_sigadoc']],
         legenda='Tabela 2 - Documentos de referência', larguras=[44, 30, 26])
FS = DEC.get('fichas_sigadoc', {})
if FS:
    d.tabela(['Ref.', 'Órgão comprador', 'Preço original', 'Ficha de evidência (Sigadoc)'],
             [[str(a['Ref']), a['Órgão'].title(), brl(a['Preço original']), FS.get(str(a['Ref']), '')] for a in R['amostra_2026']],
             legenda='Tabela 3 - Fichas de evidência de cada preço da amostra', numericas=[2], larguras=[7, 47, 16, 30])

# 3
d.secao('🔎', '3. Processo de formação do preço')
d.p('O preço resulta de um processo com etapas definidas, registradas e repetíveis. A Tabela 4 relaciona cada atributo '
    'exigido de um valor contábil auditável à evidência correspondente.')
d.tabela(['Atributo', 'Como foi atendido', 'Evidência'], [
    ['Objeto homogêneo', 'Recorte pelo Contrato nº 014/2022/SEPLAG: desenvolvimento em Java, medido em ponto de função, em fábrica de software', 'Manifestação da pesquisa, Tabela 1'],
    ['Fontes oficiais', 'Coleta nas APIs públicas do Compras.gov.br e do PNCP, compras de 01/2025 a 11/2026', 'Dados brutos gravados com data e consulta'],
    ['Rastreabilidade', 'Cada preço ligado ao órgão, processo, número de controle no PNCP, compra e item', 'Mapa Comparativo; fichas de evidência'],
    ['Conferência', '9 de 9 preços coincidem ao centavo com o resultado homologado no PNCP', 'Documentos oficiais baixados do PNCP'],
    ['Atualização monetária', f'IPCA (IBGE), série 433 do Banco Central, do mês da compra até {data_base}', 'Fator de cada preço no Mapa Comparativo'],
    ['Tratamento estatístico', 'Estatística descritiva, valores atípicos pelo intervalo interquartil, agrupamento K-Means e índice de silhueta', 'Notebook e resultados da análise'],
    ['Sensibilidade', 'Cinco cenários de amostra, com e sem atualização monetária', 'Manifestação da pesquisa, Seção 6'],
    ['Reprodutibilidade', 'Ambiente com versões fixadas; o comando de execução refaz mapa, análise e documentos com resultado idêntico', 'Guia Como Executar o Projeto'],
    ['Separação análise e decisão', 'A pesquisa não indica preço; a escolha é da comissão, fundamentada neste documento', 'Este documento'],
], legenda='Tabela 4 - Atributos do processo e evidências', larguras=[20, 52, 28])

# 4
d.secao('✅', '4. Preço aprovado')
d.caixa('conclusao', 'Decisão da comissão:',
        f"O preço de referência do ponto de função para o inventário de 2026 é de **{brl(preco)} ({DEC['preco_por_extenso']})**, "
        f"centroide do Grupo {DEC['grupo']} do agrupamento K-Means no cenário {DEC['cenario']}, com os preços atualizados pelo IPCA até {data_base}.")
d.tabela(['Ref.', 'Órgão', 'Compra', 'Preço original', 'Fator IPCA', f'Preço em {data_base}', 'Nº de controle PNCP', 'Ficha (Sigadoc)'],
         [[str(a['Ref']), a['Órgão'].title(), a['Data da compra'], brl(a['Preço original']),
           f"{a['Fator IPCA']:.6f}".replace('.', ','), brl(a['Preço atualizado']), MAPA[str(a['Ref'])]['numero_controle_pncp'], FS.get(str(a['Ref']), '')]
          for a in membros] + [['', 'Centroide do grupo', '', '', '', brl(preco), '', '']],
         legenda=f"Tabela 5 - Preços que formam o Grupo {DEC['grupo']}", numericas=[3, 4, 5],
         larguras=[5, 19, 10, 11, 8, 11, 18, 18], destaque_linhas=[len(membros)])
d.p('O cenário C5 inclui o Contrato nº 014/2022/SEPLAG entre os preços analisados. O contrato fica no grupo de menor valor '
    f"e não altera o Grupo {DEC['grupo']}, cujo centroide é o mesmo do cenário C1 (9 preços).")

# 5
d.secao('⚖️', '5. Fundamentos da escolha')
c2 = comp['Grupo 2']
d.subsecao('5.1 Mesmo critério adotado em 2025')
d.p(f"No inventário de 2025, o preço adotado ({brl(P25)}) foi o centroide do Grupo 2 do K-Means sobre os preços atualizados "
    f"pelo IPCA ({inv['criterio']}). A escolha do Grupo 2 em 2026 mantém o mesmo critério, o que preserva a comparabilidade "
    'entre exercícios, característica qualitativa da informação contábil exigida pela Estrutura Conceitual das NBC TSP. '
    'Mudar de critério a cada ano, conforme o resultado, comprometeria essa comparabilidade.')
d.subsecao('5.2 Estabilidade do grupo entre cenários')
d.p(f"O mesmo par de preços forma um grupo próprio em quase todos os cenários de sensibilidade, com o mesmo centroide:")
d.tabela(['Cenário', 'Posição do par de preços', 'Centroide ou composição'], estab,
         legenda='Tabela 6 - Presença do grupo nos cenários (preços atualizados)', larguras=[34, 26, 40])
d.p('A única exceção é o cenário que admite apenas compras com até 13 meses, no qual a Ref. 3 sai da amostra e a Ref. 7 '
    'fica isolada em um grupo de valor mais alto. O resultado não depende, portanto, da inclusão do valor atípico nem do contrato.')
d.subsecao('5.3 Preços formados em disputa competitiva e conferidos')
d.p(f"Os dois preços do grupo vieram de pregões eletrônicos, com disputa entre licitantes, e foram conferidos ao centavo com o "
    f"resultado homologado no PNCP. Em comparação, o Grupo 1 reúne {len(g1_ids)} preços de mercado"
    f"{' e o contrato' if 'Contrato' in G1['Preços do grupo'] else ''}; dos preços de mercado, "
    f"{len([i for i in g1_ids if i in sem_disputa])} vieram de contratações diretas, sem disputa de preço "
    f"(Ref. {', '.join(str(i) for i in g1_ids if i in sem_disputa)}), e "
    f"{len([i for i in g1_ids if i in fora_13])} têm mais de 13 meses (Ref. {', '.join(str(i) for i in g1_ids if i in fora_13)}).")
d.subsecao('5.4 Atualização monetária pelo IPCA')
d.p(f"Todos os preços foram atualizados pelo IPCA, índice oficial de preços ao consumidor apurado pelo IBGE, do mês de cada compra "
    f"até {data_base}, último mês publicado na data da pesquisa. O procedimento atende ao art. 23, § 1º, II, da Lei nº 14.133/2021, "
    'que admite contratações similares como parâmetro de preço desde que observado o índice de atualização correspondente, e '
    'coloca preços de datas diferentes na mesma data-base, condição para compará-los.')
d.subsecao('5.5 O preço do contrato vigente não representa o valor de mercado')
d.p(f"O Contrato nº 014/2022/SEPLAG é o objeto de referência da pesquisa, mas seu preço vigente ({brl(C)}) não serve como valor de "
    f"mercado do ponto de função: fica abaixo dos 9 preços atualizados; o preço original ({brl(CFG['contrato_referencia']['preco_original_pf'])}) "
    f"ficou {pct((1 - CFG['contrato_referencia']['preco_original_pf'] / 1252.60) * 100)} abaixo do valor estimado no edital do Pregão "
    f"Eletrônico nº 015/2021, que originou a ata aderida ({brl(1185.93)} a {brl(1252.60)} por PF, em 2021); e é reajustado pelo IGP-M, "
    'índice diferente do usado na pesquisa. O valor estimado naquele edital, resultado da pesquisa de mercado da época para o mesmo '
    f"objeto, está na mesma ordem de grandeza do preço aprovado, mesmo sem atualização desde 2021.")
d.subsecao('5.6 O preço de 2025 está desatualizado')
d.p(f"Nenhum dos 13 preços da pesquisa de 2025 atende à janela de 13 meses na data da pesquisa de 2026. Atualizado pelo IPCA "
    f"até {data_base}, o preço de 2025 equivale a {brl(P25_base)}. Na mesma data-base, os grupos de 2026 compararam-se assim com os de 2025:")
d.tabela(['Grupo', '2025 em ' + data_base, '2026 em ' + data_base, 'Variação real'],
         [[c['Grupo'], brl(c['2025 atualizado até 10/2026']), brl(c['2026 atualizado até 10/2026']),
           pct(c['Variação real, mesma data-base 10/2026'], True)] for c in R['comparacao_2025_2026']],
         legenda='Tabela 7 - Grupos de 2025 e 2026 na mesma data-base', numericas=[1, 2, 3], larguras=[34, 22, 22, 22],
         destaque_linhas=[DEC['grupo'] - 1])
d.p(f"Comparados na mesma data-base, os preços de mercado não caíram: o Grupo 1 subiu {pct(comp['Grupo 1']['Variação real, mesma data-base 10/2026'], True)} "
    f"e o Grupo 2, {pct(c2['Variação real, mesma data-base 10/2026'], True)}. A diferença do Grupo 2 decorre também da mudança de composição da amostra "
    'entre os anos, registrada na Manifestação da pesquisa.')
rg = DEC['rga']
d.subsecao('5.7 Evolução do custo interno de produção')
d.p(f"Os softwares avaliados são desenvolvidos majoritariamente por servidores. A revisão geral anual de 2026 ({rg['ato']}) "
    f"recompôs os subsídios em {pct(rg['percentual'], casas=2)}, acima dos {pct(rg['percentual_proposta_inicial'], casas=2)} da proposta inicial, "
    f"calculada pelo {rg['indice_proposta_inicial']}. O custo de pessoal que produz os ativos aumentou no período. "
    'Esse dado não determina o valor de mercado do ponto de função (art. 11, § 3º), mas é coerente com a escolha: '
    'não há indicação de redução do custo de produção que justifique reduzir o preço de referência.')

# 6
d.secao('🧩', '6. Contrapontos considerados')
d.p('Para que a escolha seja auditável, a comissão registra os argumentos contrários e as alternativas examinadas.')
d.tabela(['Contraponto', 'Consideração da comissão'], [
    [f'O grupo tem só {len(membros)} preços', 'É limitação reconhecida na pesquisa. É compensada pela estabilidade do grupo entre cenários (Tabela 6) e pela origem competitiva e conferida dos dois preços (5.3)'],
    [f"O preço fica acima da mediana ({brl(DA['Mediana'])}) e de {sum(1 for a in R['amostra_2026'] if a['Preço atualizado'] < preco)} dos 9 preços",
     'A mediana mistura preços com e sem disputa e de grupos distintos; o critério do inventário, desde 2025, é o centroide do grupo, não a mediana geral'],
    [f"A Ref. 3 tem mais de 13 meses", 'Sem ela, a Ref. 7 fica isolada com preço maior. A presença da Ref. 3 reduz o preço aprovado, não o eleva'],
    [f"Efeito sobre o inventário", f"Com o tamanho funcional de 2025 ({tam25} PF), a ordem de grandeza do grupo de softwares desenvolvidos internamente passaria de {brl(inv['valor_grupo_desenvolvidos_internamente'])} para cerca de {brl(efeito)} ({pct((preco / P25 - 1) * 100, True)}). O valor definitivo resulta das medições de 2026"],
], legenda='Tabela 8 - Contrapontos e considerações', larguras=[32, 68])
d.tabela(['Alternativa', 'Preço', 'Motivo de não adoção'], [
    ['Contrato nº 014/2022/SEPLAG', brl(C), 'Não representa valor de mercado (5.5)'],
    ['Grupo 1', brl(G1['Centroide (média)']), f"{len([i for i in g1_ids if i in sem_disputa])} dos {len(g1_ids)} preços de mercado sem disputa e {len([i for i in g1_ids if i in fora_13])} com mais de 13 meses (5.3); mudaria o critério de 2025 (5.1)"],
    ['Mediana dos 9 preços', brl(DA['Mediana']), 'Estatística geral, fora do critério de grupo adotado desde 2025'],
    ['Grupo 3', brl(grupos[2]['Centroide (média)']), 'Um único preço, valor atípico pelo intervalo interquartil, contratação direta sem disputa'],
    ['Preço de 2025', brl(P25), 'Referências com mais de 13 meses; desatualizado (5.6)'],
], legenda='Tabela 9 - Alternativas examinadas', numericas=[1], larguras=[28, 16, 56])

# 7
d.secao('📌', '7. Aprovação')
d.p(f"Com base no processo documentado na Manifestação Técnica da pesquisa de preços e nos fundamentos acima, a Comissão de "
    f"Inventário e Avaliação de Bens Intangíveis aprova o preço de **{brl(preco)} ({DEC['preco_por_extenso']})** por ponto de função, "
    f"data-base {data_base}, para a avaliação de todos os softwares medidos por pontos de função no inventário de 2026, nos termos "
    'do art. 11 da IN Conjunta nº 003/2022/SEPLAG/SEFAZ.')
d.p('Os documentos de referência, os dados brutos e os programas que reproduzem a análise acompanham o processo do inventário.')
r = DEC['responsavel']
d.assinatura('Responsável:', r['nome'], r['cargo'], *( [r['funcao']] if r.get('funcao') else [] ), f"{r['portaria']} - matrícula {r['matricula']}", DEC['cidade_data'])
d.p(f"Fonte da RGA: [Assembleia Legislativa de Mato Grosso]({rg['fonte']}).", alinhar='left')

if __name__ == '__main__':
    for x in d.salvar(AQUI / 'MANIFESTACAO_TECNICA_Aprovacao_Preco_PF_2026'):
        print('ok', x)
    print('preço', preco, 'refs', ids)
