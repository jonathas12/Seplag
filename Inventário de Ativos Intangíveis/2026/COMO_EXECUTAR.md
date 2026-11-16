# Como Executar o Projeto - Inventário de Ativos Intangíveis 2026

Guia para rodar, entender e reproduzir os resultados da pesquisa de preços no VS Code, em qualquer computador.

## 1. O que é preciso

| Item | Onde obter | Observação |
|---|---|---|
| Python 3.11 ou superior | python.org/downloads | Na instalação do Windows, marcar "Add python.exe to PATH" |
| VS Code | code.visualstudio.com | O VS Code sugere as extensões Python e Jupyter ao abrir a pasta |
| Internet | - | Só na primeira configuração (bibliotecas e navegador) e nas etapas que consultam os portais |

## 2. Primeira vez: configurar o ambiente

1. Abra no VS Code a pasta `2026` (menu Arquivo > Abrir Pasta). Abra a pasta `2026`, não a pasta do repositório inteiro, para que as configurações do VS Code funcionem.
2. Clique duas vezes em `configurar_ambiente.bat`, ou, no terminal do VS Code, rode o comando abaixo.
3. Aguarde a mensagem "Ambiente pronto". O script cria a pasta `.venv` (ambiente virtual), instala as bibliotecas com as versões fixadas em `requirements.txt`, instala o navegador usado para gerar PDFs e prints e registra o kernel do Jupyter.
4. Feche e reabra o terminal do VS Code. O ambiente passa a ser ativado sozinho.

```powershell
powershell -ExecutionPolicy Bypass -File .\configurar_ambiente.ps1
```

> **Atenção:** se a rede da SEPLAG exigir proxy, defina antes no terminal: `$env:HTTPS_PROXY = "http://usuario:senha@proxy:porta"`. No Linux ou Mac, use `bash configurar_ambiente.sh`.

## 3. Refazer todos os resultados

No terminal do VS Code, na pasta `2026`:

```powershell
python executar.py --tudo
```

Ou pelo menu Terminal > Executar Tarefa > "2. Refazer tudo (sem internet)". O atalho Ctrl+Shift+B também roda essa tarefa.

O comando refaz, nesta ordem, a partir dos dados gravados na data da pesquisa e sem acessar a internet:

| Etapa | O que faz | Onde fica o resultado |
|---|---|---|
| Mapa | Monta a base de preços a partir dos dados brutos das APIs e aplica o IPCA | `4. Mapa Comparativo/Precos_Ponto_Funcao_2025-2026.csv` |
| Análise | Executa o notebook: estatística, K-Means, sensibilidade, comparação com 2025 e gráficos | `5. Análise Estatística` |
| Fichas | Gera a planilha de rastreabilidade e a ficha de evidência de cada preço | `4. Mapa Comparativo` e `3. Evidências` |
| Manifestação | Gera a manifestação técnica em HTML, PDF e Word | `6. Parecer Técnico` |
| Documentos | Converte os documentos .md para HTML, PDF e Word no modelo institucional | ao lado de cada .md |

Os resultados devem sair idênticos aos publicados. Se algum número mudar, alguma entrada foi alterada.

## 4. Etapas por partes

| Comando | Para que serve |
|---|---|
| `python executar.py --analise` | Refazer só a análise depois de mexer no notebook |
| `python executar.py --manifestacao` | Refazer só a manifestação técnica |
| `python executar.py --documentos` | Refazer só os documentos .md |
| `python executar.py --pncp` | Baixar de novo do PNCP os documentos oficiais de cada preço (internet) |
| `python executar.py --prints` | Tirar prints das telas do PNCP e do Compras.gov.br (internet, navegador visível) |
| `python executar.py --atualizar-dados --tudo` | Fazer uma nova pesquisa nas APIs oficiais (internet). Os números podem mudar |

## 5. Prints das telas e documentos oficiais

Os documentos oficiais (edital, termo de referência, contratos) e o resultado homologado de cada preço vêm da API pública do PNCP, que não exige login nem verificação. O comando `--pncp` baixa tudo para `3. Evidências/Documentos PNCP` e gera imagens das páginas em que o preço aparece, com o valor destacado.

As telas dos portais exibem uma verificação hCaptcha. Por isso o comando `--prints` abre o navegador visível: se a verificação aparecer, resolva-a na tela e o script continua. Os prints ficam em `3. Evidências/Documentos PNCP/<referência>/telas`.

## 6. Trabalhar no notebook

Abra `5. Análise Estatística/Analise_Precos_PF-2026.ipynb`, escolha o kernel "Inventario 2026 (.venv)" no canto superior direito e use "Run All". Cada célula tem um comentário dizendo o que faz. Os gráficos são gravados em `5. Análise Estatística/graficos`.

## 7. Onde mudar parâmetros

O arquivo `2. Levantamento_Identificacao_Avaliacao/2.3 Mapa Comparativo de Preços/config_pesquisa.json` reúne os parâmetros: data da pesquisa, período das compras, contrato de referência (preço vigente e mês-base do apostilamento), janela de reaproveitamento e parâmetros do K-Means. Depois de alterar, rode `python executar.py --tudo`.

## 8. Problemas comuns

| Mensagem | Solução |
|---|---|
| "Python 3.11+ não encontrado" | Instale o Python e marque "Add python.exe to PATH" |
| "running scripts is disabled on this system" | Use o `configurar_ambiente.bat`, que já libera a execução só para o script |
| Erro de conexão no pip ou no Playwright | Configure o proxy (seção 2) ou rode em uma rede sem bloqueio |
| O VS Code não acha o ambiente | Ctrl+Shift+P > "Python: Select Interpreter" > escolha `.venv` |
| Caracteres estranhos no terminal | O projeto já força UTF-8; feche e reabra o terminal do VS Code |
