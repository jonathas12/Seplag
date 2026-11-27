# Catálogo de medidas DAX

Gerado por `gera_documentacao.py` a partir de `medidas.py`.

## 1. Base

### Valor Final (R$)

Valor do ativo (VA) no contexto do visual.

```dax
SUM ( fAvaliacao[Valor Final VA (R$)] )
```

### Valor Bruto (R$)

Valor do tamanho (VT = PF x preço do PF); nos adquiridos, igual ao valor de aquisição ou do contrato.

```dax
SUM ( fAvaliacao[Valor Bruto VT (R$)] )
```

### Tamanho Funcional (PF)

Pontos de função medidos.

```dax
SUM ( fAvaliacao[Tamanho Funcional (PF)] )
```

### Qtde Produtos

Produtos avaliados no contexto.

```dax
DISTINCTCOUNT ( fAvaliacao[ID Produto] )
```

### Ano Referência

Inventário de referência: 2026, ou o inventário filtrado.

```dax
IF ( ISFILTERED ( dInventario[Ano Inventário] ) || ISFILTERED ( dInventario[Inventário] ), MAX ( dInventario[Ano Inventário] ), 2026 )
```

### Valor Atual (R$)

Valor do ativo no inventário de referência.

```dax
VAR _a = [Ano Referência]
RETURN
    CALCULATE ( [Valor Final (R$)], REMOVEFILTERS ( dInventario ), dInventario[Ano Inventário] = _a )
```

### Valor Anterior (R$)

Valor do ativo no inventário anterior ao de referência.

```dax
VAR _a = [Ano Referência]
RETURN
    CALCULATE ( [Valor Final (R$)], REMOVEFILTERS ( dInventario ), dInventario[Ano Inventário] = _a - 1 )
```

### Variação Valor (R$)

Diferença do valor sobre o inventário anterior.

```dax
[Valor Atual (R$)] - [Valor Anterior (R$)]
```

### % Variação Valor

Variação percentual do valor sobre o inventário anterior.

```dax
DIVIDE ( [Variação Valor (R$)], [Valor Anterior (R$)] )
```

### PF Atual

Pontos de função no inventário de referência.

```dax
VAR _a = [Ano Referência]
RETURN
    CALCULATE ( [Tamanho Funcional (PF)], REMOVEFILTERS ( dInventario ), dInventario[Ano Inventário] = _a )
```

### PF Anterior

Pontos de função no inventário anterior.

```dax
VAR _a = [Ano Referência]
RETURN
    CALCULATE ( [Tamanho Funcional (PF)], REMOVEFILTERS ( dInventario ), dInventario[Ano Inventário] = _a - 1 )
```

### Variação PF

Diferença de pontos de função.

```dax
[PF Atual] - [PF Anterior]
```

### Qtde Produtos Atual

Produtos avaliados no inventário de referência.

```dax
VAR _a = [Ano Referência]
RETURN
    CALCULATE ( [Qtde Produtos], REMOVEFILTERS ( dInventario ), dInventario[Ano Inventário] = _a )
```

### VI Atual

Valor Institucional (média, quando há mais de um produto).

```dax
VAR _a = [Ano Referência]
RETURN
    CALCULATE ( AVERAGE ( fAvaliacao[Valor Institucional] ), REMOVEFILTERS ( dInventario ), dInventario[Ano Inventário] = _a )
```

### Valor Desenvolvidos (R$)

Valor dos softwares desenvolvidos internamente.

```dax
CALCULATE ( [Valor Atual (R$)], dProduto[Categoria] = "Desenvolvido internamente" )
```

### Valor Licenças (R$)

Valor das licenças e softwares de prateleira.

```dax
CALCULATE ( [Valor Atual (R$)], dProduto[Categoria] = "Adquirido: licença" )
```

### Valor SEAP (R$)

Valor do SEAP (contrato).

```dax
CALCULATE ( [Valor Atual (R$)], dProduto[Categoria] = "Adquirido: contrato (SEAP)" )
```

### Valor Adquiridos (R$)

Licenças e SEAP.

```dax
[Valor Licenças (R$)] + [Valor SEAP (R$)]
```

### Qtde Desenvolvidos

Softwares desenvolvidos internamente.

```dax
CALCULATE ( [Qtde Produtos Atual], dProduto[Categoria] = "Desenvolvido internamente" )
```

### Qtde Licenças

Licenças avaliadas.

```dax
CALCULATE ( [Qtde Produtos Atual], dProduto[Categoria] = "Adquirido: licença" )
```

### Qtde Adquiridos

Licenças e SEAP.

```dax
CALCULATE ( [Qtde Produtos Atual], dProduto[Categoria] <> "Desenvolvido internamente" )
```

### % Participação

Participação no valor do recorte.

```dax
DIVIDE ( [Valor Atual (R$)], CALCULATE ( [Valor Atual (R$)], ALLSELECTED ( dProduto ) ) )
```

### Posição no Ranking

