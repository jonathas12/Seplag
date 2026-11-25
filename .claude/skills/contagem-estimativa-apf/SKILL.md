---
name: contagem-estimativa-apf
description: Faz ou atualiza a contagem estimativa de pontos de função (NESMA; ALI 7, AIE 5, EE 4, CE 4, SE 5) de um software da SEPLAG/MT a partir de histórias de usuário ou documentação funcional em qualquer pasta, reconhecendo as mudanças de versão (texto destacado = novo ou alterado; riscado = removido), e gera a planilha de contagem no modelo institucional para o Laudo Técnico de Avaliação (IN Conjunta nº 003/2022/SEPLAG/SEFAZ). Use quando pedirem contagem estimativa, atualização de baseline por novas versões de histórias, contagem de melhoria ou revisão de uma contagem estimativa.
---

# Contagem estimativa de pontos de função (NESMA)

Segundo nível de detalhe, depois da indicativa (skill `contagem-indicativa-apf`). Identifica as funções de dados **e de
transação**, sem contar tipos de dados (TD) e arquivos referenciados (AR/TR), e aplica a complexidade padrão:

| Tipo | Complexidade | PF |
|---|---|---|
| ALI | baixa | 7 |
| AIE | baixa | 5 |
| EE | média | 4 |
| CE | média | 4 |
| SE | média | 5 |

A planilha institucional aplica esses pesos sozinha quando as colunas D (TD) e E (AR/TR) ficam vazias.

Pasta de trabalho: `Inventário de Ativos Intangíveis/2026`; Python `.venv/bin/python`.

## Passo 1: partir da indicativa

Antes das transações, faça a parte indicativa (skill `contagem-indicativa-apf`): liste os ALI (dados mantidos pela
aplicação) e os AIE (dados de outra aplicação apenas lidos), com a mesma regra de agrupamento e exclusão (dados de código,
tabelas técnicas, logs sem consulta, subgrupos 1:1). Essa lista é o esqueleto da estimativa.

## Passo 2: extrair a documentação (qualquer pasta)

```
python _Modelo_Institucional/extrai_historias_marcadas.py <pasta> <saida.txt> --resumo <resumo.json>
```

- Lê `.docx` (inclusive com extensão quebrada, como `relatório.2.0docx`), `.pdf` e `.txt`/`.md` (LEIA-ME).
- Marca `{+ ... +}` o texto destacado (realce amarelo ou sombreamento): inclusão ou alteração da versão.
- Marca `{- ... -}` o texto riscado (tachado ou revisão excluída): remoção.
- Tabelas (campos, ações, regras, histórico de versões) saem como `| c1 | c2 |`.
- O resumo traz o código da história, a versão do nome, a última linha do histórico e quantos trechos novos/removidos há.
- Arquivos do Drive: baixar com `download_file_content`, copiar para uma pasta do scratchpad com o nome original e rodar o extrator nessa pasta. Leia primeiro o LEIA-ME da analista, se houver.

## Passo 3: identificar as transações em cada história

Cada **processo elementar** que o usuário reconhece é uma função; cada um conta uma vez na aplicação.

- **EE (entrada externa):** processa dados vindos de fora da fronteira e mantém ALI ou altera comportamento.
  - Exemplos: incluir, alterar, excluir, salvar, ativar/inativar, aprovar/reprovar, assinar, importar, enviar.
  - Botões que só abrem tela ou limpam campo não contam.
- **CE (consulta externa):** recupera e apresenta dados sem cálculo, sem dado derivado e sem alterar ALI.
  - Exemplos: listar, pesquisar, visualizar, consulta implícita (dados carregados para edição), combo-box com dados de ALI/AIE.
- **SE (saída externa):** apresenta dados com cálculo, totalização, dado derivado ou formatação de relatório; pode atualizar ALI.
  - Exemplos: painéis com indicadores, relatórios em PDF/Excel com totais, grids com tempo calculado, certidões geradas.
- **Mesma lógica, telas diferentes:** listas ou consultas idênticas em vários pontos contam uma vez. Lógica, filtros ou dados diferentes contam separadamente.
- **Não contam:**
  - navegação, menus, ajuda e mensagens;
  - textos de declaração;
  - layout e cabeçalho (cosmética);
  - requisitos não funcionais (desempenho, segurança, responsividade).
