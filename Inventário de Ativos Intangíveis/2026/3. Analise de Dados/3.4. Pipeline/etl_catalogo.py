"""
ETL do Catálogo de Produtos de Software (Inventário de Bens Intangíveis 2026, CIABI/SEPLAG-MT).

Lê as fontes oficiais do inventário e gera o modelo em estrela (star schema) em .parquet:

  Dimensões: dProduto, dInventario, dPrecoPF, dDiligencia, dTipoFuncao
  Fatos:     fAvaliacao (produto x inventário), fModulo, fFuncao, fIntegracao, fHistoricoLaudo,
             fCustoProjeto, fEconomicidade, fAmortizacaoSEAP
  Ponte:     bProdutoDiligencia

Fontes (ver config.toml): aba "Avaliação 2026" da relação de sistemas, Dados.xlsx (inventários de 2023
a 2025), levantamento dos adquiridos, laudos técnicos (JSON) e a curadoria da 3ª Nota Técnica Consultiva.
Ao final confere os totais com os valores publicados nos laudos e relatórios e grava auditoria_etl.csv.
"""
import csv
import json
import sys
import tomllib
from datetime import datetime, date
from pathlib import Path

import openpyxl
import pandas as pd

AQUI = Path(__file__).resolve().parent
CFG = tomllib.loads((AQUI / "config.toml").read_text(encoding="utf-8"))
P = lambda rel: (AQUI / rel).resolve()
F = {k: P(v) for k, v in CFG["fontes"].items() if v}
SAIDA = P(CFG["saida"]["parquet"])
PRECO_2026 = CFG["parametros"]["preco_pf_mercado_2026"]

# ------------------------------------------------------------------ identificação canônica dos produtos
# ID Produto: (chave na aba Avaliação 2026, siglas no Dados.xlsx, pasta do laudo)
# WEB PONTO aparece duas vezes nas planilhas e é distinguido pelo nome.
PRODUTOS = {
    "SISPAT": ("SISPAT", ["SISPAT"], "3. SISPAT"),
    "SIAG": ("SIAG", ["SIAG"], "26. SIAG"),
    "SIG-SST": ("SIG-SST", ["SIG-SST"], "1. SST/SIG-SST"),
    "SIGPAS": ("SIGPAS", ["SIGPAS"], "5. SIGPAS"),
    "SICAD": ("SICAD", ["SICAD"], "12. SICAD"),
    "SIGED": ("SIGED", ["SIGED"], "6. SIGED"),
    "CENSO": ("Censo", ["Censo"], "25. Censo"),
    "SIGEV": ("SIGEV", ["SIGEV"], "19. SIGEV"),
    "PSICO": ("PSICO", ["PSICO"], "1. SST/PSICO"),
    "RAG": ("RAG", ["RAG"], "22. RAG-Monitora"),
    "SIES-MT": ("SIES-MT", ["SIES", "SIES-MT"], "27. SIES-MT"),
    "SINOVA": ("SINOVA", ["SINOVA"], "28. SINOVA"),
    "SIFSW": ("SIFSW", ["SIFSW"], "20. SIFSW"),
    "RECAD": ("RECAD", ["RECAD"], "11. Recadastramento"),
    "SIEP": ("SIEP", ["SIEP"], "4. SIEP"),
    "PORTAL": ("PORTAL", ["PORTAL"], "9. Portal do Servidor"),
    "SIGS": ("SIGS", ["SIGS"], "7. SIGS"),
    "SINER": ("SINER", ["SINER"], "17. SINER"),
    "MANOPLA": ("Manopla", ["Thanos", "Manopla"], "13. Manopla"),
    "WEBPONTO": ("WEB PONTO|Web Ponto", ["WEB PONTO|Web Ponto"], "10. Web Ponto"),
    "SEI": ("SEI", ["SEI"], "2. SEI"),
    "REVISA": ("Revisa", ["Revisa"], "23. Revisa Consignados"),
    "OPINIOES": ("Opiniões", ["Opiniões"], "24. Opinioes"),
    "SIADES": ("SIADES", ["SIADES"], "26. SIADES"),
    "BANCO-TALENTOS": ("Banco de Talentos", ["Banco de Talentos"], "21. Banco de Talentos"),
    "SCPA": ("SCPA", ["SCPA"], "16. SCPA"),
    "SICC": ("SICC", ["SICC"], "14. SICC"),
    "DBV": ("DBV", ["DBV"], "8. DBV"),
    "WEBPONTO-CLIENT": ("WEB PONTO|Web Ponto Client Biometria", ["WEB PONTO|Web Ponto Client Biometria"], "10. Web Ponto Client Biometria"),
    "SGA-PERICIA": ("SGA-Perícia Médica", ["SGA-Perícia Médica"], "18. Perícia Médica"),
    "AG-SGA": ("Ag. SGA", ["Ag. SGA"], "15. Agendamento SGA"),
    "PV": ("PV", [], "30. Progressão Vertical"),
    "CONTAGEM": ("Contagem", [], "31. Contagem de Tempo"),
    "SIDE": ("SIDE", [], "32. SIDE"),
    "SAGEP": ("SAGEP", [], "33. SAGEP"),
    "SIGEP": ("SIGEP", [], "34. SIGEP"),
    "SIGQA": ("SIGQA", [], "35. SIGQA"),
    "PRIMO": ("Primo", [], "36. PRIMO"),
    "SIDBENS": ("SIDBENS", [], "29. SIDBENS"),
}
FAIXA_VI = {1.0: "Imprescindível", 0.75: "Muito importante", 0.5: "Importante", 0.25: "Relativa importância"}
CAT_DEV, CAT_LIC, CAT_SEAP = "Desenvolvido internamente", "Adquirido: licença", "Adquirido: contrato (SEAP)"
AUD = []