Posição do produto pelo valor.

```dax
IF ( HASONEVALUE ( dProduto[ID Produto] ), RANKX ( ALLSELECTED ( dProduto ), [Valor Atual (R$)], , DESC, DENSE ) )
```

## 2. Governança

### Qtde Sem Documentação

Desenvolvidos sem documentação funcional disponibilizada (3ª Nota Técnica).

```dax
CALCULATE ( COUNTROWS ( dProduto ), dProduto[Documentação] = "Ausente", dProduto[Categoria] = "Desenvolvido internamente" )
```

### Valor Sem Documentação (R$)

Valor dos sistemas sem documentação funcional.

```dax
CALCULATE ( [Valor Atual (R$)], dProduto[Documentação] = "Ausente" )
```

### Qtde Sem Uso ou Suspensos

SEI, SIGS e SIFSW.

```dax
CALCULATE ( COUNTROWS ( dProduto ), dProduto[Situação Resumida] IN { "Em produção, sem uso", "Em desenvolvimento (suspenso)" } )
```

### Valor Sem Uso ou Suspensos (R$)

Valor dos sistemas sem uso ou suspensos.

```dax
CALCULATE ( [Valor Atual (R$)], dProduto[Situação Resumida] IN { "Em produção, sem uso", "Em desenvolvimento (suspenso)" } )
```

### Qtde Em Desenvolvimento

Projetos em desenvolvimento (situação do laudo).

```dax
CALCULATE ( COUNTROWS ( dProduto ), dProduto[Situação Resumida] = "Em desenvolvimento" )
```

### Qtde Licenças Encerradas

Cessões encerradas ainda registradas.

```dax
CALCULATE ( COUNTROWS ( dProduto ), dProduto[Situação Resumida] = "Licença com cessão encerrada" )
```

### Valor Licenças Encerradas (R$)

Valor das cessões encerradas.

```dax
CALCULATE ( [Valor Atual (R$)], dProduto[Situação Resumida] = "Licença com cessão encerrada" )
```

### Qtde Diligências

Diligências que alcançam os produtos do recorte.

```dax
DISTINCTCOUNT ( bProdutoDiligencia[Código] )
```

### Qtde Diligências Prioritárias

Diligências com prazo até 10/12/2026.

```dax
CALCULATE ( DISTINCTCOUNT ( bProdutoDiligencia[Código] ), dDiligencia[Prioritária] = "Sim" )
```

### Produtos Alcançados

Produtos alcançados pela diligência.

```dax
DISTINCTCOUNT ( bProdutoDiligencia[ID Produto] )
```

## 3. Adquiridos

### Amortização Acumulada 31/12 (R$)

Amortização do SEAP acumulada até o fim do exercício.

```dax
CALCULATE ( MAX ( fAmortizacaoSEAP[Amortização Acumulada (R$)] ), fAmortizacaoSEAP[Parcela] = 11 )
```

### Valor Líquido SEAP 31/12 (R$)

Valor contábil líquido do SEAP em 31/12/2026.

```dax
CALCULATE ( MIN ( fAmortizacaoSEAP[Valor Contábil Líquido (R$)] ), fAmortizacaoSEAP[Parcela] = 11 )
```

### Valor Líquido SEAP (R$)

Valor líquido ao fim de cada parcela.

```dax
SUM ( fAmortizacaoSEAP[Valor Contábil Líquido (R$)] )
```

### Amortização do Mês (R$)

Parcela mensal (cláusula 4.2).

```dax
SUM ( fAmortizacaoSEAP[Amortização do Mês (R$)] )
```

### Valor Líquido do Inventário 31/12 (R$)

Valor apurado menos a amortização do SEAP até 31/12/2026.

```dax
CALCULATE ( [Valor Atual (R$)], REMOVEFILTERS ( dProduto ) ) - [Amortização Acumulada 31/12 (R$)]
```

## 4. Economicidade

### Custo Pago (R$)

Pago à fábrica de software (Contrato nº 014/2022), TRDs até 07/2026.

```dax
SUM ( fEconomicidade[Custo Total Pago (R$)] )
```

### Custo de Construção (R$)

Componentes de desenvolvimento (sem tickets e PFT).

```dax
SUM ( fEconomicidade[Custo de Construção (R$)] )
```

### PF Faturado

Pontos de função faturados ao longo dos projetos.

```dax
SUM ( fEconomicidade[PF Faturado] )
```

### PF Equivalentes Pagos

Custo pago dividido pelo preço do PF no contrato.

```dax
SUM ( fEconomicidade[PF Equivalentes Pagos] )
```

### Custo Médio por PF Faturado (R$)

Custo pago dividido pelos PF faturados.

```dax
DIVIDE ( [Custo Pago (R$)], [PF Faturado] )
```

### Preço PF Mercado (R$)

Preço de referência do PF aprovado para o inventário de 2026.

```dax
CALCULATE ( MAX ( dInventario[Preço PF Mercado (R$)] ), REMOVEFILTERS ( dInventario ), dInventario[Ano Inventário] = 2026 )
```

