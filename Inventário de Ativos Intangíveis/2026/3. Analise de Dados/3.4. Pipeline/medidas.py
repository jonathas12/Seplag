"""
Medidas DAX do modelo "Catálogo de Produtos de Software - Inventário 2026".

Cada medida: (nome, expressão DAX, formato, pasta, descrição). Usado por gera_pbip.py (tabela Medidas) e
por gera_documentacao.py (catálogo de medidas). O inventário de referência é 2026, salvo quando o visual
filtra outro inventário (medida [Ano Referência]).
"""
CUR = '"R$"\\ #,0.00;-"R$"\\ #,0.00;"R$"\\ #,0.00'
CUR0 = '"R$"\\ #,0;-"R$"\\ #,0;"R$"\\ #,0'
PCT = "0.0%;-0.0%;0.0%"
NUM1 = "#,0.0"
NUM0 = "#,0"
NUM2 = "#,0.00"
TXT = None

DEV = '"Desenvolvido internamente"'
LIC = '"Adquirido: licença"'
SEAP = '"Adquirido: contrato (SEAP)"'
FMT_R = '"""R$"" #,0.00"'          # FORMAT(x, "R$ #,0.00") com o R$ literal
FMT_MI = '"#,0.00"'


def ano_ref(expr):
    """Avalia expr no inventário de referência (2026 ou o inventário filtrado)."""
    return f"VAR _a = [Ano Referência]\nRETURN\n    CALCULATE ( {expr}, REMOVEFILTERS ( dInventario ), dInventario[Ano Inventário] = _a )"


def ano_ant(expr):
    return f"VAR _a = [Ano Referência]\nRETURN\n    CALCULATE ( {expr}, REMOVEFILTERS ( dInventario ), dInventario[Ano Inventário] = _a - 1 )"


def sel(col, padrao='"-"'):
    return f"SELECTEDVALUE ( dProduto[{col}], {padrao} )"