def aud(item, obtido, esperado, tol=0.01):
    ok = abs(float(obtido) - float(esperado)) <= tol
    AUD.append({"Conferência": item, "Obtido": round(float(obtido), 2), "Esperado": round(float(esperado), 2), "OK": "Sim" if ok else "NÃO"})
    return ok


def chave_planilha(sig, nome):
    sig = str(sig).strip()
    return f"{sig}|{str(nome).strip()}" if sig.upper() == "WEB PONTO" else sig


def num(v):
    if v in (None, ""):
        return None
    if isinstance(v, str):
        v = v.replace("R$", "").replace(".", "").replace(",", ".").strip()
    return float(v)


def data(v):
    if isinstance(v, datetime):
        return v.date()
    if isinstance(v, date):
        return v
    if isinstance(v, str) and v.strip():
        for fmt in ("%d/%m/%Y", "%Y-%m-%d"):
            try:
                return datetime.strptime(v.strip(), fmt).date()
            except ValueError:
                pass
    return None


def resumo_situacao(s):
    s = (s or "").lower()
    if "sem uso" in s:
        return "Em produção, sem uso"
    if "legado" in s or "sucess" in s:
        return "Em produção (legado em sucessão)"
    if "suspens" in s:
        return "Em desenvolvimento (suspenso)"
    if "desenvolv" in s or "homolog" in s:
        return "Em desenvolvimento"
    if "produ" in s:
        return "Em produção"
    return s.capitalize() or "Não informado"


def texto(v, sep="\n\n"):
    if v is None:
        return ""
    if isinstance(v, list):
        return sep.join(texto(x, "; ") if isinstance(x, list) else str(x) for x in v)
    if isinstance(v, dict):
        return sep.join(f"{k}: {texto(x, ', ')}" for k, x in v.items())
    return str(v)


# ------------------------------------------------------------------ 1. aba Avaliação 2026
wb = openpyxl.load_workbook(F["sitec"], data_only=True)
ws = wb["Avaliação 2026"]
A26 = {}
for r in range(9, ws.max_row + 1):
    sig = ws.cell(r, 3).value
    if not sig:
        continue
    k = chave_planilha(sig, ws.cell(r, 5).value)
    A26[k] = dict(item=ws.cell(r, 2).value, sigla=str(sig).strip(), nome=str(ws.cell(r, 5).value).strip(), situacao=ws.cell(r, 6).value,
                  nivel=ws.cell(r, 8).value, tecnologia=ws.cell(r, 9).value, data=data(ws.cell(r, 10).value), pf=num(ws.cell(r, 11).value),
                  vida_util=ws.cell(r, 12).value, preco=num(ws.cell(r, 13).value), vt=num(ws.cell(r, 14).value), vi=num(ws.cell(r, 15).value),
                  va=num(ws.cell(r, 16).value))
TOT26 = (num(ws["K8"].value), num(ws["P8"].value))
assert len(A26) == 39, f"Avaliação 2026 deveria ter 39 sistemas: {len(A26)}"

# ------------------------------------------------------------------ 2. histórico (Dados.xlsx)
wd = openpyxl.load_workbook(F["historico"], data_only=True)["Plan1"]
HIST = []
for row in wd.iter_rows(min_row=2, values_only=True):
    if not row[0]:
        continue
    HIST.append(dict(ano=int(row[0]), sigla=str(row[1]).strip(), nome=str(row[2]).strip(), situacao=row[3], nivel=row[4], tecnologia=row[5],
                     data=data(row[6]), pf=num(row[7]), preco=num(row[8]), vt=num(row[9]), vi=num(row[10]), va=num(row[11]), obs=row[12]))

# ------------------------------------------------------------------ 3. laudos
LAUDOS = {}
for pid, (_, _, pasta) in PRODUTOS.items():
    d = F["laudos"] / pasta
    lj = next(d.glob("laudo_*.json"))
    LAUDOS[pid] = dict(cfg=json.loads(lj.read_text(encoding="utf-8")), res=json.loads((d / "resultado_laudo.json").read_text(encoding="utf-8")),
                       pdf=next(d.glob("LAUDO_TECNICO_AVALIACAO_*.pdf")).name, pasta=pasta)
CUR = {r["chave_sitec"]: r for r in csv.DictReader(open(F["curadoria"], encoding="utf-8"), delimiter=";")}
DIL = list(csv.DictReader(open(F["diligencias"], encoding="utf-8"), delimiter=";"))

# ------------------------------------------------------------------ 4. adquiridos
wa = openpyxl.load_workbook(F["adquiridos"], data_only=True)


def linhas_aba(nome, hr=5, c0=2):
    w = wa[nome]
    cab = [w.cell(hr, c).value for c in range(c0, w.max_column + 1)]
    n = len([x for x in cab if x])
    out = []
    for r in range(hr + 1, w.max_row + 1):
        v = [w.cell(r, c).value for c in range(c0, c0 + n)]
        if any(x not in (None, "") for x in v):
            out.append(dict(zip(cab[:n], v)))
    return out