### Preço PF Contrato Vigente (R$)

Preço vigente do PF no Contrato nº 014/2022/SEPLAG.

```dax
CALCULATE ( MAX ( dPrecoPF[Preço PF (R$)] ), dPrecoPF[Tipo] = "Contrato" )
```

### Custo a Preço de Mercado (R$)

O mesmo serviço pago (mesmos PF, percentuais e deflatores) ao preço de referência do PF de 2026, em vez do preço do contrato informado no laudo.

```dax
SUM ( fEconomicidade[Custo do Volume a Preço de Mercado (R$)] )
```

### Economia vs Mercado (R$)

Quanto a administração deixou de pagar.

```dax
[Custo a Preço de Mercado (R$)] - [Custo Pago (R$)]
```

### % Economia

Economia sobre o custo de mercado.

```dax
DIVIDE ( [Economia vs Mercado (R$)], [Custo a Preço de Mercado (R$)] )
```

### VT Sistemas com Custo (R$)

Valor do produto (VT 2026) dos sistemas com custo registrado.

```dax
SUM ( fEconomicidade[VT 2026 (R$)] )
```

### VA Sistemas com Custo (R$)

Valor do ativo (VA 2026) dos sistemas com custo registrado.

```dax
SUM ( fEconomicidade[VA 2026 (R$)] )
```

### Retorno Produto por R$ 1

Valor do produto (VT) gerado a cada R$ 1,00 pago à fábrica.

```dax
DIVIDE ( [VT Sistemas com Custo (R$)], [Custo Pago (R$)] )
```

### Retorno Ativo por R$ 1

Valor do ativo (VA) gerado a cada R$ 1,00 pago à fábrica.

```dax
DIVIDE ( [VA Sistemas com Custo (R$)], [Custo Pago (R$)] )
```

### Qtde Sistemas com Custo

Sistemas com custo de projeto registrado nos laudos.

```dax
COUNTROWS ( fEconomicidade )
```

## 5. Produto

### Ficha Produto

Nome do produto selecionado.

```dax
SELECTEDVALUE ( dProduto[Nome do Produto], "Selecione um produto" )
```

### Ficha Sigla



```dax
SELECTEDVALUE ( dProduto[Sigla], "-" )
```

### Ficha Categoria



```dax
SELECTEDVALUE ( dProduto[Categoria], "-" )
```

### Ficha Situação



```dax
SELECTEDVALUE ( dProduto[Situação], "-" )
```

### Ficha Tecnologia



```dax
SELECTEDVALUE ( dProduto[Tecnologia], "-" )
```

### Ficha Nível



```dax
SELECTEDVALUE ( dProduto[Nível de Medição], "-" )
```

### Ficha Medida



```dax
SELECTEDVALUE ( dProduto[Medida PF], "-" )
```

### Ficha Vida Útil



```dax
SELECTEDVALUE ( dProduto[Vida Útil], "-" )
```

### Ficha Faixa VI



```dax
SELECTEDVALUE ( dProduto[Faixa Valor Institucional], "-" )
```

### Ficha Finalidade



```dax
SELECTEDVALUE ( dProduto[Finalidade], "-" )
```

### Ficha Benefício



```dax
SELECTEDVALUE ( dProduto[Benefício], "-" )
```

### Ficha Base Legal



```dax
SELECTEDVALUE ( dProduto[Base Legal], "-" )
```

### Ficha Áreas



```dax
SELECTEDVALUE ( dProduto[Áreas de Negócio], "-" )
```

### Ficha Justificativa VI



```dax
SELECTEDVALUE ( dProduto[Justificativa do VI], "-" )
```

### Ficha Documentação



```dax
SELECTEDVALUE ( dProduto[Documentação], "-" )
```

### Ficha Achado



```dax
SELECTEDVALUE ( dProduto[Principal Achado], "-" )
```

### Ficha Diligências



```dax
SELECTEDVALUE ( dProduto[Diligências], "-" )
```

### Ficha Laudo



```dax
SELECTEDVALUE ( dProduto[Laudo], "-" )
```

### Ficha Fornecedor



```dax
SELECTEDVALUE ( dProduto[Fornecedor], "-" )
```

### Ficha Unidade



```dax
SELECTEDVALUE ( dProduto[Unidade de Desenvolvimento], "-" )
```

### PF Módulo

Pontos de função por módulo (laudo).

```dax
SUM ( fModulo[Tamanho Funcional (PF)] )
```

### Qtde Funções

Funções contadas por tipo (laudo).

```dax
SUM ( fFuncao[Qtde Funções] )
```

### PF por Tipo de Função

Pontos de função por tipo (ALI, AIE, EE, CE, SE).

```dax
SUM ( fFuncao[Tamanho Funcional (PF)] )
```

### Qtde Integrações

Integrações registradas no laudo.

```dax
COUNTROWS ( fIntegracao )
```

