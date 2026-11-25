---
name: manifestacao-reconhecimento-intangivel
description: Elabora Manifestação Técnica (PDF e Word, modelo institucional SEPLAG/MT) que responde se uma contratação, licença, assinatura, software ou serviço de TI é ou não ativo intangível pela IN Conjunta nº 003/2022/SEPLAG/SEFAZ, com análise de reconhecimento, benefício ou potencial de serviço, controle e propriedade, mensuração, vida útil, amortização e recomendação ao setor contábil. Use quando pedirem parecer, manifestação, consultoria ou análise sobre "isso é intangível?", licença de software por prazo determinado, SaaS, renovação, cessão de uso, termo de referência ou contrato a classificar como ativo ou despesa.
---

# Manifestação Técnica de reconhecimento de bem intangível

Consultas que o avaliador (Jonathas Gomes Marques) recebe de áreas da SEPLAG ou de outros órgãos: uma contratação
deve ou não ir para o Ativo Intangível? O resultado é uma Manifestação Técnica opinativa, com assinatura do avaliador.
Pasta de trabalho: `Inventário de Ativos Intangíveis/2026`; Python `.venv/bin/python`.

## Passos

1. **Ler o documento da consulta inteiro** (termo de referência, ETP, contrato, proposta, nota fiscal): `pdftotext -layout`.
   Anotar objeto, contratada, titular dos direitos autorais e do código-fonte, vigência, prorrogação, valor e forma de
   pagamento, natureza da despesa (3.3.90.xx corrente ou 4.4.90.xx capital), se é primeira aquisição ou renovação,
   suporte e atualizações, restrições (alterar, ceder, comercializar).
2. **Ler a IN** (`5. Governança_Recomendações/Estudo_Custos_Produtos_Software/Referencias/MT_IN_Conjunta_03-2022-SEPLAG-SEFAZ.pdf`)
   e citar só artigos conferidos no texto. Dispositivos usuais:
   - **Definição e alcance:**
     - art. 2º, II: bem intangível, controlado e gerador de benefício ou potencial de serviço;
     - art. 2º, XI: software de prateleira;
     - art. 2º, § 1º: código do Estado, prateleira e projetos em desenvolvimento;
     - art. 2º, § 2º, I: sem licença válida não registra.
   - **Renovação:** art. 2º, IV, renovação de licença é custo de manutenção periódica; art. 10, parágrafo único, esse custo não entra no valor.
   - **Critérios:** art. 6º, parágrafo único, I a IV; III e IV são alternativos.
   - **Gerado internamente:** arts. 8º e 9º.
   - **Mensuração:**
     - art. 10, I: custo de aquisição;
     - art. 10, II: valor justo, se sem contraprestação;
     - art. 10, III: custos incorridos;
     - art. 11: pontos de função, só quando não há custo conhecido.
   - **Agrupamento:** art. 12, valor do conjunto.
   - **Vida útil:**
     - arts. 14 e 15: definida ou indefinida;
     - art. 16, caput e § 1º: vida útil limitada pelo direito, renovação só sem custo significativo;
     - art. 16, § 2º: software não passa da vigência da licença.
   - **Amortização:** arts. 17 a 19; início na disponibilização para uso (art. 19, § 1º); residual zero (art. 19, § 2º).
   - **Contabilização:** art. 20, II (IS 022/2020-SACE/SEFAZ, item 4.7), arts. 23, 24 e 27.
3. **Analisar cada critério** (tabela Ponto, Dispositivo, Aplicação ao caso, Resultado: Atende, Não atende, Condiciona,
   Não impede). Pontos de entendimento firmados:
   - **Controle e propriedade:** o controle exigido é dos benefícios, não da propriedade do código. Licença de uso de
     software de prateleira pode ser reconhecida, com o direito de uso como objeto.
   - **Licença por prazo determinado:** vida útil definida igual à vigência. Amortização linear mensal e baixa no vencimento.
   - **Separabilidade:** licença intransferível não atende o III, mas o IV (direito contratual) basta.
   - **Fatores que afastam ou condicionam o registro:**
     - despesa corrente (3.3.90.40);
     - renovação de licença já usada;
     - cessão temporária, equivalente a assinatura ou SaaS;
     - valor pequeno consumido em até 12 meses, quando o custo do controle supera o benefício informacional.
   - **Natureza da despesa:** a correlação com o registro patrimonial não está na IN; dizer que deve ser confirmada com
     o setor contábil (art. 27), sem citar texto do MCASP que não foi lido.
4. **Recomendação clara**, com alternativa: se o setor contábil optar pelo registro, dar os parâmetros:
   - custo;
   - agrupamento;
   - vida útil;
   - início e valor da amortização, com centavos da última parcela;
   - baixa;
   - identificação contábil.
5. **Inconsistências do documento** (campos "XX", trechos copiados de outro objeto, classificação incoerente com o
   objeto, contrato dispensado com vigência futura): listar com o item do documento.
6. **Escrever o JSON** em `5. Governança_Recomendações/Manifestacoes_Tecnicas/<AAAA-MM objeto>/manifestacao.json`.
   - Os campos estão no cabeçalho de `_Modelo_Institucional/manifestacao_tecnica.py`.
   - Exemplo completo: `2026-11 Metrica Topo/manifestacao.json`.
7. **Gerar:** `python _Modelo_Institucional/manifestacao_tecnica.py "<pasta>/manifestacao.json"`. O script recusa
   travessão longo.
8. **Conferir o PDF visualmente.** Commitar o JSON e os documentos gerados, sem o documento recebido, que pode ter
   dados pessoais ou bancários. Enviar o PDF e o DOCX ao usuário.

## Estilo e assinatura

- **Tom técnico e formal.** Cada afirmação cita o item do documento analisado ou o artigo da IN. Sem elogios e sem adjetivos de valor.
- **Caráter opinativo:** a decisão sobre o registro é do setor contábil (Portaria nº 124/2026/SEPLAG, art. 3º).
- **Assinatura (campo `responsavel`):** Jonathas Gomes Marques, "Avaliador de Ativos Intangíveis de Software", Presidente da CIABI, "Gerente de projetos e cientista de dados (CPPTI/SSCPG/SAPGD/SEPLAG)", Portaria nº 124/2026/SEPLAG, matrícula 280193.
- **Campo `qualificacao`:** atuação em gestão de produtos e tecnologia, métricas de software (pontos de função), gestão de projetos, avaliação de ativos intangíveis e ciência de dados.
- **Não inventar:**
  - número de manifestação ou de processo: usar `numero` só se o usuário informar;
  - nomes de servidores do documento recebido: não reproduzir sem necessidade.