LIC = [r for r in linhas_aba("Licenças 2026") if r.get("Item") not in (None, "TOTAL")]
CONC = {str(r["Nº Patrimônio"]).strip(): r for r in linhas_aba("Conciliação") if r.get("Nº Patrimônio")}
AMORT = [r for r in linhas_aba("Amortização SEAP") if isinstance(r.get("Parcela"), (int, float))]
SEAP_INFO = {r["Campo"]: r["Informação"] for r in linhas_aba("SEAP 2026") if r.get("Campo") and r.get("Informação") and r["Campo"] != "Item"}
assert len(LIC) == 18, len(LIC)
VALOR_SEAP = {2023: 96833.33, 2024: 96833.33, 2025: 3166000.00, 2026: 5254186.60}

# ------------------------------------------------------------------ dProduto
prod = []
hoje = date(2026, 11, 26)
for pid, (ksitec, _, pasta) in PRODUTOS.items():
    a, L = A26[ksitec], LAUDOS[pid]
    c, cur = L["cfg"], CUR[ksitec.split("|")[0] if "|" not in ksitec else ("WEB PONTO CLIENT" if "Client" in ksitec else "WEB PONTO")]
    integ = c.get("integracoes") or []
    prod.append({
        "ID Produto": pid, "Sigla": a["sigla"] if a["sigla"] != "WEB PONTO" else ("Web Ponto Client" if "Client" in ksitec else "Web Ponto"),
        "Nome do Produto": c.get("nome") or a["nome"], "Nome no Inventário": a["nome"], "Categoria": CAT_DEV,
        "Grupo": "Software desenvolvido internamente e/ou medido por pontos de função",
        "Situação": c.get("situacao") or a["situacao"], "Situação Resumida": resumo_situacao(c.get("situacao") or a["situacao"]),
        "Situação na Avaliação": a["situacao"], "Tecnologia": a["tecnologia"], "Nível de Medição": (a["nivel"] or "").replace("INDICATIVA", "Indicativa"),
        "Medida PF": c.get("medida") or L["res"].get("medida", ""), "Vida Útil": a["vida_util"], "Valor Institucional": a["vi"],
        "Faixa Valor Institucional": FAIXA_VI.get(a["vi"], ""), "Unidade de Desenvolvimento": c.get("unidade_desenvolvimento", ""),
        "Tipo de Bem": c.get("tipo_bem", ""), "Propriedade": texto(c.get("propriedade")), "Finalidade": texto(c.get("finalidade")),
        "Benefício": texto(c.get("beneficio")), "Base Legal": texto(c.get("base_legal")), "Áreas de Negócio": texto(c.get("areas_negocio"), "; "),
        "Perfis de Usuário": texto(c.get("perfis"), "; "), "Justificativa do VI": texto(c.get("vi_justificativa")), "Uso": texto(c.get("uso")),
        "Integrações": "; ".join(i[0] for i in integ if isinstance(i, list) and i), "Qtde Integrações": len(integ),
        "Qtde Módulos": len(L["res"].get("por_modulo") or {}), "Qtde Funções": L["res"].get("funcoes"),
        "Documentação": cur["documentacao"], "Principal Achado": cur["principal_achado"], "Diligências": cur["diligencias"],
        "Ressalva de Documentação": texto(c.get("ressalva_documentacao")), "Ressalvas": texto(c.get("ressalvas_extras")),
        "Motivo da Variação": texto(c.get("motivo_variacao")), "Fora do Escopo": texto(c.get("fora_do_escopo")),
        "Linha de Base": f'{c.get("baseline_nome", "")} {c.get("baseline_versao", "")}'.strip(),
        "Data da Avaliação": a["data"], "Laudo": L["pdf"], "Pasta do Laudo": f"4. Relatório Final/Laudos Técnicos de Avaliação/{pasta}",
        "Nº Laudo": int(pasta.split(".")[0]), "Patrimônio": "", "Fornecedor": "SEPLAG (equipe interna e/ou fábrica de software)",
        "Contrato": "", "Tipo de Licença": "", "Prazo da Licença": "", "Data de Aquisição": None, "Data Fim": None,
        "Situação da Licença": "", "Tem Custo de Projeto": "Sim" if "custo_projeto" in c else "Não",
    })
for r in LIC:
    pat = str(r["Nº Patrimônio (SIGPAT)"]).strip()
    fim = data(r.get("Data fim"))
    prod.append({
        "ID Produto": pat, "Sigla": pat, "Nome do Produto": str(r["Sigla / Nome"]).strip(), "Nome no Inventário": str(r["Sigla / Nome"]).strip(),
        "Categoria": CAT_LIC, "Grupo": "Software adquirido (licença e/ou de prateleira)", "Situação": r.get("Situação") or "Ativo",
        "Situação Resumida": "Licença com cessão encerrada" if fim and fim < hoje else "Licença vigente",
        "Situação na Avaliação": r.get("Situação") or "", "Tecnologia": "", "Nível de Medição": "Custo de aquisição (SIGPAT)", "Medida PF": "",
        "Vida Útil": "Definida (vigência da cessão)" if fim else "Indefinida (licença sem prazo)", "Valor Institucional": None,
        "Faixa Valor Institucional": "", "Unidade de Desenvolvimento": "", "Tipo de Bem": "Software adquirido", "Propriedade": "Direito de uso (licença)",
        "Finalidade": str(r.get("Descrição") or ""), "Benefício": "", "Base Legal": "", "Áreas de Negócio": "", "Perfis de Usuário": "",
        "Justificativa do VI": "", "Uso": "", "Integrações": "", "Qtde Integrações": 0, "Qtde Módulos": 0, "Qtde Funções": None,
        "Documentação": "Não disponibilizada (nota fiscal, contrato e certificado)", "Principal Achado": "", "Diligências": "D19",
        "Ressalva de Documentação": "", "Ressalvas": str(CONC.get(pat, {}).get("Observação") or ""), "Motivo da Variação": "", "Fora do Escopo": "",
        "Linha de Base": "", "Data da Avaliação": date(2026, 11, 26), "Laudo": "LAUDO_TECNICO_AVALIACAO_SOFTWARES_ADQUIRIDOS_2026.pdf",
        "Pasta do Laudo": "4. Relatório Final/Laudos Técnicos de Avaliação/37. Softwares Adquiridos", "Nº Laudo": 37, "Patrimônio": pat,
        "Fornecedor": str(r.get("Fornecedor") or ""), "Contrato": str(r.get("Contrato") or ""), "Tipo de Licença": str(r.get("Tipo de licença") or ""),
        "Prazo da Licença": str(r.get("Prazo da licença") or ""), "Data de Aquisição": data(r.get("Data de aquisição / início")), "Data Fim": fim,
        "Situação da Licença": "Encerrada em " + fim.strftime("%d/%m/%Y") if fim and fim < hoje else "Vigente ou sem prazo",
        "Tem Custo de Projeto": "Não",
    })
    if fim and fim < hoje:
        prod[-1]["Principal Achado"] = f"Cessão encerrada em {fim:%d/%m/%Y}, sem baixa nem amortização"
        prod[-1]["Diligências"] = "D01, D19"
    if pat == "C0045042":
        prod[-1]["Principal Achado"] = "Data de aquisição divergente das demais licenças do lote"