### PF Histórico (laudo)

Medições registradas no histórico do laudo.

```dax
SUM ( fHistoricoLaudo[Tamanho Funcional (PF)] )
```

## 6. Narrativas

### Texto Valor Atual

Valor atual em milhões.

```dax
FORMAT ( [Valor Atual (R$)] / 1000000, "#,0.00" ) & " mi"
```

### Texto Variação

Variação sobre o inventário anterior.

```dax
VAR v = [% Variação Valor] RETURN IF ( ISBLANK ( v ), "primeiro inventário", IF ( v >= 0, "+", "" ) & FORMAT ( v, "0.0%" ) & " sobre " & ( [Ano Referência] - 1 ) )
```

### Leitura Visão Geral

Leitura rápida da Visão Geral.

```dax
VAR a = [Ano Referência] VAR n = [Qtde Produtos Atual] VAR d = [Qtde Desenvolvidos] VAR v = [Valor Atual (R$)] VAR vd = [Valor Desenvolvidos (R$)]
RETURN "Inventário " & a & ": " & n & " produtos, avaliados em R$ " & FORMAT ( v / 1000000, "#,0.00" ) & " milhões (" & [Texto Variação] & "). "
    & d & " softwares desenvolvidos internamente respondem por " & FORMAT ( DIVIDE ( vd, v ), "0.0%" ) & " do valor; " & [Qtde Sem Documentação] & " deles não têm documentação funcional."
```

### Leitura Desenvolvidos

Leitura rápida dos desenvolvidos.

```dax
VAR n = [Qtde Desenvolvidos] RETURN n & " sistemas, " & FORMAT ( CALCULATE ( [PF Atual], dProduto[Categoria] = "Desenvolvido internamente" ), "#,0.0" ) & " PF e R$ "
    & FORMAT ( [Valor Desenvolvidos (R$)] / 1000000, "#,0.00" ) & " milhões. " & [Qtde Sem Uso ou Suspensos] & " sem uso ou suspensos e " & [Qtde Em Desenvolvimento]
    & " em desenvolvimento dependem das diligências da 3ª Nota Técnica."
```

### Leitura Adquiridos

Leitura rápida dos adquiridos.

```dax
[Qtde Licenças] & " licenças (R$ " & FORMAT ( [Valor Licenças (R$)] / 1000000, "#,0.00" ) & " mi) e o SEAP (R$ " & FORMAT ( [Valor SEAP (R$)] / 1000000, "#,0.00" )
    & " mi, amortizado em 12 meses). " & [Qtde Licenças Encerradas] & " cessões encerradas em 19/07/2026 continuam registradas: confirmar renovação ou baixa."
```

### Leitura Economicidade

Leitura rápida da economicidade.

```dax
"Nos " & [Qtde Sistemas com Custo] & " sistemas com custo registrado, a SEPLAG pagou R$ " & FORMAT ( [Custo Pago (R$)] / 1000000, "#,0.00" )
    & " mi à fábrica. O mesmo serviço ao preço de mercado do PF custaria R$ " & FORMAT ( [Custo a Preço de Mercado (R$)] / 1000000, "#,0.00" )
    & " mi: economia de " & FORMAT ( [% Economia], "0.0%" ) & ". Cada R$ 1,00 pago gerou R$ " & FORMAT ( [Retorno Ativo por R$ 1], "0.00" ) & " em valor do ativo."
```

### Leitura Operacional

Resumo do recorte da visão operacional.

```dax
COUNTROWS ( dProduto ) & " produtos no recorte · " & [Qtde Diligências] & " diligências aplicáveis · " & [Qtde Diligências Prioritárias] & " prioritárias até 10/12/2026"
```

## 7. Cores

### Cor Situação

Cor da situação: laranja indica ressalva.

```dax
SWITCH ( SELECTEDVALUE ( dProduto[Situação Resumida] ), "Em produção", "#155C78", "Licença vigente", "#155C78", "Em desenvolvimento", "#6FA0B3", "Em produção (legado em sucessão)", "#C77A3F",
    "Em produção, sem uso", "#FF8C42", "Em desenvolvimento (suspenso)", "#FF8C42", "Licença com cessão encerrada", "#FF8C42", "#5E7C88" )
```

### Cor Documentação

Cor da classificação da documentação.

```dax
SWITCH ( SELECTEDVALUE ( dProduto[Documentação] ), "Ausente", "#FF8C42", "Com lacunas", "#C77A3F", "Parcial", "#6FA0B3", "Adequada", "#155C78", "#5E7C88" )
```

### Cor Economia



```dax
IF ( [Custo Médio por PF Faturado (R$)] <= [Preço PF Mercado (R$)], "#155C78", "#FF8C42" )
```

## 8. Contexto

### Qtde Produtos Anterior

Produtos avaliados no inventário anterior.

```dax
VAR _a = [Ano Referência]
RETURN
    CALCULATE ( [Qtde Produtos], REMOVEFILTERS ( dInventario ), dInventario[Ano Inventário] = _a - 1 )
```

