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

Variação percentual do valor.

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
IF ( HASONEVALUE ( dProduto[ID Produto] ), RANKX ( ALLSELECTED ( dProduto[ID Produto] ), [Valor Atual (R$)], , DESC, DENSE ) )
```

## 2. Governança

### Qtde Sem Documentação

Desenvolvidos sem documentação funcional disponibilizada (2ª Nota Técnica).

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
    & " em desenvolvimento dependem das diligências da 2ª Nota Técnica."
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