cs = json.loads((F["laudos"] / "38. SEAP" / "laudo_SEAP.json").read_text(encoding="utf-8"))
prod.append({
    "ID Produto": "SEAP", "Sigla": "SEAP", "Nome do Produto": "Sistema Estadual de Administração de Pessoas", "Nome no Inventário": "SEAP",
    "Categoria": CAT_SEAP, "Grupo": "Software adquirido (contrato com transferência de tecnologia)", "Situação": "Em produção",
    "Situação Resumida": "Em produção", "Situação na Avaliação": "Em produção", "Tecnologia": "", "Nível de Medição": "Valor do contrato",
    "Medida PF": "", "Vida Útil": "Definida: 12 meses (26/01/2026 a 25/01/2027)", "Valor Institucional": 1.0, "Faixa Valor Institucional": "Imprescindível",
    "Unidade de Desenvolvimento": "", "Tipo de Bem": "Software adquirido por contrato", "Propriedade": str(SEAP_INFO.get("Transferência de tecnologia (cláusulas 10.2.1, d, e 10.3.1)", "")),
    "Finalidade": str(SEAP_INFO.get("Objeto (cláusula 1.1)", "")), "Benefício": "", "Base Legal": str(SEAP_INFO.get("Fundamentação (cláusula 3.1)", "")),
    "Áreas de Negócio": "", "Perfis de Usuário": "", "Justificativa do VI": str(SEAP_INFO.get("Valor Institucional informado", "")), "Uso": "",
    "Integrações": "", "Qtde Integrações": 0, "Qtde Módulos": 0, "Qtde Funções": None, "Documentação": "Contrato nº 001/2026/SEPLAG",
    "Principal Achado": "Sucessão pelo SIGEP sem plano formal; prorrogação a comunicar", "Diligências": "D07",
    "Ressalva de Documentação": "", "Ressalvas": "", "Motivo da Variação": "Avaliado pelo valor do Contrato nº 001/2026/SEPLAG (cláusula 2.2)",
    "Fora do Escopo": "", "Linha de Base": "", "Data da Avaliação": date(2026, 11, 26), "Laudo": "LAUDO_TECNICO_AVALIACAO_SEAP_2026.pdf",
    "Pasta do Laudo": "4. Relatório Final/Laudos Técnicos de Avaliação/38. SEAP", "Nº Laudo": 38, "Patrimônio": "",
    "Fornecedor": "Techne Engenharia e Sistemas Ltda.", "Contrato": "Contrato nº 001/2026/SEPLAG", "Tipo de Licença": "Contrato de serviços com transferência de tecnologia",
    "Prazo da Licença": str(SEAP_INFO.get("Vigência (cláusula 4.2)", "")), "Data de Aquisição": date(2026, 1, 26), "Data Fim": date(2027, 1, 25),
    "Situação da Licença": "Vigente", "Tem Custo de Projeto": "Não",
})
dProduto = pd.DataFrame(prod)

# ------------------------------------------------------------------ fAvaliacao
fav = []
SIG2PID = {}
for pid, (_, siglas, _) in PRODUTOS.items():
    for s in siglas:
        SIG2PID[s] = pid
for h in HIST:
    k = chave_planilha(h["sigla"], h["nome"])
    if h["sigla"] == "SEAP":
        fav.append(dict(pid="SEAP", ano=h["ano"], cat=CAT_SEAP, sit=h["situacao"], niv=h["nivel"], pf=None, preco=None, vt=VALOR_SEAP[h["ano"]],
                        vi=None, va=VALOR_SEAP[h["ano"]], fonte=f"Dados.xlsx (inventário {h['ano']})"))
        aud(f"SEAP {h['ano']} no Dados.xlsx", h["va"], VALOR_SEAP[h["ano"]])
        continue
    pid = SIG2PID[k]
    fav.append(dict(pid=pid, ano=h["ano"], cat=CAT_DEV, sit=h["situacao"], niv=h["nivel"], pf=h["pf"], preco=h["preco"], vt=h["vt"], vi=h["vi"], va=h["va"],
                    fonte=f"Dados.xlsx (inventário {h['ano']})"))