### Var Qtde Produtos

Diferença de produtos sobre o inventário anterior.

```dax
[Qtde Produtos Atual] - [Qtde Produtos Anterior]
```

### % Variação PF

Variação percentual do tamanho funcional.

```dax
DIVIDE ( [PF Atual] - [PF Anterior], [PF Anterior] )
```

### Variação PF (seta)

Diferença de pontos de função, com seta.

```dax
[Variação PF]
```

### % Var Desenvolvidos



```dax
CALCULATE ( [% Variação Valor], dProduto[Categoria] = "Desenvolvido internamente" )
```

### % Var Adquiridos



```dax
CALCULATE ( [% Variação Valor], dProduto[Categoria] <> "Desenvolvido internamente" )
```

### % Var Licenças



```dax
CALCULATE ( [% Variação Valor], dProduto[Categoria] = "Adquirido: licença" )
```

### % Var SEAP



```dax
CALCULATE ( [% Variação Valor], dProduto[Categoria] = "Adquirido: contrato (SEAP)" )
```

### Var % (tabela)

Variação do valor para tabelas.

```dax
[% Variação Valor]
```

### % Sistemas Sem Documentação



```dax
DIVIDE ( [Qtde Sem Documentação], CALCULATE ( COUNTROWS ( dProduto ), dProduto[Categoria] = "Desenvolvido internamente" ) )
```

### % Valor Sem Uso



```dax
DIVIDE ( [Valor Sem Uso ou Suspensos (R$)], [Valor Desenvolvidos (R$)] )
```

### Valor Em Desenvolvimento (R$)



```dax
CALCULATE ( [Valor Atual (R$)], dProduto[Situação Resumida] = "Em desenvolvimento" )
```

### % Licenças Encerradas



```dax
DIVIDE ( [Valor Licenças Encerradas (R$)], [Valor Licenças (R$)] )
```

### % SEAP Líquido



```dax
DIVIDE ( [Valor Líquido SEAP 31/12 (R$)], [Valor SEAP (R$)] )
```

### Total Diligências



```dax
COUNTROWS ( ALL ( dDiligencia ) )
```

### Prioritárias (contexto)



```dax
[Qtde Diligências Prioritárias]
```

### % Economia (contexto)



```dax
[% Economia]
```

### Mercado sobre Pago



```dax
DIVIDE ( [Custo a Preço de Mercado (R$)], [Custo Pago (R$)] )
```

### Sistemas com Custo (contexto)



```dax
[Qtde Sistemas com Custo]
```

### VI Anterior



```dax
VAR _a = [Ano Referência]
RETURN
    CALCULATE ( AVERAGE ( fAvaliacao[Valor Institucional] ), REMOVEFILTERS ( dInventario ), dInventario[Ano Inventário] = _a - 1 )
```

### Qtde Funções (contexto)



```dax
[Qtde Funções]
```

### Qtde Módulos (contexto)



```dax
COUNTROWS ( fModulo )
```

### Valor Atual (contexto)



```dax
[Valor Atual (R$)]
```

### Valor Desenvolvidos (contexto)

Valor dos softwares desenvolvidos internamente, para o card da capa.

```dax
[Valor Desenvolvidos (R$)]
```

### Posição

Posição pelo valor, com medalhas para os quatro maiores.

```dax
VAR r = [Posição no Ranking] RETURN IF ( NOT ISBLANK ( r ), SWITCH ( r, 1, "💎 1º", 2, "🥇 2º", 3, "🥈 3º", 4, "🥉 4º", r & "º" ) )
```

## 7. Cores

### Cor Faixa Valor

Nove faixas de valor no mesmo tom de azul.

```dax
VAR v = [Valor Atual (R$)] RETURN SWITCH ( TRUE (), v <= 100000, "#CFE3EA", v <= 300000, "#B4D3DE", v <= 600000, "#98C2D1", v <= 900000, "#7BAFC2", v <= 1200000, "#5F9BB2", v <= 2200000, "#4787A1", v <= 5200000, "#33748F", v <= 10000000, "#22617D", "#0E3A4D" )
```

### Cor Var Valor

Verde: aumento; vermelho: redução; cinza: estável.

```dax
VAR v = [% Variação Valor] RETURN SWITCH ( TRUE (), ISBLANK ( v ), "#5E7C88", v > 0.0005, "#1E8E5A", v < -0.0005, "#C0392B", "#5E7C88" )
```

### Cor Var Valor (escuro)

Verde: aumento; vermelho: redução; cinza: estável.

```dax
VAR v = [% Variação Valor] RETURN SWITCH ( TRUE (), ISBLANK ( v ), "#D9EAF0", v > 0.0005, "#8EE4B8", v < -0.0005, "#FFB3A7", "#D9EAF0" )
```

### Cor Var PF

Verde: aumento; vermelho: redução; cinza: estável.

