# Inventário de Ativos Intangíveis - Exercício 2026

Inventário físico-financeiro dos bens intangíveis da Secretaria de Estado de Planejamento e Gestão de Mato Grosso (SEPLAG/MT).

| Item | Informação |
|---|---|
| Ato de designação | Portaria nº 124/2026/SEPLAG, de 22/07/2026 (DOE/MT nº 29.279, de 23/07/2026, p. 5) |
| Norma de regência | Instrução Normativa Conjunta nº 003/2022/SEPLAG/SEFAZ |
| Presidente | Jonathas Gomes Marques - matrícula 280193 |
| Membros designados | João Vitor de Vasconcelos - matrícula 350093; Thiago Nascimento de Vasconcelos - matrícula 348164; Vanessa Camila Souza Viana - matrícula 301112. Recusaram-se a exercer as atividades entre 12 e 17/11/2026 (Ata 001/2026, Atualização nº 2) |
| Prazo da Portaria | 30/10/2026 (art. 6º) - vencido |
| Data final de entrega | 27/11/2026, sem pedido de prorrogação |
| Progresso em 17/11/2026 | 45% (pesquisa de preços concluída em 16/11/2026) |
| Prazo do setorial de patrimônio ao setor contábil | 15/12/2026 (IN 03/2022, art. 26, § 1º) |
| Objeto de referência do preço do PF | Contrato nº 014/2022/SEPLAG - R$ 544,53 por PF (5º Termo de Apostilamento, SEPLAG-PRO-2026/09621) |

## Como executar

Veja o documento "Como Executar o Projeto" (`COMO_EXECUTAR.pdf`). Em resumo, na pasta `2026`:

1. `configurar_ambiente.bat` (Windows) ou `bash configurar_ambiente.sh` (Linux/Mac): cria o ambiente `.venv` e instala as bibliotecas.
2. `python executar.py --tudo`: refaz mapa, análise, evidências, manifestação e documentos, sem acessar a internet.

## Estrutura

| Pasta ou arquivo | Conteúdo |
|---|---|
| `0. Planejamento` | Plano de trabalho e cronograma, análise do inventário de 2025 e atas da comissão |
| `1.Legislação_Normas` | IN Conjunta 03/2022 e Portaria de designação da comissão |
| `2. Levantamento_Identificacao_Avaliacao` | Softwares adquiridos, softwares desenvolvidos internamente (APF) e pesquisa de preços do ponto de função |
| `3. Analise de Dados` | Assets, dados e painel Power BI |
| `4. Relatório Final` | Relatório final, laudos técnicos de avaliação (um por sistema, em `Laudos Técnicos de Avaliação`) e processo |
| `5. Governança_Recomendações` | Nota técnica consultiva; estudo de custos, contabilização e governança dos produtos de software, com minuta de IN Conjunta e referências oficiais |
| `_Modelo_Institucional` | Gerador de documentos no padrão visual da CPPTI/SEPLAG (HTML, PDF e Word), logo e fontes |
| `executar.py` | Executa as etapas do projeto na ordem certa |
| `requirements.txt` | Bibliotecas Python com as versões fixadas |
| `configurar_ambiente.*` | Instaladores do ambiente para Windows e Linux/Mac |
| `.vscode` | Configurações e tarefas prontas para o VS Code |

## Pesquisa de preços do ponto de função

Pasta `2. Levantamento_Identificacao_Avaliacao/2.3 Mapa Comparativo de Preços`. Leitura recomendada:

1. `6. Parecer Técnico/MANIFESTACAO_TECNICA_Preco_Ponto-Funcao_2026.pdf`: resultados, gráficos e limitações.
2. `4. Mapa Comparativo/Mapa_Comparativo_Precos_PF_2026.xlsx`: rastreabilidade de cada preço até a compra de origem.
3. `3. Evidências`: ficha de cada preço e documentos oficiais baixados do PNCP.
4. `5. Análise Estatística/Analise_Precos_PF-2026.ipynb`: notebook que reproduz a análise.