for pid, (ksitec, _, _) in PRODUTOS.items():
    a = A26[ksitec]
    fav.append(dict(pid=pid, ano=2026, cat=CAT_DEV, sit=a["situacao"], niv=a["nivel"], pf=a["pf"], preco=a["preco"], vt=a["vt"], vi=a["vi"], va=a["va"],
                    fonte="Inventário de Sistemas SITEC-2026, aba Avaliação 2026"))
    aud(f"VA do laudo x aba Avaliação 2026 ({pid})", LAUDOS[pid]["res"]["va"], a["va"], 0.01)
    aud(f"PF do laudo x aba Avaliação 2026 ({pid})", LAUDOS[pid]["res"]["pf"], a["pf"], 0.001)
fav.append(dict(pid="SEAP", ano=2026, cat=CAT_SEAP, sit="Em produção", niv="Valor do contrato", pf=None, preco=None, vt=VALOR_SEAP[2026], vi=1.0,
                va=VALOR_SEAP[2026], fonte="Contrato nº 001/2026/SEPLAG; Laudo Técnico de Avaliação do SEAP"))
for r in LIC:
    pat = str(r["Nº Patrimônio (SIGPAT)"]).strip()
    c = CONC[pat]
    for ano, col in [(2023, "2023 (versão final)"), (2024, "2024 (versão final)"), (2025, "2025"), (2026, "2026")]:
        v = c.get(col)
        if isinstance(v, (int, float)):
            fav.append(dict(pid=pat, ano=ano, cat=CAT_LIC, sit="Ativo", niv="Custo de aquisição", pf=None, preco=None, vt=v, vi=None, va=v,
                            fonte="Levantamento dos adquiridos 2026, aba Conciliação"))
fAvaliacao = pd.DataFrame(fav).rename(columns={
    "pid": "ID Produto", "ano": "Ano Inventário", "cat": "Categoria", "sit": "Situação", "niv": "Nível de Medição", "pf": "Tamanho Funcional (PF)",
    "preco": "Preço PF (R$)", "vt": "Valor Bruto VT (R$)", "vi": "Valor Institucional", "va": "Valor Final VA (R$)", "fonte": "Fonte"})

# ------------------------------------------------------------------ fatos dos laudos
fmod, ffun, fint, fhist = [], [], [], []
TIPOS = {"ALI": ("Arquivo Lógico Interno", "Dado"), "AIE": ("Arquivo de Interface Externa", "Dado"), "EE": ("Entrada Externa", "Transação"),
         "CE": ("Consulta Externa", "Transação"), "SE": ("Saída Externa", "Transação")}
for pid, L in LAUDOS.items():
    for mod, pf in (L["res"].get("por_modulo") or {}).items():
        us = (L["cfg"].get("modulos") or {}).get(mod)
        fmod.append({"ID Produto": pid, "Módulo": mod, "Tamanho Funcional (PF)": float(pf), "Qtde Histórias": len(us) if isinstance(us, list) else None})
    for t, (q, pf) in (L["res"].get("por_tipo") or {}).items():
        ffun.append({"ID Produto": pid, "Tipo de Função": t, "Qtde Funções": int(q), "Tamanho Funcional (PF)": float(pf)})
    for i in L["cfg"].get("integracoes") or []:
        if isinstance(i, list) and i:
            fint.append({"ID Produto": pid, "Sistema Integrado": i[0], "Dados Trocados": i[1] if len(i) > 1 else "", "Forma": i[2] if len(i) > 2 else ""})
    for h in L["cfg"].get("historico_medicoes") or []:
        fhist.append({"ID Produto": pid, "Ano Inventário": int(h.get("inventario")), "Data da Medição": h.get("data", ""), "Tamanho Funcional (PF)": num(h.get("pf")),
                      "Nível de Medição": h.get("nivel", ""), "Situação": h.get("situacao", ""), "Observação": h.get("uso", "")})
fModulo, fFuncao, fIntegracao, fHistoricoLaudo = map(pd.DataFrame, (fmod, ffun, fint, fhist))
dTipoFuncao = pd.DataFrame([{"Tipo de Função": k, "Descrição": v[0], "Natureza": v[1], "Ordem": i + 1} for i, (k, v) in enumerate(TIPOS.items())])

# ------------------------------------------------------------------ custos e economicidade
fcus, feco = [], []
for pid, L in LAUDOS.items():
    cp = L["cfg"].get("custo_projeto")
    if not cp:
        continue
    constr = set(cp.get("componentes_construcao") or [])
    for nome, v in cp["componentes"]:
        tipo = "Construção" if nome in constr else ("Tickets" if "Ticket" in nome else ("Pontos de função de teste" if "teste" in nome.lower() else "Outros"))
        fcus.append({"ID Produto": pid, "Componente": nome, "Tipo de Custo": tipo, "Valor (R$)": float(v)})
    total = float(cp["custo_total"])
    aud(f"Componentes do custo ({pid})", sum(float(v) for _, v in cp["componentes"]), total)
    a = A26[PRODUTOS[pid][0]]
    pf_fat = float(cp["pf_faturado"])
    preco_c = float(cp["preco_contrato"])
    # O custo pago já embute os percentuais de cada grupo de atividades e os deflatores do contrato; o mesmo serviço
    # a preço de mercado é o custo convertido do preço do PF no contrato para o preço de referência do inventário.
    pf_equiv = total / preco_c
    mercado = pf_equiv * PRECO_2026
    feco.append({
        "ID Produto": pid, "Período": "Acumulado até 07/2026", "PF Faturado": pf_fat, "Preço PF Contrato (R$)": float(cp.get("preco_contrato") or 0),
        "Nota Preço Contrato": cp.get("nota_preco_contrato", ""), "Custo Total Pago (R$)": total,
        "Custo de Construção (R$)": sum(float(v) for n, v in cp["componentes"] if n in constr),
        "Custo Médio por PF Faturado (R$)": total / pf_fat, "PF Equivalentes Pagos": pf_equiv, "Preço PF Mercado 2026 (R$)": PRECO_2026,
        "Custo do Volume a Preço de Mercado (R$)": mercado, "Economia vs Mercado (R$)": mercado - total, "% Economia": (mercado - total) / mercado,
        "PF Medido 2026": a["pf"], "VT 2026 (R$)": a["vt"], "VA 2026 (R$)": a["va"],
        "Retorno VT por R$ 1": a["vt"] / total, "Retorno VA por R$ 1": a["va"] / total,
        "Fator Grupo Contratado": cp.get("fator_grupo_contratado"), "Fonte": cp.get("fonte", CFG["parametros"]["referencia_custos"]),
    })