```dax
VAR v = [% Variação PF] RETURN SWITCH ( TRUE (), ISBLANK ( v ), "#5E7C88", v > 0.0005, "#1E8E5A", v < -0.0005, "#C0392B", "#5E7C88" )
```

### Cor Var Qtde

Verde: aumento; vermelho: redução; cinza: estável.

```dax
VAR v = [Var Qtde Produtos] RETURN SWITCH ( TRUE (), ISBLANK ( v ), "#5E7C88", v > 0.0005, "#1E8E5A", v < -0.0005, "#C0392B", "#5E7C88" )
```

### Cor Var Desenvolvidos

Verde: aumento; vermelho: redução; cinza: estável.

```dax
VAR v = [% Var Desenvolvidos] RETURN SWITCH ( TRUE (), ISBLANK ( v ), "#5E7C88", v > 0.0005, "#1E8E5A", v < -0.0005, "#C0392B", "#5E7C88" )
```

### Cor Var Adquiridos

Verde: aumento; vermelho: redução; cinza: estável.

```dax
VAR v = [% Var Adquiridos] RETURN SWITCH ( TRUE (), ISBLANK ( v ), "#5E7C88", v > 0.0005, "#1E8E5A", v < -0.0005, "#C0392B", "#5E7C88" )
```

### Cor Var Licenças

Verde: aumento; vermelho: redução; cinza: estável.

```dax
VAR v = [% Var Licenças] RETURN SWITCH ( TRUE (), ISBLANK ( v ), "#5E7C88", v > 0.0005, "#1E8E5A", v < -0.0005, "#C0392B", "#5E7C88" )
```

### Cor Var SEAP

Verde: aumento; vermelho: redução; cinza: estável.

```dax
VAR v = [% Var SEAP] RETURN SWITCH ( TRUE (), ISBLANK ( v ), "#5E7C88", v > 0.0005, "#1E8E5A", v < -0.0005, "#C0392B", "#5E7C88" )
```

### Cor Variação PF Sistema

Verde: aumento; vermelho: redução; cinza: estável.

```dax
VAR v = SUM ( fPonte[Variação PF] ) RETURN SWITCH ( TRUE (), ISBLANK ( v ), "#5E7C88", v > 0.0005, "#1E8E5A", v < -0.0005, "#C0392B", "#5E7C88" )
```

## 9. Cenários

### Cenário A (ordem)

Cenário A escolhido (padrão: 2025 ao preço de 2026).

```dax
SELECTEDVALUE ( dCenarioA[Ordem], 2 )
```

### Cenário B (ordem)

Cenário B escolhido (padrão: Real 2026).

```dax
SELECTEDVALUE ( dCenarioB[Ordem], 7 )
```

### Valor Cenário A



```dax
VAR c = [Cenário A (ordem)] RETURN CALCULATE ( SUM ( fCenario[Valor (R$)] ), fCenario[Ordem] = c )
```

### PF Cenário A



```dax
VAR c = [Cenário A (ordem)] RETURN CALCULATE ( SUM ( fCenario[Tamanho Funcional (PF)] ), fCenario[Ordem] = c )
```

### Preço PF Cenário A



```dax
VAR c = [Cenário A (ordem)] RETURN CALCULATE ( MAX ( fCenario[Preço PF (R$)] ), fCenario[Ordem] = c )
```

### Sistemas Cenário A



```dax
VAR c = [Cenário A (ordem)] RETURN CALCULATE ( SUM ( fCenario[Sistemas] ), fCenario[Ordem] = c )
```

### Dif Real 2026 Cenário A



```dax
VAR c = [Cenário A (ordem)] RETURN CALCULATE ( SUM ( fCenario[Diferença para o Real 2026 (R$)] ), fCenario[Ordem] = c )
```

### Dif Real 2025 Cenário A



```dax
VAR c = [Cenário A (ordem)] RETURN CALCULATE ( SUM ( fCenario[Diferença para o Real 2025 (R$)] ), fCenario[Ordem] = c )
```

### Valor Cenário B



```dax
VAR c = [Cenário B (ordem)] RETURN CALCULATE ( SUM ( fCenario[Valor (R$)] ), fCenario[Ordem] = c )
```

### PF Cenário B



```dax
VAR c = [Cenário B (ordem)] RETURN CALCULATE ( SUM ( fCenario[Tamanho Funcional (PF)] ), fCenario[Ordem] = c )
```

### Preço PF Cenário B



```dax
VAR c = [Cenário B (ordem)] RETURN CALCULATE ( MAX ( fCenario[Preço PF (R$)] ), fCenario[Ordem] = c )
```

### Sistemas Cenário B



```dax
VAR c = [Cenário B (ordem)] RETURN CALCULATE ( SUM ( fCenario[Sistemas] ), fCenario[Ordem] = c )
```

### Dif Real 2026 Cenário B



```dax
VAR c = [Cenário B (ordem)] RETURN CALCULATE ( SUM ( fCenario[Diferença para o Real 2026 (R$)] ), fCenario[Ordem] = c )
```

