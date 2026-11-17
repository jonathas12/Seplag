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
| Documentos | Gera atas, plano, análises e notas em HTML, PDF e Word no modelo institucional | ao lado de cada documento |

Os resultados devem sair idênticos aos publicados. Se algum número mudar, alguma entrada foi alterada.

## 4. Etapas por partes

| Comando | Para que serve |
|---|---|
| `python executar.py --analise` | Refazer só a análise depois de mexer no notebook |
| `python executar.py --manifestacao` | Refazer só a manifestação técnica |
| `python executar.py --documentos` | Refazer só os documentos (atas, plano, análises e notas) |
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

## 9. Editar atas, plano e notas no próprio VS Code

Cada documento tem um arquivo-fonte em texto simples (Markdown, extensão .md) e três arquivos gerados a partir dele: HTML, PDF e Word. **Edite sempre o arquivo-fonte**; o HTML, o PDF e o Word são refeitos a partir dele, no modelo institucional. Se você editar o Word ou o PDF, a alteração se perde na próxima geração.

| Documento | Arquivo-fonte (editar) | Arquivos gerados |
|---|---|---|
| Ata 001/2026 | `0. Planejamento/Atas/ATA 001-2026 - Abertura dos Trabalhos.md` | .html, .pdf e .docx na mesma pasta |
| Plano de Trabalho e Cronograma | `0. Planejamento/Plano_Trabalho_Cronograma_2026.md` | idem |
| Análise do Inventário de 2025 | `0. Planejamento/Analise_Inventario_2025_Apontamentos.md` | idem |
| Pesquisa de Preços | `2. Levantamento_Identificacao_Avaliacao/2.3 Mapa Comparativo de Preços/Pesquisa_Precos_PF_2026.md` | idem |
| Nota Técnica Consultiva | `5. Governança_Recomendações/Nota_Tecnica_Consultiva_Gestao_Governanca_Software.md` | idem |
| Nova ata ou novo documento | Copie um arquivo-fonte existente, renomeie e edite | gerados ao lado |

A Manifestação Técnica da pesquisa de preços é a exceção: ela é montada a partir dos resultados da análise, por `gera_manifestacao.py`, e não tem arquivo-fonte para editar.

### Como trabalhar

1. Abra o arquivo-fonte no VS Code e edite o texto.
2. Para ver como está ficando, use Ctrl+Shift+V (pré-visualização do Markdown).
3. Gere o PDF e o Word de uma das duas formas:
   - **Só o documento aberto:** Terminal > Executar Tarefa > "Documento aberto: gerar PDF e Word".
   - **Automático ao salvar:** Terminal > Executar Tarefa > "Documentos: gerar ao salvar (modo observação)". Enquanto a tarefa estiver aberta, cada Ctrl+S gera de novo o HTML, o PDF e o Word daquele documento, em poucos segundos.

### Regras de escrita que o modelo entende

| Escreva assim | Vira no documento |
|---|---|
| `# Título - Subtítulo` (primeira linha) | Faixa azul com título e subtítulo |
| `## 1. Seção` | Título de seção com barra verde |
| `### 1.1 Subseção` | Subtítulo azul |
| `**texto**` | Negrito |
| `> texto` | Caixa de destaque azul |
| `> **Atenção:** texto` | Caixa de destaque amarela |
| `- item` ou `1. item` | Lista |
| Tabela com barras verticais | Tabela com cabeçalho azul |
| `Cuiabá/MT, 17 de novembro de 2026.` (antes da primeira seção) | Data à direita, abaixo da faixa |

### Guardar as alterações no GitHub

O ideal é trabalhar em um clone do repositório, não na cópia extraída do .zip. Assim suas alterações e as feitas aqui se juntam pelo Git, sem perder nada:

1. No VS Code: Ctrl+Shift+P > "Git: Clone" > `https://github.com/jonathas12/Seplag` e escolha a pasta.
2. No canto inferior esquerdo, troque para a branch `jonathasgomes/hopeful-bohr-dhxkks`.
3. Abra a pasta `Inventário de Ativos Intangíveis/2026` e siga as seções 2 e 3 deste guia.
4. Depois de editar: painel Controle do Código-Fonte (Ctrl+Shift+G), escreva a mensagem (por exemplo, `docs(ata): registra reunião de 19/11`), clique em Confirmar e depois em Sincronizar.