fCustoProjeto, fEconomicidade = pd.DataFrame(fcus), pd.DataFrame(feco)
if F.get("faturamento_trd") and F["faturamento_trd"].is_file():  # abertura opcional por ano (projeto custos-projetos-fsw)
    trd = pd.read_parquet(F["faturamento_trd"])
    trd.to_parquet(SAIDA / "fFaturamentoTRD.parquet", index=False)
    print("  base de TRD incorporada:", len(trd), "linhas")

fAmortizacaoSEAP = pd.DataFrame([{
    "Parcela": int(r["Parcela"]), "Início do Período": data(r["Início do período"]), "Fim do Período": data(r["Fim do período"]),
    "Amortização do Mês (R$)": float(r["Amortização do mês (R$)"]), "Amortização Acumulada (R$)": float(r["Amortização acumulada (R$)"]),
    "Valor Contábil Líquido (R$)": float(r["Valor contábil líquido (R$)"]), "Marco": r.get("Marco") or ""} for r in AMORT])

# ------------------------------------------------------------------ dimensões de apoio
dInventario = pd.DataFrame([
    {"Ano Inventário": 2023, "Inventário": "2023", "Preço PF Mercado (R$)": 705.60, "Portaria": "Portaria nº 077/2023/SEPLAG", "Data de Referência": date(2023, 12, 31), "Fonte do Preço": "Inventário de 2023 (Dados.xlsx)"},
    {"Ano Inventário": 2024, "Inventário": "2024", "Preço PF Mercado (R$)": 707.64, "Portaria": "Portaria nº 121/2024/SEPLAG", "Data de Referência": date(2024, 12, 31), "Fonte do Preço": "Inventário de 2024 (Dados.xlsx); SIAG avaliado a R$ 705,60"},
    {"Ano Inventário": 2025, "Inventário": "2025", "Preço PF Mercado (R$)": 943.25, "Portaria": "Portaria nº 138/2025/SEPLAG", "Data de Referência": date(2025, 12, 31), "Fonte do Preço": "Sigadoc SEPLAG-DIC-2025/36270"},
    {"Ano Inventário": 2026, "Inventário": "2026", "Preço PF Mercado (R$)": 1215.09, "Portaria": "Portaria nº 124/2026/SEPLAG", "Data de Referência": date(2026, 11, 26), "Fonte do Preço": "Sigadoc SEPLAG-DIC-2026/59859 (aprovação); 59836-A (pesquisa); 59842-A (manifestação)"},
])
dPrecoPF = pd.DataFrame([
    {"Referência": "Mercado - inventário 2023", "Tipo": "Mercado", "Data": date(2023, 12, 31), "Preço PF (R$)": 705.60, "Fonte": "Dados.xlsx"},
    {"Referência": "Mercado - inventário 2024", "Tipo": "Mercado", "Data": date(2024, 12, 31), "Preço PF (R$)": 707.64, "Fonte": "Dados.xlsx"},
    {"Referência": "Mercado - inventário 2025", "Tipo": "Mercado", "Data": date(2025, 12, 31), "Preço PF (R$)": 943.25, "Fonte": "SEPLAG-DIC-2025/36270"},
    {"Referência": "Mercado - inventário 2026", "Tipo": "Mercado", "Data": date(2026, 11, 26), "Preço PF (R$)": 1215.09, "Fonte": "SEPLAG-DIC-2026/59859"},
    {"Referência": "Contrato nº 014/2022/SEPLAG - 2022", "Tipo": "Contrato", "Data": date(2022, 7, 1), "Preço PF (R$)": 457.00, "Fonte": "Laudos (custo de projeto)"},
    {"Referência": "Contrato nº 014/2022/SEPLAG - 05/2025", "Tipo": "Contrato", "Data": date(2025, 5, 1), "Preço PF (R$)": 519.99, "Fonte": "Laudos (custo de projeto)"},
    {"Referência": "Contrato nº 014/2022/SEPLAG - 5º Termo de Apostilamento", "Tipo": "Contrato", "Data": date(2026, 5, 1), "Preço PF (R$)": 544.53, "Fonte": "Laudos (custo de projeto)"},
])
dDiligencia = pd.DataFrame([{"Código": d["codigo"], "Objeto": d["objeto"], "Destinatário": d["destinatario"], "Fundamento": d["fundamento"],
                             "Prazo Sugerido": d["prazo"], "Prioritária": "Sim" if "Prioritária" in d["prazo"] else "Não", "Ordem": i + 1} for i, d in enumerate(DIL)])