### Dif Real 2025 Cenário B



```dax
VAR c = [Cenário B (ordem)] RETURN CALCULATE ( SUM ( fCenario[Diferença para o Real 2025 (R$)] ), fCenario[Ordem] = c )
```

### Valor por PF A

Valor médio por ponto de função.

```dax
DIVIDE ( [Valor Cenário A], [PF Cenário A] )
```

### Valor por PF B

Valor médio por ponto de função.

```dax
DIVIDE ( [Valor Cenário B], [PF Cenário B] )
```

### Valor por Sistema A

Valor médio por sistema.

```dax
DIVIDE ( [Valor Cenário A], [Sistemas Cenário A] )
```

### Valor por Sistema B

Valor médio por sistema.

```dax
DIVIDE ( [Valor Cenário B], [Sistemas Cenário B] )
```

### Nome Cenário A



```dax
VAR c = [Cenário A (ordem)] RETURN CALCULATE ( MAX ( fCenario[Cenário] ), fCenario[Ordem] = c )
```

### Nome Cenário B



```dax
VAR c = [Cenário B (ordem)] RETURN CALCULATE ( MAX ( fCenario[Cenário] ), fCenario[Ordem] = c )
```

### Pergunta Cenário A



```dax
VAR c = [Cenário A (ordem)] RETURN CALCULATE ( MAX ( fCenario[Pergunta] ), fCenario[Ordem] = c )
```

### Pergunta Cenário B



```dax
VAR c = [Cenário B (ordem)] RETURN CALCULATE ( MAX ( fCenario[Pergunta] ), fCenario[Ordem] = c )
```

### Premissas Cenário A



```dax
VAR c = [Cenário A (ordem)] RETURN CALCULATE ( MAX ( fCenario[Premissas] ), fCenario[Ordem] = c )
```

### Premissas Cenário B



```dax
VAR c = [Cenário B (ordem)] RETURN CALCULATE ( MAX ( fCenario[Premissas] ), fCenario[Ordem] = c )
```

### Diferença B - A (R$)



```dax
[Valor Cenário B] - [Valor Cenário A]
```

### % Diferença B sobre A



```dax
DIVIDE ( [Diferença B - A (R$)], [Valor Cenário A] )
```

### Placar Cenários



```dax
VAR d = [Diferença B - A (R$)] RETURN IF ( d >= 0, "B supera A em R$ ", "A supera B em R$ " ) & FORMAT ( ABS ( d ) / 1000000, "#,0.00" ) & " milhões (" & FORMAT ( ABS ( DIVIDE ( d, IF ( d >= 0, [Valor Cenário A], [Valor Cenário B] ) ) ), "0.0%" ) & ")"
```

## 7. Cores

### Cor Valor Cenário A

Laranja: lado com o maior valor.

```dax
IF ( [Valor Cenário A] > [Valor Cenário B], "#FF8C42", "#0E3A4D" )
```

### Cor Valor Cenário B

Laranja: lado com o maior valor.

```dax
IF ( [Valor Cenário B] > [Valor Cenário A], "#FF8C42", "#0E3A4D" )
```

### Cor PF Cenário A

Laranja: lado com o maior valor.

```dax
IF ( [PF Cenário A] > [PF Cenário B], "#FF8C42", "#0E3A4D" )
```

### Cor PF Cenário B

Laranja: lado com o maior valor.

```dax
IF ( [PF Cenário B] > [PF Cenário A], "#FF8C42", "#0E3A4D" )
```

### Cor Preço PF Cenário A

Laranja: lado com o maior valor.

```dax
IF ( [Preço PF Cenário A] > [Preço PF Cenário B], "#FF8C42", "#0E3A4D" )
```

### Cor Preço PF Cenário B

Laranja: lado com o maior valor.

```dax
IF ( [Preço PF Cenário B] > [Preço PF Cenário A], "#FF8C42", "#0E3A4D" )
```

### Cor Sistemas Cenário A

Laranja: lado com o maior valor.

```dax
IF ( [Sistemas Cenário A] > [Sistemas Cenário B], "#FF8C42", "#0E3A4D" )
```

### Cor Sistemas Cenário B

Laranja: lado com o maior valor.

```dax
IF ( [Sistemas Cenário B] > [Sistemas Cenário A], "#FF8C42", "#0E3A4D" )
```

### Cor Valor por PF A

Laranja: lado com o maior valor.

```dax
IF ( [Valor por PF A] > [Valor por PF B], "#FF8C42", "#0E3A4D" )
```

### Cor Valor por PF B

Laranja: lado com o maior valor.

```dax
IF ( [Valor por PF B] > [Valor por PF A], "#FF8C42", "#0E3A4D" )
```

### Cor Valor por Sistema A

Laranja: lado com o maior valor.

```dax
IF ( [Valor por Sistema A] > [Valor por Sistema B], "#FF8C42", "#0E3A4D" )
```