MEDIDAS = [
    # ------------------------------------------------------------------ 1. Base
    ("Valor Final (R$)", "SUM ( fAvaliacao[Valor Final VA (R$)] )", CUR, "1. Base", "Valor do ativo (VA) no contexto do visual."),
    ("Valor Bruto (R$)", "SUM ( fAvaliacao[Valor Bruto VT (R$)] )", CUR, "1. Base", "Valor do tamanho (VT = PF x preço do PF); nos adquiridos, igual ao valor de aquisição ou do contrato."),
    ("Tamanho Funcional (PF)", "SUM ( fAvaliacao[Tamanho Funcional (PF)] )", NUM1, "1. Base", "Pontos de função medidos."),
    ("Qtde Produtos", "DISTINCTCOUNT ( fAvaliacao[ID Produto] )", NUM0, "1. Base", "Produtos avaliados no contexto."),
    ("Ano Referência", "IF ( ISFILTERED ( dInventario[Ano Inventário] ) || ISFILTERED ( dInventario[Inventário] ), MAX ( dInventario[Ano Inventário] ), 2026 )",
     "0", "1. Base", "Inventário de referência: 2026, ou o inventário filtrado."),
    ("Valor Atual (R$)", ano_ref("[Valor Final (R$)]"), CUR, "1. Base", "Valor do ativo no inventário de referência."),
    ("Valor Anterior (R$)", ano_ant("[Valor Final (R$)]"), CUR, "1. Base", "Valor do ativo no inventário anterior ao de referência."),
    ("Variação Valor (R$)", "[Valor Atual (R$)] - [Valor Anterior (R$)]", CUR, "1. Base", "Diferença do valor sobre o inventário anterior."),
    ("% Variação Valor", "DIVIDE ( [Variação Valor (R$)], [Valor Anterior (R$)] )", PCT, "1. Base", "Variação percentual do valor."),
    ("PF Atual", ano_ref("[Tamanho Funcional (PF)]"), NUM1, "1. Base", "Pontos de função no inventário de referência."),
    ("PF Anterior", ano_ant("[Tamanho Funcional (PF)]"), NUM1, "1. Base", "Pontos de função no inventário anterior."),
    ("Variação PF", "[PF Atual] - [PF Anterior]", NUM1, "1. Base", "Diferença de pontos de função."),
    ("Qtde Produtos Atual", ano_ref("[Qtde Produtos]"), NUM0, "1. Base", "Produtos avaliados no inventário de referência."),
    ("VI Atual", ano_ref("AVERAGE ( fAvaliacao[Valor Institucional] )"), NUM2, "1. Base", "Valor Institucional (média, quando há mais de um produto)."),
    ("Valor Desenvolvidos (R$)", f"CALCULATE ( [Valor Atual (R$)], dProduto[Categoria] = {DEV} )", CUR, "1. Base", "Valor dos softwares desenvolvidos internamente."),
    ("Valor Licenças (R$)", f"CALCULATE ( [Valor Atual (R$)], dProduto[Categoria] = {LIC} )", CUR, "1. Base", "Valor das licenças e softwares de prateleira."),
    ("Valor SEAP (R$)", f"CALCULATE ( [Valor Atual (R$)], dProduto[Categoria] = {SEAP} )", CUR, "1. Base", "Valor do SEAP (contrato)."),
    ("Valor Adquiridos (R$)", "[Valor Licenças (R$)] + [Valor SEAP (R$)]", CUR, "1. Base", "Licenças e SEAP."),
    ("Qtde Desenvolvidos", f"CALCULATE ( [Qtde Produtos Atual], dProduto[Categoria] = {DEV} )", NUM0, "1. Base", "Softwares desenvolvidos internamente."),
    ("Qtde Licenças", f"CALCULATE ( [Qtde Produtos Atual], dProduto[Categoria] = {LIC} )", NUM0, "1. Base", "Licenças avaliadas."),
    ("Qtde Adquiridos", f"CALCULATE ( [Qtde Produtos Atual], dProduto[Categoria] <> {DEV} )", NUM0, "1. Base", "Licenças e SEAP."),
    ("% Participação", "DIVIDE ( [Valor Atual (R$)], CALCULATE ( [Valor Atual (R$)], ALLSELECTED ( dProduto ) ) )", PCT, "1. Base", "Participação no valor do recorte."),
    ("Posição no Ranking", "IF ( HASONEVALUE ( dProduto[ID Produto] ), RANKX ( ALLSELECTED ( dProduto[ID Produto] ), [Valor Atual (R$)], , DESC, DENSE ) )",
     NUM0, "1. Base", "Posição do produto pelo valor."),
    # ------------------------------------------------------------------ 2. Governança
    ("Qtde Sem Documentação", f'CALCULATE ( COUNTROWS ( dProduto ), dProduto[Documentação] = "Ausente", dProduto[Categoria] = {DEV} )', NUM0, "2. Governança",
     "Desenvolvidos sem documentação funcional disponibilizada (2ª Nota Técnica)."),
    ("Valor Sem Documentação (R$)", 'CALCULATE ( [Valor Atual (R$)], dProduto[Documentação] = "Ausente" )', CUR, "2. Governança", "Valor dos sistemas sem documentação funcional."),
    ("Qtde Sem Uso ou Suspensos", 'CALCULATE ( COUNTROWS ( dProduto ), dProduto[Situação Resumida] IN { "Em produção, sem uso", "Em desenvolvimento (suspenso)" } )',
     NUM0, "2. Governança", "SEI, SIGS e SIFSW."),
    ("Valor Sem Uso ou Suspensos (R$)", 'CALCULATE ( [Valor Atual (R$)], dProduto[Situação Resumida] IN { "Em produção, sem uso", "Em desenvolvimento (suspenso)" } )',
     CUR, "2. Governança", "Valor dos sistemas sem uso ou suspensos."),
    ("Qtde Em Desenvolvimento", 'CALCULATE ( COUNTROWS ( dProduto ), dProduto[Situação Resumida] = "Em desenvolvimento" )', NUM0, "2. Governança",
     "Projetos em desenvolvimento (situação do laudo)."),
    ("Qtde Licenças Encerradas", 'CALCULATE ( COUNTROWS ( dProduto ), dProduto[Situação Resumida] = "Licença com cessão encerrada" )', NUM0, "2. Governança",
     "Cessões encerradas ainda registradas."),
    ("Valor Licenças Encerradas (R$)", 'CALCULATE ( [Valor Atual (R$)], dProduto[Situação Resumida] = "Licença com cessão encerrada" )', CUR, "2. Governança",
     "Valor das cessões encerradas."),
    ("Qtde Diligências", "DISTINCTCOUNT ( bProdutoDiligencia[Código] )", NUM0, "2. Governança", "Diligências que alcançam os produtos do recorte."),
    ("Qtde Diligências Prioritárias", 'CALCULATE ( DISTINCTCOUNT ( bProdutoDiligencia[Código] ), dDiligencia[Prioritária] = "Sim" )', NUM0, "2. Governança",
     "Diligências com prazo até 10/12/2026."),
    ("Produtos Alcançados", "DISTINCTCOUNT ( bProdutoDiligencia[ID Produto] )", NUM0, "2. Governança", "Produtos alcançados pela diligência."),
    # ------------------------------------------------------------------ 3. Adquiridos e SEAP
    ("Amortização Acumulada 31/12 (R$)", "CALCULATE ( MAX ( fAmortizacaoSEAP[Amortização Acumulada (R$)] ), fAmortizacaoSEAP[Parcela] = 11 )", CUR, "3. Adquiridos",
     "Amortização do SEAP acumulada até o fim do exercício."),
    ("Valor Líquido SEAP 31/12 (R$)", "CALCULATE ( MIN ( fAmortizacaoSEAP[Valor Contábil Líquido (R$)] ), fAmortizacaoSEAP[Parcela] = 11 )", CUR, "3. Adquiridos",
     "Valor contábil líquido do SEAP em 31/12/2026."),
    ("Valor Líquido SEAP (R$)", "SUM ( fAmortizacaoSEAP[Valor Contábil Líquido (R$)] )", CUR, "3. Adquiridos", "Valor líquido ao fim de cada parcela."),
    ("Amortização do Mês (R$)", "SUM ( fAmortizacaoSEAP[Amortização do Mês (R$)] )", CUR, "3. Adquiridos", "Parcela mensal (cláusula 4.2)."),
    ("Valor Líquido do Inventário 31/12 (R$)",
     "CALCULATE ( [Valor Atual (R$)], REMOVEFILTERS ( dProduto ) ) - [Amortização Acumulada 31/12 (R$)]", CUR, "3. Adquiridos",
     "Valor apurado menos a amortização do SEAP até 31/12/2026."),
    # ------------------------------------------------------------------ 4. Economicidade
    ("Custo Pago (R$)", "SUM ( fEconomicidade[Custo Total Pago (R$)] )", CUR, "4. Economicidade", "Pago à fábrica de software (Contrato nº 014/2022), TRDs até 07/2026."),
    ("Custo de Construção (R$)", "SUM ( fEconomicidade[Custo de Construção (R$)] )", CUR, "4. Economicidade", "Componentes de desenvolvimento (sem tickets e PFT)."),
    ("PF Faturado", "SUM ( fEconomicidade[PF Faturado] )", NUM1, "4. Economicidade", "Pontos de função faturados ao longo dos projetos."),
    ("PF Equivalentes Pagos", "SUM ( fEconomicidade[PF Equivalentes Pagos] )", NUM1, "4. Economicidade", "Custo pago dividido pelo preço do PF no contrato."),
    ("Custo Médio por PF Faturado (R$)", "DIVIDE ( [Custo Pago (R$)], [PF Faturado] )", CUR, "4. Economicidade", "Custo pago dividido pelos PF faturados."),
    ("Preço PF Mercado (R$)", "CALCULATE ( MAX ( dInventario[Preço PF Mercado (R$)] ), REMOVEFILTERS ( dInventario ), dInventario[Ano Inventário] = 2026 )", CUR,
     "4. Economicidade", "Preço de referência do PF aprovado para o inventário de 2026."),
    ("Preço PF Contrato Vigente (R$)", 'CALCULATE ( MAX ( dPrecoPF[Preço PF (R$)] ), dPrecoPF[Tipo] = "Contrato" )', CUR, "4. Economicidade",
     "Preço vigente do PF no Contrato nº 014/2022/SEPLAG."),
    ("Custo a Preço de Mercado (R$)", "SUM ( fEconomicidade[Custo do Volume a Preço de Mercado (R$)] )", CUR, "4. Economicidade",
     "O mesmo serviço pago (mesmos PF, percentuais e deflatores) ao preço de referência do PF de 2026, em vez do preço do contrato informado no laudo."),
    ("Economia vs Mercado (R$)", "[Custo a Preço de Mercado (R$)] - [Custo Pago (R$)]", CUR, "4. Economicidade", "Quanto a administração deixou de pagar."),
    ("% Economia", "DIVIDE ( [Economia vs Mercado (R$)], [Custo a Preço de Mercado (R$)] )", PCT, "4. Economicidade", "Economia sobre o custo de mercado."),
    ("VT Sistemas com Custo (R$)", "SUM ( fEconomicidade[VT 2026 (R$)] )", CUR, "4. Economicidade", "Valor do produto (VT 2026) dos sistemas com custo registrado."),
    ("VA Sistemas com Custo (R$)", "SUM ( fEconomicidade[VA 2026 (R$)] )", CUR, "4. Economicidade", "Valor do ativo (VA 2026) dos sistemas com custo registrado."),
    ("Retorno Produto por R$ 1", "DIVIDE ( [VT Sistemas com Custo (R$)], [Custo Pago (R$)] )", '"R$"\\ #,0.00', "4. Economicidade",
     "Valor do produto (VT) gerado a cada R$ 1,00 pago à fábrica."),
    ("Retorno Ativo por R$ 1", "DIVIDE ( [VA Sistemas com Custo (R$)], [Custo Pago (R$)] )", '"R$"\\ #,0.00', "4. Economicidade",
     "Valor do ativo (VA) gerado a cada R$ 1,00 pago à fábrica."),
    ("Qtde Sistemas com Custo", "COUNTROWS ( fEconomicidade )", NUM0, "4. Economicidade", "Sistemas com custo de projeto registrado nos laudos."),
    # ------------------------------------------------------------------ 5. Produto (ficha)
    ("Ficha Produto", sel("Nome do Produto", '"Selecione um produto"'), TXT, "5. Produto", "Nome do produto selecionado."),
    ("Ficha Sigla", sel("Sigla"), TXT, "5. Produto", ""),
    ("Ficha Categoria", sel("Categoria"), TXT, "5. Produto", ""),
    ("Ficha Situação", sel("Situação"), TXT, "5. Produto", ""),
    ("Ficha Tecnologia", sel("Tecnologia"), TXT, "5. Produto", ""),
    ("Ficha Nível", sel("Nível de Medição"), TXT, "5. Produto", ""),
    ("Ficha Medida", sel("Medida PF"), TXT, "5. Produto", ""),
    ("Ficha Vida Útil", sel("Vida Útil"), TXT, "5. Produto", ""),
    ("Ficha Faixa VI", sel("Faixa Valor Institucional"), TXT, "5. Produto", ""),
    ("Ficha Finalidade", sel("Finalidade"), TXT, "5. Produto", ""),
    ("Ficha Benefício", sel("Benefício"), TXT, "5. Produto", ""),
    ("Ficha Base Legal", sel("Base Legal"), TXT, "5. Produto", ""),
    ("Ficha Áreas", sel("Áreas de Negócio"), TXT, "5. Produto", ""),
    ("Ficha Justificativa VI", sel("Justificativa do VI"), TXT, "5. Produto", ""),
    ("Ficha Documentação", sel("Documentação"), TXT, "5. Produto", ""),
    ("Ficha Achado", sel("Principal Achado"), TXT, "5. Produto", ""),
    ("Ficha Diligências", sel("Diligências"), TXT, "5. Produto", ""),
    ("Ficha Laudo", sel("Laudo"), TXT, "5. Produto", ""),
    ("Ficha Fornecedor", sel("Fornecedor"), TXT, "5. Produto", ""),
    ("Ficha Unidade", sel("Unidade de Desenvolvimento"), TXT, "5. Produto", ""),
    ("PF Módulo", "SUM ( fModulo[Tamanho Funcional (PF)] )", NUM1, "5. Produto", "Pontos de função por módulo (laudo)."),
    ("Qtde Funções", "SUM ( fFuncao[Qtde Funções] )", NUM0, "5. Produto", "Funções contadas por tipo (laudo)."),
    ("PF por Tipo de Função", "SUM ( fFuncao[Tamanho Funcional (PF)] )", NUM1, "5. Produto", "Pontos de função por tipo (ALI, AIE, EE, CE, SE)."),
    ("Qtde Integrações", "COUNTROWS ( fIntegracao )", NUM0, "5. Produto", "Integrações registradas no laudo."),
    ("PF Histórico (laudo)", "SUM ( fHistoricoLaudo[Tamanho Funcional (PF)] )", NUM1, "5. Produto", "Medições registradas no histórico do laudo."),
    # ------------------------------------------------------------------ 6. Narrativas
    ("Texto Valor Atual", f'FORMAT ( [Valor Atual (R$)] / 1000000, {FMT_MI} ) & " mi"', TXT, "6. Narrativas", "Valor atual em milhões."),
    ("Texto Variação", 'VAR v = [% Variação Valor] RETURN IF ( ISBLANK ( v ), "primeiro inventário", IF ( v >= 0, "+", "" ) & FORMAT ( v, "0.0%" ) & " sobre " & ( [Ano Referência] - 1 ) )',
     TXT, "6. Narrativas", "Variação sobre o inventário anterior."),
    ("Leitura Visão Geral",
     'VAR a = [Ano Referência] VAR n = [Qtde Produtos Atual] VAR d = [Qtde Desenvolvidos] VAR v = [Valor Atual (R$)] VAR vd = [Valor Desenvolvidos (R$)]\n'
     'RETURN "Inventário " & a & ": " & n & " produtos, avaliados em R$ " & FORMAT ( v / 1000000, "#,0.00" ) & " milhões (" & [Texto Variação] & "). "\n'
     '    & d & " softwares desenvolvidos internamente respondem por " & FORMAT ( DIVIDE ( vd, v ), "0.0%" ) & " do valor; " & [Qtde Sem Documentação] & " deles não têm documentação funcional."',
     TXT, "6. Narrativas", "Leitura rápida da Visão Geral."),
    ("Leitura Desenvolvidos",
     'VAR n = [Qtde Desenvolvidos] RETURN n & " sistemas, " & FORMAT ( CALCULATE ( [PF Atual], dProduto[Categoria] = "Desenvolvido internamente" ), "#,0.0" ) & " PF e R$ "\n'
     '    & FORMAT ( [Valor Desenvolvidos (R$)] / 1000000, "#,0.00" ) & " milhões. " & [Qtde Sem Uso ou Suspensos] & " sem uso ou suspensos e " & [Qtde Em Desenvolvimento]\n'
     '    & " em desenvolvimento dependem das diligências da 2ª Nota Técnica."',
     TXT, "6. Narrativas", "Leitura rápida dos desenvolvidos."),
    ("Leitura Adquiridos",
     '[Qtde Licenças] & " licenças (R$ " & FORMAT ( [Valor Licenças (R$)] / 1000000, "#,0.00" ) & " mi) e o SEAP (R$ " & FORMAT ( [Valor SEAP (R$)] / 1000000, "#,0.00" )\n'
     '    & " mi, amortizado em 12 meses). " & [Qtde Licenças Encerradas] & " cessões encerradas em 19/07/2026 continuam registradas: confirmar renovação ou baixa."',
     TXT, "6. Narrativas", "Leitura rápida dos adquiridos."),
    ("Leitura Economicidade",
     '"Nos " & [Qtde Sistemas com Custo] & " sistemas com custo registrado, a SEPLAG pagou R$ " & FORMAT ( [Custo Pago (R$)] / 1000000, "#,0.00" )\n'
     '    & " mi à fábrica. O mesmo serviço ao preço de mercado do PF custaria R$ " & FORMAT ( [Custo a Preço de Mercado (R$)] / 1000000, "#,0.00" )\n'
     '    & " mi: economia de " & FORMAT ( [% Economia], "0.0%" ) & ". Cada R$ 1,00 pago gerou R$ " & FORMAT ( [Retorno Ativo por R$ 1], "0.00" ) & " em valor do ativo."',
     TXT, "6. Narrativas", "Leitura rápida da economicidade."),
    ("Leitura Operacional",
     'COUNTROWS ( dProduto ) & " produtos no recorte · " & [Qtde Diligências] & " diligências aplicáveis · " & [Qtde Diligências Prioritárias] & " prioritárias até 10/12/2026"',
     TXT, "6. Narrativas", "Resumo do recorte da visão operacional."),
    # ------------------------------------------------------------------ 7. Cores (formatação condicional)
    ("Cor Situação",
     'SWITCH ( SELECTEDVALUE ( dProduto[Situação Resumida] ), "Em produção", "#155C78", "Licença vigente", "#155C78", "Em desenvolvimento", "#6FA0B3", "Em produção (legado em sucessão)", "#C77A3F",\n'
     '    "Em produção, sem uso", "#FF8C42", "Em desenvolvimento (suspenso)", "#FF8C42", "Licença com cessão encerrada", "#FF8C42", "#5E7C88" )',
     TXT, "7. Cores", "Cor da situação: laranja indica ressalva."),
    ("Cor Documentação",
     'SWITCH ( SELECTEDVALUE ( dProduto[Documentação] ), "Ausente", "#FF8C42", "Com lacunas", "#C77A3F", "Parcial", "#6FA0B3", "Adequada", "#155C78", "#5E7C88" )',
     TXT, "7. Cores", "Cor da classificação da documentação."),
    ("Cor Economia", 'IF ( [Custo Médio por PF Faturado (R$)] <= [Preço PF Mercado (R$)], "#155C78", "#FF8C42" )', TXT, "7. Cores", ""),
]
