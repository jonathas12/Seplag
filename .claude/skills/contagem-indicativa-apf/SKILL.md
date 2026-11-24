---
name: contagem-indicativa-apf
description: Faz a contagem indicativa de pontos de função (NESMA, 35 PF por ALI e 15 PF por AIE) de um software da SEPLAG/MT sem medição anterior, a partir da documentação disponível (documentação técnica, manual, normas, histórias, telas), e gera a planilha de contagem no modelo institucional para o Laudo Técnico de Avaliação (IN Conjunta nº 003/2022/SEPLAG/SEFAZ). Use quando o usuário pedir contagem indicativa, medição inicial em PF ou a medição de um sistema que ainda não tem planilha de APF.
---

# Contagem indicativa de pontos de função (NESMA)

Usada quando o sistema não tem planilha de APF e a documentação não permite contagem estimativa ou detalhada
(nada de histórias com campos e transações). O resultado alimenta a skill `laudo-avaliacao-intangivel`.
Pasta de trabalho: `Inventário de Ativos Intangíveis/2026`; Python `.venv/bin/python`.

## Método

- **Contagem indicativa NESMA (ISO/IEC 24570):** identifica só as funções de dados. Cada Arquivo Lógico Interno (ALI)
  vale 35 PF e cada Arquivo de Interface Externa (AIE) vale 15 PF; o peso das transações (EE, CE, SE) está embutido.
  Tamanho = 35 x ALI + 15 x AIE. No laudo, o tamanho indicativo vem de `'Sumário 1'!G47` da planilha.
- **ALI:** grupo de dados logicamente relacionado, reconhecido pelo usuário, **mantido** por processo elementar da
  aplicação (incluir, alterar, excluir). Ex.: bens, reservas, usuários, órgãos, setores, categorias mantidas por tela.
- **AIE:** grupo de dados reconhecido pelo usuário, **só lido** pela aplicação e mantido por outra (SEAP, Manopla, Thanos,
  CIP, FIPLAN). Integração que só envia dados para fora não gera AIE.
- **Não contar:** dados de código (tabelas fixas de tipos, situações, perfis com poucos atributos e sem tela de
  manutenção), tabelas técnicas do framework (sessões, cache, jobs, migrations), logs e auditoria sem consulta pelo
  usuário, arquivos físicos (imagens) que são atributos do grupo de dados.
- **Agrupar subgrupos (RET) no mesmo ALI:** tabelas 1:1 ou dependentes que não existem sozinhas para o usuário (ex.:
  certidão gerada na finalização da reserva = subgrupo da reserva; vínculo usuário-perfil = subgrupo do usuário).
  Na dúvida, prefira o agrupamento (contagem conservadora) e registre a decisão na coluna O e nas ressalvas.
- **Fontes por ordem de força:** modelo de dados/ER e lista de models; rotas e telas (CRUD indica manutenção);
  regras de negócio; manual do usuário; normas (dizem o que o sistema deve guardar). Cite a fonte de cada função.

## Passos

1. Ler toda a documentação (PDF com `pdftotext -layout`; docx pelo XML) e as normas. Anotar entidades, quem mantém cada
   uma (tela/rota de cadastro), integrações e dados lidos de outros sistemas.
2. Montar a lista de ALI e AIE por módulo, com observação de origem (ex.: "pat_produto; rotas /produto; doc. técnica §5").
   Descartar e registrar o que não conta (dados de código, técnicos, subgrupos).
3. Escrever `contagem.json` (grupos, campos da aba Contagem: F5 aplicação, F6 "Aplicação", F7 "Indicativa (NESMA)",
   R7 tecnologia, F9/F10 responsável/revisor, R9/R10 datas, A17 escopo, A22 documentação) e gerar a planilha:
   `python _Modelo_Institucional/gera_contagem_indicativa.py modelo.xlsx destino.xlsx contagem.json`
   Modelo: `2. Levantamento_Identificacao_Avaliacao/.../11. Recadastramento/APF-Recadastramento-v1.0.xlsx` (G47 =
   (ALI)*35 + (AIE)*15 pela coluna G da aba Funções). O script limpa as funções do modelo, grava as novas, recalcula no
   LibreOffice e confere G47. Destino: pasta do sistema em `2.1. Medições em APF/<nº. SIGLA>/APF-<SIGLA>-v1.0.xlsx`.
4. Gerar o laudo com `laudo_apf_indicativa.py` (`medida` e `nivel_contagem` = "Indicativa (NESMA)", `modulo_por_tipo`
   opcional), seguindo a skill `laudo-avaliacao-intangivel`.
5. No laudo, explicar o nível (só funções de dados, transações embutidas), listar o que não foi contado e recomendar
   contagem estimativa ou detalhada quando houver documentação funcional.

## Práticas aprendidas no inventário de 2026

- **Planilhas recebidas:** sempre conferir antes de usar.
  - Linhas de modelo esquecidas ("Ali", "Criar", "Exter"... no Revisa).
  - Contagem de melhoria usada como baseline (A50/COS somados pelo valor integral).
  - Aba renomeada ("SPRINT1" no Manopla, que quebra a aba Contagem com #REF!).
  - Rótulo F7 incoerente com as complexidades.
  - Funções duplicadas entre histórias (Portal, SIGS).
  - Funções de exclusão (E) de funcionalidade retirada.
  - Referências externas que o LibreOffice não resolve (SIGS).
- **Correções:**
  - Nunca alterar o arquivo de 2025: gravar cópia em 2026 com nova versão ou com a Contagem revisada.
  - Registrar cada correção na coluna O e nas ressalvas.
  - Decisões de tamanho (o que entra, duplicadas, entregue x especificado) são do presidente da comissão: perguntar com os números.
- **Sistemas da fábrica (Contrato 014/2022):**
  - Medir só o que foi entregue (e-mail de entrega/produção, TRD).
  - Citar Grupo I 25% e Grupo II 75% da OS e o custo do painel.
  - Sem uso ou sem continuidade: ressalva com os arts. 2º § 1º, 9º I/II/V, 18 e 23 da IN, recomendando decisão formal de continuidade ou baixa.
- **Textos:** citar só o que foi lido. Norma informada e não anexada vira "referência informada, não lida". Arquivo acima de 10MB no Drive não baixa pelo conector: registrar e pedir PDF menor.