bProdutoDiligencia = pd.DataFrame([{"ID Produto": p["ID Produto"], "Código": c.strip()} for p in prod for c in str(p["Diligências"]).split(",") if c.strip()])

# ------------------------------------------------------------------ cenários "E se?" e ponte 2025 -> 2026 (desenvolvidos)
P25, P26 = 943.25, PRECO_2026
d25 = {r["ID Produto"]: r for r in fAvaliacao[(fAvaliacao["Ano Inventário"] == 2025) & (fAvaliacao.Categoria == CAT_DEV)].to_dict("records")}
d26 = {r["ID Produto"]: r for r in fAvaliacao[(fAvaliacao["Ano Inventário"] == 2026) & (fAvaliacao.Categoria == CAT_DEV)].to_dict("records")}
ponte = []
for pid, b in d26.items():
    a = d25.get(pid)
    if a:
        e_preco = a["Tamanho Funcional (PF)"] * P26 * (1 + a["Valor Institucional"]) - a["Valor Final VA (R$)"]
        e_tam = (b["Tamanho Funcional (PF)"] - a["Tamanho Funcional (PF)"]) * P26 * (1 + a["Valor Institucional"])
        e_vi = b["Valor Final VA (R$)"] - (a["Valor Final VA (R$)"] + e_preco + e_tam)
        ponte.append({"ID Produto": pid, "Situação no Período": "Mantido", "PF 2025": a["Tamanho Funcional (PF)"], "PF 2026": b["Tamanho Funcional (PF)"],
                      "Variação PF": b["Tamanho Funcional (PF)"] - a["Tamanho Funcional (PF)"], "VI 2025": a["Valor Institucional"], "VI 2026": b["Valor Institucional"],
                      "VA 2025 (R$)": a["Valor Final VA (R$)"], "VA 2026 (R$)": b["Valor Final VA (R$)"], "Efeito Preço (R$)": e_preco,
                      "Efeito Tamanho (R$)": e_tam, "Efeito VI (R$)": e_vi, "Efeito Novo Sistema (R$)": 0.0})
    else:
        ponte.append({"ID Produto": pid, "Situação no Período": "Novo em 2026", "PF 2025": 0.0, "PF 2026": b["Tamanho Funcional (PF)"],
                      "Variação PF": b["Tamanho Funcional (PF)"], "VI 2025": None, "VI 2026": b["Valor Institucional"], "VA 2025 (R$)": 0.0,
                      "VA 2026 (R$)": b["Valor Final VA (R$)"], "Efeito Preço (R$)": 0.0, "Efeito Tamanho (R$)": 0.0, "Efeito VI (R$)": 0.0,
                      "Efeito Novo Sistema (R$)": b["Valor Final VA (R$)"]})
assert set(d25) <= set(d26), set(d25) - set(d26)
fPonte = pd.DataFrame(ponte)
fPonte["Variação Total (R$)"] = fPonte["VA 2026 (R$)"] - fPonte["VA 2025 (R$)"]
fPonte["Movimento do Tamanho"] = fPonte.apply(lambda r: "Novo sistema" if r["Situação no Período"] != "Mantido" else
                                              ("Aumentou" if r["Variação PF"] > 0.001 else ("Diminuiu" if r["Variação PF"] < -0.001 else "Sem alteração")), axis=1)
k = fPonte[fPonte["Situação no Período"] == "Mantido"]; n = fPonte[fPonte["Situação no Período"] != "Mantido"]
real25, real26 = sum(r["Valor Final VA (R$)"] for r in d25.values()), sum(r["Valor Final VA (R$)"] for r in d26.values())
c1 = (k["PF 2025"] * P26 * (1 + k["VI 2025"])).sum()
c3 = (k["PF 2026"] * P25 * (1 + k["VI 2025"])).sum()
c4 = sum(r["Tamanho Funcional (PF)"] * P25 * (1 + r["Valor Institucional"]) for r in d26.values())
c5 = (k["PF 2026"] * P26 * (1 + k["VI 2025"])).sum() + n["VA 2026 (R$)"].sum()
CEN = [
    (1, "Real 2025", "Como o inventário de 2025 avaliou", "31 sistemas, PF e VI de 2025, preço de R$ 943,25", len(k), k["PF 2025"].sum(), P25, real25),
    (2, "2025 ao preço de 2026", "Quanto valeriam os mesmos sistemas de 2025 só com o novo preço do PF?", "31 sistemas, PF e VI de 2025, preço de R$ 1.215,09", len(k), k["PF 2025"].sum(), P26, c1),
    (3, "2025 ao preço de 2026 + novos de 2026", "E se, além do preço, entrassem os 8 sistemas novos?", "C2 + 8 sistemas avaliados pela primeira vez em 2026", len(fPonte), k["PF 2025"].sum() + n["PF 2026"].sum(), P26, c1 + n["VA 2026 (R$)"].sum()),
    (4, "2025 com o tamanho de 2026, preço de 2025", "Quanto pesou o crescimento do tamanho funcional dos mesmos sistemas?", "31 sistemas, PF de 2026, VI de 2025, preço de R$ 943,25", len(k), k["PF 2026"].sum(), P25, c3),
    (5, "2026 com o VI de 2025", "Quanto pesou a revisão do Valor Institucional?", "39 sistemas, PF de 2026, preço de 2026, VI de 2025 nos mantidos", len(fPonte), fPonte["PF 2026"].sum(), P26, c5),
    (6, "2026 ao preço de 2025", "Quanto valeria o inventário de 2026 se o PF não tivesse mudado de preço?", "39 sistemas, PF e VI de 2026, preço de R$ 943,25", len(fPonte), fPonte["PF 2026"].sum(), P25, c4),
    (7, "Real 2026", "Como o inventário de 2026 avaliou", "39 sistemas, PF e VI de 2026, preço de R$ 1.215,09", len(fPonte), fPonte["PF 2026"].sum(), P26, real26)]