### Cor Valor por Sistema B

Laranja: lado com o maior valor.

```dax
IF ( [Valor por Sistema B] > [Valor por Sistema A], "#FF8C42", "#0E3A4D" )
```

## 9. Cenários

### Valor do Cenário (R$)

Valor de cada cenário.

```dax
SUM ( fCenario[Valor (R$)] )
```

### Efeito Fator (R$)

Ponte do valor dos desenvolvidos de 2025 para 2026.

```dax
SUM ( fPonteFator[Valor (R$)] )
```

### Aumento 2025-2026 (R$)



```dax
CALCULATE ( SUM ( fPonteFator[Valor (R$)] ), fPonteFator[Fator] <> "Inventário 2025" )
```

### Efeito Preço



```dax
CALCULATE ( SUM ( fPonteFator[Valor (R$)] ), fPonteFator[Fator] = "Preço do PF" )
```

### Efeito Tamanho



```dax
CALCULATE ( SUM ( fPonteFator[Valor (R$)] ), fPonteFator[Fator] = "Tamanho funcional" )
```

### Efeito VI



```dax
CALCULATE ( SUM ( fPonteFator[Valor (R$)] ), fPonteFator[Fator] = "Valor Institucional" )
```

### Efeito Novos



```dax
CALCULATE ( SUM ( fPonteFator[Valor (R$)] ), fPonteFator[Fator] = "Novos sistemas" )
```

### Efeito Base 2025



```dax
CALCULATE ( SUM ( fPonteFator[Valor (R$)] ), fPonteFator[Fator] = "Inventário 2025" )
```

### % Efeito Preço



```dax
DIVIDE ( [Efeito Preço], [Aumento 2025-2026 (R$)] )
```

### % Efeito Tamanho



```dax
DIVIDE ( [Efeito Tamanho], [Aumento 2025-2026 (R$)] )
```

### % Efeito VI



```dax
DIVIDE ( [Efeito VI], [Aumento 2025-2026 (R$)] )
```

### % Efeito Novos



```dax
DIVIDE ( [Efeito Novos], [Aumento 2025-2026 (R$)] )
```

### Variação PF Sistemas

Variação de PF de 2025 para 2026.

```dax
SUM ( fPonte[Variação PF] )
```

### Variação Valor Sistemas (R$)



```dax
SUM ( fPonte[Variação Total (R$)] )
```

### Mantidos que Aumentaram



```dax
CALCULATE ( COUNTROWS ( fPonte ), fPonte[Movimento do Tamanho] = "Aumentou" )
```

### Mantidos que Diminuíram



```dax
CALCULATE ( COUNTROWS ( fPonte ), fPonte[Movimento do Tamanho] = "Diminuiu" )
```

### Mantidos sem Alteração



```dax
CALCULATE ( COUNTROWS ( fPonte ), fPonte[Movimento do Tamanho] = "Sem alteração" )
```

### PF Mantidos 2025



```dax
CALCULATE ( SUM ( fPonte[PF 2025] ), fPonte[Situação no Período] = "Mantido" )
```

### Variação PF Mantidos



```dax
CALCULATE ( SUM ( fPonte[Variação PF] ), fPonte[Situação no Período] = "Mantido" )
```

### % Variação PF Mantidos



```dax
DIVIDE ( [Variação PF Mantidos], [PF Mantidos 2025] )
```

## 6. Narrativas

### Leitura Ponte

Leitura rápida da ponte 2025-2026.

```dax
"De R$ " & FORMAT ( [Efeito Base 2025] / 1000000, "#,0.00" ) & " mi (2025) para R$ " & FORMAT ( ( [Efeito Base 2025] + [Aumento 2025-2026 (R$)] ) / 1000000, "#,0.00" ) & " mi (2026): o novo preço do PF explica " & FORMAT ( DIVIDE ( [Efeito Preço], [Aumento 2025-2026 (R$)] ), "0.0%" ) & " do aumento, os sistemas novos " & FORMAT ( DIVIDE ( [Efeito Novos], [Aumento 2025-2026 (R$)] ), "0.0%" ) & ", a revisão do VI " & FORMAT ( DIVIDE ( [Efeito VI], [Aumento 2025-2026 (R$)] ), "0.0%" ) & " e o tamanho funcional " & FORMAT ( DIVIDE ( [Efeito Tamanho], [Aumento 2025-2026 (R$)] ), "0.0%" ) & ". Nos 31 sistemas mantidos, o tamanho variou " & FORMAT ( [Variação PF Mantidos], "+#,0.0;-#,0.0" ) & " PF: " & [Mantidos que Aumentaram] & " aumentaram, " & [Mantidos que Diminuíram] & " diminuíram e " & [Mantidos sem Alteração] & " não mudaram."
```

### Leitura Placar



```dax
"Compare dois cenários nos seletores acima. " & [Placar Cenários] & ". Cenário A: " & [Nome Cenário A] & "; cenário B: " & [Nome Cenário B] & "."
```