- **Exportação:** exportar a mesma listagem em PDF e Excel com o mesmo conteúdo é uma função; exportações de listagens diferentes são funções distintas.

## Passo 4: atualização de versão (histórias com marcações)

- **Função nova:** `{+ +}` que cria um processo elementar ou grupo de dados que não existia. Entra no tamanho da aplicação.
  - Exemplos: nova tela ou aba, novo relatório ou exportação, novo cadastro.
- **Alteração:** `{+ +}` que muda campos, regras, filtros, colunas ou validações de função existente. Não muda o tamanho da aplicação (contagem de aplicação); registre na coluna O da função ("Alterada em AAAA (USnn vX): ...").
  - Numa contagem de **projeto de melhoria**, a alteração entra com o tipo de manutenção A e é deflacionada no PF Local da FS.
- **Remoção:** `{- -}` de uma função inteira a retira da aplicação. Apague a linha com `remove_duplicadas.py` e uma nota.
  - Riscado de rótulo ou campo é só alteração.
- **História nova inteira:** sem marcações, mas indicada como nova no LEIA-ME ou no histórico. Conta todas as suas funções.
- **Conferência:**
  - Compare com a baseline anterior por história (grupo da aba Funções) antes de acrescentar, para não duplicar.
  - Se a baseline tiver erros, corrija em cópia e registre: tipo de contagem, projeto copiado de outro sistema, tecnologia vazia, tipo de função trocado.

## Passo 5: gravar a planilha

```
python _Modelo_Institucional/gera_contagem_estimativa.py origem.xlsx destino.xlsx contagem.json
```

Modos do `contagem.json`:
- **Contagem nova:** chave `grupos`, com `limpar_linhas` opcional. Use uma planilha institucional como modelo, por exemplo a v1.1 do Revisa.
- **Incremento:** chave `acrescentar`, com grupos novos gravados depois da última linha usada.
- **Ajustes em linhas existentes:** `anotar` (coluna O) e `renomear` (coluna A).
- **Aba Contagem:** chave `contagem` (F6 tipo, F7 "Estimativa (NESMA)", R7 tecnologia, F10 revisor, R10 data, A17 escopo, A22 documentação).

O script recalcula no LibreOffice e confere `Funções!L4` com o total esperado (existente + novas, pelos pesos NESMA).
Não use o recálculo em planilha com referência a outra pasta de trabalho (ex.: `[1]Deflatores`): nesse caso, ajuste os
valores em cache como no SIGS. Grave sempre em `2026/.../2.1. Medições em APF/<nº. SIGLA>/` com nova versão; nunca altere
o arquivo de 2025.

Testes (25/11/2026):
- **Incremento:** a baseline do Banco de Talentos (281 PF) recebeu a US012 (+36 PF) e as anotações de alteração, total 317 PF.
- **Contagem nova com outro modelo:** Progressão Vertical (210 PF) e Contagem de Tempo (258 PF), gravados sobre a v1.2 do Revisa.
  Esse teste revelou que o LibreOffice mantinha os valores em cache do modelo (as linhas novas herdavam os pesos das
  funções antigas e L4 continuava 319). O script passou a usar um perfil temporário do LibreOffice com recálculo
  obrigatório ao abrir (OOXMLRecalcMode = 0). Recriar o Revisa sobre ele mesmo não serve de teste, pois os valores em
  cache coincidem.
- **Conferência obrigatória:** além de L4, confira linha a linha que a coluna H de cada função tem o peso NESMA do tipo.

## Passo 6: laudo

Gerar o laudo pela skill `laudo-avaliacao-intangivel`, com `nivel_contagem` "Estimativa (NESMA)". Na primeira avaliação de
um sistema (uma só medição), use `laudo_apf_primeira_dev.py`, que também aceita `rotulo_uso`, `rotulo_fase` e
`conclusao_reconhecimento` para bens em desenvolvimento e arredonda os centavos como o Excel. O texto do nível explica
a complexidade padrão. A evolução e as ressalvas registram o que foi incluído, alterado, removido ou corrigido na versão.
Recomende contagem detalhada quando as histórias trouxerem campos (TD) e entidades (AR/TR) suficientes.