fCenario = pd.DataFrame([{"Ordem": o, "Cenário": c, "Pergunta": q, "Premissas": pr_, "Sistemas": ns, "Tamanho Funcional (PF)": pf, "Preço PF (R$)": pp,
                          "Valor (R$)": v, "Diferença para o Real 2026 (R$)": v - real26, "Diferença para o Real 2025 (R$)": v - real25} for o, c, q, pr_, ns, pf, pp, v in CEN])
FATORES = [(1, "Inventário 2025", real25), (2, "Preço do PF", k["Efeito Preço (R$)"].sum()), (3, "Tamanho funcional", k["Efeito Tamanho (R$)"].sum()),
           (4, "Valor Institucional", k["Efeito VI (R$)"].sum()), (5, "Novos sistemas", n["Efeito Novo Sistema (R$)"].sum())]
fPonteFator = pd.DataFrame([{"Ordem": o, "Fator": f, "Valor (R$)": v} for o, f, v in FATORES])
aud("Ponte 2025 -> 2026 fecha no total de 2026", fPonteFator["Valor (R$)"].sum(), real26)
aud("Efeito preço igual ao do relatório dos desenvolvidos", k["Efeito Preço (R$)"].sum(), 12962010.80)
aud("Efeito novos sistemas igual ao do relatório dos desenvolvidos", n["Efeito Novo Sistema (R$)"].sum(), 7463690.33)

# ------------------------------------------------------------------ conferências com os valores publicados
f26 = fAvaliacao[fAvaliacao["Ano Inventário"] == 2026]
aud("Total desenvolvidos internamente 2026 (aba, linha TOTAL)", f26[f26.Categoria == CAT_DEV]["Valor Final VA (R$)"].sum(), TOT26[1])
aud("Total desenvolvidos internamente 2026 (relatório)", f26[f26.Categoria == CAT_DEV]["Valor Final VA (R$)"].sum(), 70234996.71)
aud("PF total 2026", f26["Tamanho Funcional (PF)"].sum(), 31732.8, 0.001)
aud("Licenças 2026", f26[f26.Categoria == CAT_LIC]["Valor Final VA (R$)"].sum(), 3121832.16)
aud("SEAP 2026", f26[f26.Categoria == CAT_SEAP]["Valor Final VA (R$)"].sum(), 5254186.60)
aud("Total geral 2026 (Relatório Resumido)", f26["Valor Final VA (R$)"].sum(), 78611015.47)
for ano, esp in [(2025, 51264350.29), (2024, 28266644.86)]:
    aud(f"Total geral {ano}", fAvaliacao[fAvaliacao["Ano Inventário"] == ano]["Valor Final VA (R$)"].sum(), esp)
aud("Desenvolvidos 2025 (relatório consolidado)", fAvaliacao[(fAvaliacao["Ano Inventário"] == 2025) & (fAvaliacao.Categoria == CAT_DEV)]["Valor Final VA (R$)"].sum(), 44976518.13)
aud("Desenvolvidos 2024 sem o SEAP", fAvaliacao[(fAvaliacao["Ano Inventário"] == 2024) & (fAvaliacao.Categoria == CAT_DEV)]["Valor Final VA (R$)"].sum(), 26249155.48)
aud("Custo de projeto registrado (9 sistemas)", fCustoProjeto["Valor (R$)"].sum(), 9368136.99)
aud("Amortização SEAP acumulada", fAmortizacaoSEAP["Amortização do Mês (R$)"].sum(), 5254186.60)
aud("Produtos no catálogo", len(dProduto), 58, 0)

# ------------------------------------------------------------------ grava
SAIDA.mkdir(parents=True, exist_ok=True)
TABELAS = {"dProduto": dProduto, "dInventario": dInventario, "dPrecoPF": dPrecoPF, "dDiligencia": dDiligencia, "dTipoFuncao": dTipoFuncao,
           "fAvaliacao": fAvaliacao, "fModulo": fModulo, "fFuncao": fFuncao, "fIntegracao": fIntegracao, "fHistoricoLaudo": fHistoricoLaudo,
           "fCustoProjeto": fCustoProjeto, "fEconomicidade": fEconomicidade, "fAmortizacaoSEAP": fAmortizacaoSEAP, "bProdutoDiligencia": bProdutoDiligencia,
           "fPonte": fPonte, "fCenario": fCenario, "fPonteFator": fPonteFator,
           "dCenarioA": fCenario[["Ordem", "Cenário"]].copy(), "dCenarioB": fCenario[["Ordem", "Cenário"]].copy()}
for nome, df in TABELAS.items():
    for c in df.columns:
        if df[c].map(lambda x: isinstance(x, date)).any():
            df[c] = pd.to_datetime(df[c])
    df.to_parquet(SAIDA / f"{nome}.parquet", index=False)
    print(f"  {nome:22s} {len(df):5d} linhas  {len(df.columns):3d} colunas")
pd.DataFrame(AUD).to_csv(SAIDA / "auditoria_etl.csv", index=False, sep=";", encoding="utf-8-sig")
falhas = [a for a in AUD if a["OK"] != "Sim"]
print(f"Conferências: {len(AUD) - len(falhas)} de {len(AUD)} conferem")
for a in falhas:
    print("  DIVERGÊNCIA:", a)
sys.exit(1 if falhas else 0)
