"""
Gera o projeto Power BI (PBIP: modelo TMDL + relatório PBIR) do Catálogo de Produtos de Software 2026.

Identidade visual 60-30-10: Porcelana Gelada (fundos, 60%), Azul Mergulho (estrutura, 30%) e Laranja
Mandarina (destaque, 10%). O "cromo" das páginas (cabeçalho, abas, molduras, rótulos e ícones) é desenhado
em SVG de fundo; os números vêm de medidas DAX em visuais transparentes posicionados sobre as molduras.

Páginas: Capa · Visão Geral · Desenvolvidos · Adquiridos · Economicidade · Operacional · Ficha do Produto
Tooltips: Produto · Economia

O projeto é recriado do zero a cada execução (pasta "3.3. Power BI").
"""
import base64
import io
import json
import re
import shutil
import tomllib
import uuid
from pathlib import Path

import pyarrow.parquet as pq
from PIL import Image, ImageFilter

from medidas import MEDIDAS

AQUI = Path(__file__).resolve().parent
CFG = tomllib.loads((AQUI / "config.toml").read_text(encoding="utf-8"))
DADOS = (AQUI / CFG["saida"]["parquet"]).resolve()
RAIZ = (AQUI / CFG["powerbi"]["pasta"]).resolve()
NOME = CFG["powerbi"]["nome"]
ASSETS = AQUI / "assets"
REP, SMD = RAIZ / f"{NOME}.Report", RAIZ / f"{NOME}.SemanticModel"
DEF, RES = REP / "definition", REP / "StaticResources" / "RegisteredResources"
SM = SMD / "definition"

# ---------------------------------------------------------------- paleta 60-30-10
PORC, CARD, LINHA = "#E0ECEA", "#FBFDFC", "#C8D9D6"            # 60% Porcelana Gelada
AZUL, AZUL_ESC, AZUL_MED, AZUL_CL = "#155C78", "#0E3A4D", "#3F7F96", "#D5E6EC"   # 30% Azul Mergulho
LAR, LAR_CL = "#FF8C42", "#FFE6D5"                             # 10% Laranja Mandarina
CINZA_CL = "#D9EAF0"
TEXTO, APOIO, SUAVE = "#0E2F3C", "#4E6B76", "#7D949B"
CORES_DADOS = [AZUL, LAR, "#6FA0B3", AZUL_ESC, "#B9D3DA", "#C77A3F", "#5E7C88", "#9FC2B9"]


def tag():
    return str(uuid.uuid4())


def gravar(p, s):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(s, encoding="utf-8", newline="\n")


def qn(nome):
    return f"'{nome}'" if re.search(r"[^\w]", nome) or nome[0].isdigit() else nome


# ================================================================= MODELO SEMÂNTICO (TMDL)
CUR = '"R$"\\ #,0.00;-"R$"\\ #,0.00;"R$"\\ #,0.00'
OCULTAS = {"ID Produto", "Ordem", "Ano Inventário"}
SORT_BY = {("dInventario", "Inventário"): "Ano Inventário", ("dTipoFuncao", "Tipo de Função"): "Ordem", ("dDiligencia", "Código"): "Ordem",
           ("fCenario", "Cenário"): "Ordem", ("dCenarioA", "Cenário"): "Ordem", ("dCenarioB", "Cenário"): "Ordem", ("fPonteFator", "Fator"): "Ordem"}
GRUPO = {"d": "Dimensões", "f": "Fatos", "b": "Fatos"}


def tipo_col(t):
    s = str(t)
    if s.startswith("timestamp") or s.startswith("date"):
        return "dateTime"
    if s in ("double", "float"):
        return "double"
    if s.startswith("int"):
        return "int64"
    if s == "bool":
        return "boolean"
    return "string"


def fmt_col(nome, tipo):
    if tipo == "dateTime":
        return "dd/mm/yyyy"
    if tipo not in ("double", "int64"):
        return None
    if "(R$)" in nome:
        return CUR
    if nome.startswith("%") or "% " in nome:
        return "0.0%;-0.0%;0.0%"
    if "Retorno" in nome:
        return '"R$"\\ #,0.00'
    if "PF" in nome or "Tamanho" in nome:
        return "#,0.0"
    if nome in ("Valor Institucional", "Fator Grupo Contratado"):
        return "0.00"
    return "0" if tipo == "int64" else "#,0.00"


def tabela_tmdl(nome):
    esquema = pq.read_schema(DADOS / f"{nome}.parquet")
    oculta_ids = nome[0] in "fb"
    corpo = f"table {nome}\n\tlineageTag: {tag()}\n\n"
    datas = []
    for campo in esquema:
        c, t = campo.name, tipo_col(campo.type)
        if t == "dateTime":
            datas.append(c)
        linhas = [f"\tcolumn {qn(c)}", f"\t\tdataType: {t}"]
        f = fmt_col(c, t)
        if f:
            linhas.append(f"\t\tformatString: {tmdl_valor(f)}")
        if (c in OCULTAS and (oculta_ids or c == "Ordem")) or c == "Ordem":
            linhas.append("\t\tisHidden")
        resumo = "sum" if t in ("double", "int64") and c not in ("Ano Inventário", "Nº Laudo", "Parcela", "Ordem", "Valor Institucional",
                                                                "Preço PF (R$)", "Preço PF Mercado (R$)", "Preço PF Contrato (R$)") else "none"
        linhas += [f"\t\tlineageTag: {tag()}", f"\t\tsummarizeBy: {resumo}", f"\t\tsourceColumn: {c}"]
        if (nome, c) in SORT_BY:
            linhas.append(f"\t\tsortByColumn: {qn(SORT_BY[(nome, c)])}")
        linhas += ["", "\t\tannotation SummarizationSetBy = Automatic"]
        if t == "dateTime":
            linhas += ["", "\t\tannotation UnderlyingDateTimeDataType = Date"]
        corpo += "\n".join(linhas) + "\n\n"
    passos = ""
    if datas:
        lista = ", ".join('{"%s", type date}' % d for d in datas)
        passos = f",\n    Resultado = Table.TransformColumnTypes(Fonte, {{{lista}}})"
    else:
        passos = ",\n    Resultado = Fonte"
    m = (f'let\n    Fonte = Parquet.Document(File.Contents(PastaDados & "\\{nome}.parquet"), '
         f"[Compression=null, LegacyColumnNameEncoding=false, MaxDepth=null]){passos}\nin\n    Resultado")
    m_ind = "\n".join("\t\t\t\t" + l for l in m.split("\n"))
    corpo += (f"\tpartition {nome} = m\n\t\tmode: import\n\t\tqueryGroup: {GRUPO[nome[0]]}\n\t\tsource =\n{m_ind}\n\n"
              "\tannotation PBI_NavigationStepName = Navegação\n\n\tannotation PBI_ResultType = Table\n")
    gravar(SM / "tables" / f"{nome}.tmdl", corpo)


def tmdl_valor(v):
    """Valor de propriedade TMDL: com aspas internas, envolve em aspas e duplica as internas."""
    v = str(v)
    if '"' in v or v != v.strip():
        return '"' + v.replace('"', '""') + '"'
    return v


def medidas_tmdl():
    corpo = f"table Medidas\n\tlineageTag: {tag()}\n\n"
    for nome, expr, fmt, pasta, desc in MEDIDAS:
        if desc:
            corpo += f"\t/// {desc}\n"
        linhas = expr.split("\n")
        if len(linhas) == 1:
            corpo += f"\tmeasure {qn(nome)} = {expr}\n"
        else:
            corpo += f"\tmeasure {qn(nome)} =\n" + "\n".join("\t\t\t" + l for l in linhas) + "\n"
        if fmt:
            corpo += f"\t\tformatString: {tmdl_valor(fmt)}\n"
        corpo += f"\t\tdisplayFolder: {pasta}\n\t\tlineageTag: {tag()}\n\n"
    corpo += (f"\tcolumn Coluna\n\t\tdataType: string\n\t\tisHidden\n\t\tlineageTag: {tag()}\n\t\tsummarizeBy: none\n\t\tsourceColumn: Coluna\n\n"
              "\t\tannotation SummarizationSetBy = Automatic\n\n"
              "\tpartition Medidas = m\n\t\tmode: import\n\t\tqueryGroup: Dimensões\n\t\tsource =\n"
              "\t\t\t\tlet\n\t\t\t\t    Fonte = #table(type table [Coluna = text], {})\n\t\t\t\tin\n\t\t\t\t    Fonte\n\n"
              "\tannotation PBI_ResultType = Table\n")
    gravar(SM / "tables" / "Medidas.tmdl", corpo)


RELACOES = [("fAvaliacao", "ID Produto", "dProduto", "ID Produto", False), ("fAvaliacao", "Ano Inventário", "dInventario", "Ano Inventário", False),
            ("fModulo", "ID Produto", "dProduto", "ID Produto", False), ("fFuncao", "ID Produto", "dProduto", "ID Produto", False),
            ("fFuncao", "Tipo de Função", "dTipoFuncao", "Tipo de Função", False), ("fIntegracao", "ID Produto", "dProduto", "ID Produto", False),
            ("fHistoricoLaudo", "ID Produto", "dProduto", "ID Produto", False), ("fCustoProjeto", "ID Produto", "dProduto", "ID Produto", False),
            ("fEconomicidade", "ID Produto", "dProduto", "ID Produto", False), ("bProdutoDiligencia", "ID Produto", "dProduto", "ID Produto", False),
            ("bProdutoDiligencia", "Código", "dDiligencia", "Código", True), ("fPonte", "ID Produto", "dProduto", "ID Produto", False)]


def gera_modelo():
    tabelas = sorted(p.stem for p in DADOS.glob("*.parquet") if p.stem != "fFaturamentoTRD")
    for t in tabelas:
        tabela_tmdl(t)
    medidas_tmdl()
    gravar(SM / "database.tmdl", "database\n\tcompatibilityLevel: 1600\n\n")
    refs = "".join(f"ref table {qn(t)}\n" for t in ["Medidas"] + tabelas)
    gravar(SM / "model.tmdl",
           "model Model\n\tculture: pt-BR\n\tdefaultPowerBIDataSourceVersion: powerBI_V3\n\tsourceQueryCulture: pt-BR\n\tdataAccessOptions\n"
           "\t\tlegacyRedirects\n\t\treturnErrorValuesAsNull\n\n"
           "queryGroup Dimensões\n\n\tannotation PBI_QueryGroupOrder = 0\n\nqueryGroup Fatos\n\n\tannotation PBI_QueryGroupOrder = 1\n\n"
           "queryGroup Parâmetros\n\n\tannotation PBI_QueryGroupOrder = 2\n\n"
           "annotation __PBI_TimeIntelligenceEnabled = 0\n\n"
           f'annotation PBI_QueryOrder = {json.dumps(["PastaDados"] + tabelas + ["Medidas"], ensure_ascii=False)}\n\n'
           'annotation PBI_ProTooling = ["DevMode"]\n\n' + refs)
    pasta = CFG["powerbi"]["pasta_dados"].replace('"', '""')
    gravar(SM / "expressions.tmdl",
           f'expression PastaDados = "{pasta}" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]\n'
           f"\tlineageTag: {tag()}\n\tqueryGroup: Parâmetros\n\n\tannotation PBI_ResultType = Text\n")
    rel = ""
    for ft, fc, dt, dc, ambos in RELACOES:
        rel += f"relationship {tag()}\n"
        if ambos:
            rel += "\tcrossFilteringBehavior: bothDirections\n"
        rel += f"\tfromColumn: {ft}.{qn(fc)}\n\ttoColumn: {dt}.{qn(dc)}\n\n"
    gravar(SM / "relationships.tmdl", rel)
    gravar(SMD / "definition.pbism", json.dumps({"$schema": "https://developer.microsoft.com/json-schemas/fabric/item/semanticModel/definitionProperties/1.0.0/schema.json",
                                                 "version": "4.2", "settings": {}}, indent=2))
    gravar(SMD / ".platform", json.dumps({"$schema": "https://developer.microsoft.com/json-schemas/fabric/gitIntegration/platformProperties/2.0.0/schema.json",
                                          "metadata": {"type": "SemanticModel", "displayName": NOME}, "config": {"version": "2.0", "logicalId": tag()}}, indent=2))
    return tabelas


# ================================================================= RELATÓRIO (PBIR)
SCHEMA_VC = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.5.0/schema.json"
SCHEMA_PG = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.0.0/schema.json"
PAGINAS = {  # chave -> (id fixo de 20 caracteres, nome)
    "capa": ("ca7a10900000000000a1", "Capa"), "geral": ("ca7a10900000000000b2", "Visão Geral"),
    "dev": ("ca7a10900000000000c3", "Desenvolvidos"), "adq": ("ca7a10900000000000d4", "Adquiridos"),
    "eco": ("ca7a10900000000000e5", "Economicidade"), "ope": ("ca7a10900000000000f6", "Operacional"),
    "ficha": ("ca7a1090000000000017", "Ficha do Produto"),
    "cen": ("ca7a109000000000004a", "Cenários"), "ponte": ("ca7a109000000000005b", "Ponte 2025-2026"),
    "tt_prod": ("ca7a1090000000000028", "Tooltip Produto"), "tt_eco": ("ca7a1090000000000039", "Tooltip Economia"),
}
ABAS = [("geral", "Visão Geral", "grafico"), ("dev", "Desenvolvidos", "codigo"), ("adq", "Adquiridos", "licenca"),
        ("eco", "Economicidade", "moeda"), ("cen", "Cenários", "alvo"), ("ponte", "Ponte 2025-2026", "linha"),
        ("ope", "Operacional", "lista"), ("ficha", "Ficha", "documento")]
X_ABAS = 292
ABA_W = [round(34 + len(r) * 6.4) for _, r, _ in ABAS]
URL_PROCESSO = "https://www.sigadoc.mt.gov.br/sigaex/app/expediente/doc/exibir?sigla=SEPLAG-PRO-2026/20317-V01"


def L(v):
    return {"expr": {"Literal": {"Value": v}}}


def S(txt):
    return L("'" + str(txt).replace("'", "''") + "'")


PILHA = {"Segoe UI": "'Segoe UI', wf_segoe-ui_normal, helvetica, arial, sans-serif",
         "Segoe UI Semibold": "'Segoe UI Semibold', wf_segoe-ui_semibold, helvetica, arial, sans-serif",
         "Segoe UI Bold": "'Segoe UI Bold', wf_segoe-ui_bold, helvetica, arial, sans-serif"}


def FONTE(n):
    return S(PILHA.get(n, n))


def COR(h):
    return {"solid": {"color": S(h)}}


def campo(ent, prop, medida=False):
    return {("Measure" if medida else "Column"): {"Expression": {"SourceRef": {"Entity": ent}}, "Property": prop}}


def M(p):
    return campo("Medidas", p, True)


def C(ent, prop):
    return campo(ent, prop)


def proj(f, ativo=False, nome=None):
    t = "Measure" if "Measure" in f else "Column"
    ent, prop = f[t]["Expression"]["SourceRef"]["Entity"], f[t]["Property"]
    p = {"field": f, "queryRef": f"{ent}.{prop}", "nativeQueryRef": nome or prop}
    if nome:
        p["displayName"] = nome
    if ativo:
        p["active"] = True
    return p


def ref(f):
    t = "Measure" if "Measure" in f else "Column"
    return f'{f[t]["Expression"]["SourceRef"]["Entity"]}.{f[t]["Property"]}'


def filtro_in(ent, col, valores, nome=None):
    return {"name": nome or tag().replace("-", "")[:20], "field": C(ent, col), "type": "Categorical",
            "filter": {"Version": 2, "From": [{"Name": "x", "Entity": ent, "Type": 0}],
                       "Where": [{"Condition": {"In": {"Expressions": [{"Column": {"Expression": {"SourceRef": {"Source": "x"}}, "Property": col}}],
                                                       "Values": [[{"Literal": {"Value": "'" + v.replace("'", "''") + "'"}}] for v in valores]}}}]}}


SEM_MOLDURA = {"background": [{"properties": {"show": L("false")}}], "title": [{"properties": {"show": L("false")}}],
               "border": [{"properties": {"show": L("false")}}], "dropShadow": [{"properties": {"show": L("false")}}]}


class Pagina:
    def __init__(self, chave, w=1280, h=720, tooltip=False):
        self.id, self.nome = PAGINAS[chave]
        self.chave, self.w, self.h, self.tooltip = chave, w, h, tooltip
        self.visuais, self.z, self.filtros = [], 1000, []

    def add(self, x, y, w, h, visual, filtros=None, cabecalho=False, dica=None):
        n = f"{self.id[-8:]}{len(self.visuais):012d}"
        vco = json.loads(json.dumps(SEM_MOLDURA))
        if not cabecalho:
            vco["visualHeader"] = [{"properties": {"show": L("false")}}]
        if dica:
            vco["visualTooltip"] = [{"properties": {"show": L("true"), "section": S(PAGINAS[dica][0])}}]
        visual.setdefault("visualContainerObjects", {}).update(vco)
        visual.setdefault("drillFilterOtherVisuals", True)
        c = {"$schema": SCHEMA_VC, "name": n, "position": {"x": x, "y": y, "z": self.z, "height": h, "width": w, "tabOrder": self.z}, "visual": visual}
        if filtros:
            c["filterConfig"] = {"filters": filtros}
        self.visuais.append(c)
        self.z += 1000
        return c

    def texto(self, x, y, w, h, medida, tam=11, cor=TEXTO, fonte="Segoe UI", cor_medida=None):
        """Valor numérico (multiRowCard). Medidas de texto vão em texto_longo, que quebra linha e não usa o estilo de título."""
        cor_ = {"solid": {"color": {"expr": M(cor_medida)}}} if cor_medida else COR(cor)
        return self.add(x, y, w, h, {"visualType": "multiRowCard", "query": {"queryState": {"Values": {"projections": [proj(M(medida))]}}},
                                     "objects": {"dataLabels": [{"properties": {"fontSize": L(f"{tam}D"), "color": cor_, "fontFamily": FONTE(fonte)}}],
                                                 "categoryLabels": [{"properties": {"show": L("false")}}],
                                                 "card": [{"properties": {"barShow": L("false"), "outlineStyle": L("0D")}}]}})

    def valor(self, x, y, w, h, medida, tam=18, cor=AZUL_ESC, cor_medida=None):
        return self.texto(x, y, w, h, medida, tam, cor, "Segoe UI Bold", cor_medida)

    def contexto(self, x, y, w, h, medida, cor_medida=None, cor=APOIO, tam=9.5):
        return self.texto(x, y, w, h, medida, tam, cor, "Segoe UI Semibold", cor_medida)

    def texto_longo(self, x, y, w, h, medida, tam=10, cor=TEXTO, fundo=CARD, negrito=False):
        f = M(medida)
        o = {"columnHeaders": [{"properties": {"fontSize": L("1D"), "fontColor": COR(fundo), "backColor": COR(fundo), "wordWrap": L("false")}}],
             "values": [{"properties": {"fontColorPrimary": COR(cor), "backColorPrimary": COR(fundo), "fontColorSecondary": COR(cor),
                                        "backColorSecondary": COR(fundo), "fontSize": L(f"{tam}D"), "wordWrap": L("true"),
                                        "fontFamily": FONTE("Segoe UI Bold" if negrito else "Segoe UI")}}],
             "grid": [{"properties": {"gridVertical": L("false"), "gridHorizontal": L("false"), "outlineColor": COR(fundo), "rowPadding": L("0D")}}],
             "columnWidth": [{"properties": {"value": L(f"{w - 26}D")}, "selector": {"metadata": ref(f)}}],
             "total": [{"properties": {"totals": L("false")}}]}
        return self.add(x, y, w, h, {"visualType": "tableEx", "query": {"queryState": {"Values": {"projections": [proj(f, nome=" ")]}}}, "objects": o})

    def link_web(self, x, y, w, h, url, dica):
        return self.add(x, y, w, h, {
            "visualType": "actionButton",
            "objects": {"icon": [{"properties": {"shapeType": S("blank")}, "selector": {"id": "default"}}, {"properties": {"show": L("false")}}],
                        "outline": [{"properties": {"show": L("false")}}], "fill": [{"properties": {"show": L("false")}}]},
            "visualContainerObjects": {"visualLink": [{"properties": {"show": L("true"), "type": S("WebUrl"), "webUrl": S(url), "tooltip": S(dica)}}]}})

    def cascata(self, x, y, w, h, categoria, medida):
        o = self._eixos(True)
        o["valueAxis"][0]["properties"]["labelDisplayUnits"] = L("1000000D")
        o["labels"] = [{"properties": {"show": L("true"), "color": COR(TEXTO), "fontSize": L("8.5D"), "labelDisplayUnits": L("1000000D"), "labelPrecision": L("2L")}}]
        o["sentimentColors"] = [{"properties": {"increaseFill": COR(AZUL), "decreaseFill": COR(LAR), "totalFill": COR(AZUL_ESC)}}]
        o["legend"] = [{"properties": {"show": L("false")}}]
        return self.add(x, y, w, h, {"visualType": "waterfallChart",
                                     "query": {"queryState": {"Category": {"projections": [proj(categoria, True)]}, "Y": {"projections": [proj(medida)]}},
                                               "sortDefinition": {"sort": [{"field": categoria, "direction": "Ascending"}]}},
                                     "objects": o}, cabecalho=True)

    def link(self, x, y, w, h, destino, dica=""):
        return self.add(x, y, w, h, {
            "visualType": "actionButton",
            "objects": {"icon": [{"properties": {"shapeType": S("blank")}, "selector": {"id": "default"}}, {"properties": {"show": L("false")}}],
                        "outline": [{"properties": {"show": L("false")}}], "fill": [{"properties": {"show": L("false")}}]},
            "visualContainerObjects": {"visualLink": [{"properties": {"show": L("true"), "type": S("PageNavigation"),
                                                                       "navigationSection": S(PAGINAS[destino][0]), "tooltip": S(dica or PAGINAS[destino][1])}}]}})

    def slicer(self, x, y, w, h, ent, col, modo="Dropdown", unico=False):
        return self.add(x, y, w, h, {
            "visualType": "slicer", "query": {"queryState": {"Values": {"projections": [proj(C(ent, col), True)]}}},
            "objects": {"data": [{"properties": {"mode": S(modo)}}],
                        "selection": [{"properties": {"selectAllCheckboxEnabled": L("false" if unico else "true"), "singleSelect": L("true" if unico else "false")}}],
                        "header": [{"properties": {"show": L("false")}}],
                        "items": [{"properties": {"textSize": L("10D"), "fontColor": COR(TEXTO), "background": COR(CARD),
                                                  "outlineColor": COR(LINHA), "outlineStyle": L("1D")}}]}})

    def _eixos(self, rot_y=True, tam=8):
        return {"categoryAxis": [{"properties": {"showAxisTitle": L("false"), "labelColor": COR(APOIO), "fontSize": L(f"{tam}D")}}],
                "valueAxis": [{"properties": {"showAxisTitle": L("false"), "labelColor": COR(SUAVE), "fontSize": L(f"{tam}D"), "show": L("true" if rot_y else "false"),
                                              "gridlineShow": L("true" if rot_y else "false"), "gridlineColor": COR(LINHA)}}]}

    def grafico(self, tipo, x, y, w, h, categoria, medidas, serie=None, cor_unica=None, ordenar=None, desc=True, rotulos=False,
                legenda=True, dica=None, filtros=None, unidades="1000000D", rot_y=True, cores=None, precisao="1L"):
        qs = {"Category": {"projections": [proj(categoria, True)]}, "Y": {"projections": [proj(m) for m in medidas]}}
        if serie:
            qs["Series"] = {"projections": [proj(serie)]}
        alvo = ordenar or categoria
        o = self._eixos(rot_y)
        o["legend"] = [{"properties": {"show": L("true" if (serie or len(medidas) > 1) and legenda else "false"), "position": S("Top"),
                                       "labelColor": COR(APOIO), "fontSize": L("8D"), "showTitle": L("false")}}]
        o["labels"] = [{"properties": {"show": L("true" if rotulos else "false"), "color": COR(TEXTO), "fontSize": L("8D"),
                                       "labelDisplayUnits": L(unidades), "labelPrecision": L(precisao)}}]
        o["valueAxis"][0]["properties"]["labelDisplayUnits"] = L(unidades)
        if cores:
            o["dataPoint"] = [{"properties": {"fill": COR(c)}, "selector": {"metadata": ref(m)}} for m, c in zip(medidas, cores)]
        if cor_unica:
            o["dataPoint"] = [{"properties": {"fill": COR(cor_unica)}}]
        v = {"visualType": tipo, "query": {"queryState": qs, "sortDefinition": {"sort": [{"field": alvo, "direction": "Descending" if (ordenar and desc) else "Ascending"}]}},
             "objects": o}
        return self.add(x, y, w, h, v, filtros=filtros, cabecalho=True, dica=dica)

    def barras(self, x, y, w, h, categoria, medida, cor=AZUL, cor_medida=None, dica=None, filtros=None, unidades="1000000D", precisao="2L", margem=None):
        o = self._eixos(False, 9)
        o["categoryAxis"][0]["properties"]["labelColor"] = COR(TEXTO)
        if margem:
            o["categoryAxis"][0]["properties"]["maxMarginFactor"] = L(f"{margem}L")
        o["legend"] = [{"properties": {"show": L("false")}}]
        o["labels"] = [{"properties": {"show": L("true"), "color": COR(TEXTO), "fontSize": L("8.5D"), "labelPosition": S("OutsideEnd"),
                                       "labelDisplayUnits": L(unidades), "labelPrecision": L(precisao), "fontFamily": FONTE("Segoe UI Semibold")}}]
        o["dataPoint"] = [{"properties": {"fill": {"solid": {"color": {"expr": M(cor_medida)}}} if cor_medida else COR(cor)},
                           **({"selector": {"data": [{"dataViewWildcard": {"matchingOption": 1}}]}} if cor_medida else {})}]
        return self.add(x, y, w, h, {"visualType": "clusteredBarChart",
                                     "query": {"queryState": {"Category": {"projections": [proj(categoria, True)]}, "Y": {"projections": [proj(medida)]}},
                                               "sortDefinition": {"sort": [{"field": medida, "direction": "Descending"}]}},
                                     "objects": o}, filtros=filtros, cabecalho=True, dica=dica)

    def combo(self, x, y, w, h, categoria, colunas, linhas, ordenar=None, desc=True, dica=None, rotulos=True, unidades="0D", secundario=False,
              unid_y="1000000D", unid_y2="1D"):
        o = self._eixos(True)
        o["legend"] = [{"properties": {"show": L("true"), "position": S("Top"), "labelColor": COR(APOIO), "fontSize": L("8D"), "showTitle": L("false")}}]
        o["labels"] = [{"properties": {"show": L("true" if rotulos else "false"), "color": COR(TEXTO), "fontSize": L("8D"),
                                       "labelDisplayUnits": L(unidades), "labelPrecision": L("0L")}}]
        o["lineStyles"] = [{"properties": {"strokeWidth": L("3D"), "showMarker": L("true")}}]
        o["valueAxis"][0]["properties"]["labelDisplayUnits"] = L(unid_y)
        o["valueAxis"][0]["properties"]["secLabelDisplayUnits"] = L(unid_y2)
        if not secundario:
            o["valueAxis"][0]["properties"]["secShow"] = L("false")
            o["valueAxis"][0]["properties"]["alignZeros"] = L("true")
        cores = [AZUL, LAR, AZUL_ESC, "#6FA0B3"]
        o["dataPoint"] = [{"properties": {"fill": COR(cores[i])}, "selector": {"metadata": ref(m)}} for i, m in enumerate(colunas + linhas)]
        alvo = ordenar or categoria
        return self.add(x, y, w, h, {"visualType": "lineClusteredColumnComboChart",
                                     "query": {"queryState": {"Category": {"projections": [proj(categoria, True)]}, "Y": {"projections": [proj(m) for m in colunas]},
                                                              "Y2": {"projections": [proj(m) for m in linhas]}},
                                               "sortDefinition": {"sort": [{"field": alvo, "direction": "Descending" if (ordenar and desc) else "Ascending"}]}},
                                     "objects": o}, cabecalho=True, dica=dica)

    def rosca(self, x, y, w, h, categoria, medida, dica=None):
        return self.add(x, y, w, h, {"visualType": "donutChart",
                                     "query": {"queryState": {"Category": {"projections": [proj(categoria, True)]}, "Y": {"projections": [proj(medida)]}}},
                                     "objects": {"legend": [{"properties": {"show": L("false")}}],
                                                 "labels": [{"properties": {"labelStyle": S("Category, percent of total"), "color": COR(TEXTO), "fontSize": L("8.5D"),
                                                                            "percentageLabelPrecision": L("1L")}}],
                                                 "slices": [{"properties": {"innerRadiusRatio": L("62L")}}]}}, cabecalho=True, dica=dica)

    def tabela(self, x, y, w, h, colunas, nomes=None, ordenar=None, desc=True, cor_por=None, filtros=None, dica=None, barras=None, tam=9):
        estilo = {"columnHeaders": [{"properties": {"fontColor": COR(AZUL_ESC), "backColor": COR(AZUL_CL), "fontSize": L(f"{tam}D"),
                                                    "fontFamily": FONTE("Segoe UI Semibold"), "wordWrap": L("true")}}],
                  "values": [{"properties": {"fontColorPrimary": COR(TEXTO), "backColorPrimary": COR(CARD), "fontColorSecondary": COR(TEXTO),
                                             "backColorSecondary": COR("#F1F6F5"), "fontSize": L(f"{tam}D"), "wordWrap": L("true")}}],
                  "grid": [{"properties": {"gridVertical": L("false"), "gridHorizontal": L("true"), "gridHorizontalColor": COR(LINHA),
                                           "outlineColor": COR(LINHA), "rowPadding": L("3D")}}],
                  "total": [{"properties": {"totals": L("false")}}]}
        for alvo, med in (cor_por or []):
            estilo["values"].append({"properties": {"fontColor": {"solid": {"color": {"expr": M(med)}}}},
                                     "selector": {"data": [{"dataViewWildcard": {"matchingOption": 1}}], "metadata": ref(alvo)}})
        if barras:
            estilo["columnFormatting"] = [{"properties": {"dataBars": {"positiveColor": COR("#9FC4D2"), "negativeColor": COR(LAR), "axisColor": COR(LINHA),
                                                                       "reverseDirection": L("false"), "hideText": L("false")}}, "selector": {"metadata": ref(barras)}}]
        nomes = nomes or {}
        v = {"visualType": "tableEx", "query": {"queryState": {"Values": {"projections": [proj(c, nome=nomes.get(i)) for i, c in enumerate(colunas)]}}},
             "objects": estilo}
        if ordenar:
            v["query"]["sortDefinition"] = {"sort": [{"field": ordenar, "direction": "Descending" if desc else "Ascending"}]}
        return self.add(x, y, w, h, v, filtros=filtros, cabecalho=True, dica=dica)

    def grava(self, svg):
        pasta = DEF / "pages" / self.id
        (pasta / "visuals").mkdir(parents=True)
        arq = f"pg_{self.chave}.svg"
        gravar(RES / arq, svg)
        page = {"$schema": SCHEMA_PG, "name": self.id, "displayName": self.nome, "displayOption": "FitToPage", "height": self.h, "width": self.w,
                "objects": {"background": [{"properties": {"image": {"image": {"name": S(arq), "url": {"expr": {"ResourcePackageItem": {
                    "PackageName": "RegisteredResources", "PackageType": 1, "ItemName": arq}}}, "scaling": S("Fit")}}, "transparency": L("0D")}}],
                    "outspace": [{"properties": {"color": COR(AZUL_ESC if self.chave == "capa" else PORC)}}]}}
        if self.tooltip:
            page["type"] = "Tooltip"
            page["visibility"] = "HiddenInViewMode"
        if self.filtros:
            page["filterConfig"] = {"filters": self.filtros}
        gravar(pasta / "page.json", json.dumps(page, ensure_ascii=False, indent=2))
        for v in self.visuais:
            gravar(pasta / "visuals" / v["name"] / "visual.json", json.dumps(v, ensure_ascii=False, indent=2))
        return arq


# ---------------------------------------------------------------- SVG
FONTE_SVG = "font-family:'Segoe UI',Arial,sans-serif"
LOGO = (ASSETS / "logo_seplag_site_branca.png").read_bytes()
LOGO_B64, LOGO_W, LOGO_H = base64.b64encode(LOGO).decode(), *Image.open(io.BytesIO(LOGO)).size


def esc(t):
    return str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def txt(x, y, t, tam=12, cor=TEXTO, peso=400, extra=""):
    return f'<text x="{x}" y="{y}" style="{FONTE_SVG};font-size:{tam}px;font-weight:{peso};fill:{cor}" {extra}>{esc(t)}</text>'


def ret(x, y, w, h, fill=CARD, r=12, stroke=LINHA, sw=1, extra=""):
    st = f'stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" {st} {extra}/>'


def logo(x, y, alt):
    return f'<image x="{x}" y="{y}" width="{alt * LOGO_W / LOGO_H:.1f}" height="{alt}" href="data:image/png;base64,{LOGO_B64}"/>'


ICONES = {
    "moeda": '<circle cx="8" cy="8" r="7"/><path d="M10.5 5.5H7a1.5 1.5 0 0 0 0 3h2a1.5 1.5 0 0 1 0 3H5.5M8 3.5v9"/>',
    "codigo": '<path d="M5 4 1 8l4 4M11 4l4 4-4 4M9.5 2.5l-3 11"/>',
    "licenca": '<rect x="1.5" y="3" width="13" height="10" rx="1.5"/><circle cx="5.5" cy="8" r="1.8"/><path d="M9 6.5h3.5M9 9.5h3.5"/>',
    "grafico": '<path d="M2 14h12M4 11V7M8 11V3M12 11V9"/>',
    "pizza": '<path d="M8 1v7h7a7 7 0 1 1-7-7z"/><path d="M10 1.3A7 7 0 0 1 14.7 6H10z"/>',
    "linha": '<path d="M1 13l4-5 3 3 6-8"/><path d="M1 15h14"/>',
    "lista": '<path d="M5 3h10M5 8h10M5 13h10M1.5 3h.01M1.5 8h.01M1.5 13h.01"/>',
    "documento": '<path d="M3 1h7l3 3v11H3z"/><path d="M10 1v3h3M5.5 8h5M5.5 11h5"/>',
    "camadas": '<path d="M8 1 1 5l7 4 7-4zM1 8.5l7 4 7-4M1 12l7 4 7-4"/>',
    "regua": '<path d="M2 11 11 2l3 3-9 9z"/><path d="M5 8l1.5 1.5M7 6l1.5 1.5M9 4l1.5 1.5"/>',
    "alvo": '<circle cx="8" cy="8" r="7"/><circle cx="8" cy="8" r="4"/><circle cx="8" cy="8" r="1"/>',
    "trofeu": '<path d="M4 2h8v4a4 4 0 0 1-8 0zM4 4H1.5a2.5 2.5 0 0 0 2.5 3M12 4h2.5A2.5 2.5 0 0 1 12 7M8 10v3M5 15h6"/>',
    "alerta": '<path d="M8 1.5 15 14H1z"/><path d="M8 6v4M8 12h.01"/>',
    "escudo": '<path d="M8 1 2 3.5v4C2 11 4.5 13.8 8 15c3.5-1.2 6-4 6-7.5v-4z"/><path d="m5.5 8 2 2 3-3.5"/>',
    "lupa": '<circle cx="7" cy="7" r="5"/><path d="m11 11 4 4"/>',
    "casa": '<path d="M1.5 7.5 8 2l6.5 5.5M3.5 6v8h9V6"/>',
    "seta": '<path d="M2 8h12M9 3l5 5-5 5"/>',
    "calendario": '<rect x="1.5" y="2.5" width="13" height="12" rx="2"/><path d="M1.5 6.5h13M5 1v3M11 1v3"/>',
    "engrenagem": '<circle cx="8" cy="8" r="2.5"/><path d="M8 1v2M8 13v2M1 8h2M13 8h2M3 3l1.5 1.5M11.5 11.5 13 13M3 13l1.5-1.5M11.5 4.5 13 3"/>',
    "conexao": '<circle cx="3" cy="8" r="2"/><circle cx="13" cy="3.5" r="2"/><circle cx="13" cy="12.5" r="2"/><path d="M5 7l6-3M5 9l6 3"/>',
    "cubo": '<path d="M8 1 14.5 4.5v7L8 15 1.5 11.5v-7z"/><path d="M1.5 4.5 8 8l6.5-3.5M8 8v7"/>',
    "porquinho": '<path d="M2.5 8.5a5 4 0 0 1 9.5-1.8H14v3l-1.5.8-.8 2H9.5v-1h-3v1H4.3l-.8-2.2A3.5 3.5 0 0 1 2.5 8.5z"/><path d="M10.5 7h.01"/>',
}


def icone(nome, x, y, cor=AZUL, e=1.0):
    return (f'<g transform="translate({x},{y}) scale({e})" fill="none" stroke="{cor}" stroke-width="1.8" stroke-linecap="round" '
            f'stroke-linejoin="round">{ICONES[nome]}</g>')


def svg_doc(conteudo, fundo=PORC, w=1280, h=720, defs=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}"><defs>{defs}'
            f'<filter id="sombra" x="-5%" y="-5%" width="110%" height="120%"><feDropShadow dx="0" dy="2" stdDeviation="3" flood-color="#0E3A4D" flood-opacity="0.08"/></filter>'
            f'</defs><rect width="{w}" height="{h}" fill="{fundo}"/>{conteudo}</svg>')


def cabecalho(ativa):
    s = f'<rect x="0" y="0" width="1280" height="56" fill="{AZUL}"/>'
    s += icone("cubo", 18, 20, LAR, 1.05)
    s += txt(42, 24, "INVENTÁRIO DE BENS INTANGÍVEIS 2026", 8, "#BFDCE6", 700, 'letter-spacing="1.2"')
    s += txt(42, 42, "Catálogo de Produtos de Software", 14, "#FFFFFF", 700)
    x = X_ABAS
    for (chave, rot, ic), w in zip(ABAS, ABA_W):
        on = chave == ativa
        if on:
            s += ret(x - 2, 12, w - 4, 32, "#FFFFFF", 16, None, extra='fill-opacity="0.16"')
        s += icone(ic, x + 8, 20, LAR if on else "#BFDCE6", 0.9)
        s += txt(x + 28, 33, rot, 11.5, "#FFFFFF" if on else "#E3F0F4", 700 if on else 400)
        if on:
            s += f'<rect x="{x + 8}" y="51" width="{w - 20}" height="5" rx="2.5" fill="{LAR}"/>'
        x += w
    s += logo(1272 - 40 * LOGO_W / LOGO_H, 8, 40)
    return s


def barra_filtros(campos, nota="Fonte: laudos, relatórios e 3ª Nota Técnica · inventário 2026"):
    s = f'<rect x="0" y="56" width="1280" height="44" fill="{CARD}"/><line x1="0" y1="100" x2="1280" y2="100" stroke="{LINHA}"/>'
    for ic, rot, x in campos:
        s += icone(ic, x, 70, AZUL, 0.9) + txt(x + 20, 83, rot, 11, APOIO)
    s += txt(1260, 83, nota, 9.5, SUAVE, 400, 'text-anchor="end"')
    return s


def leitura():
    return ret(20, 110, 122, 24, LAR, 6, None) + txt(30, 126, "LEITURA RÁPIDA", 10, "#FFFFFF", 800, 'letter-spacing="1"')


def kpi_heroi(x, y, w, h, rot, ic):
    return ret(x, y, w, h, AZUL, 14, None, extra='filter="url(#sombra)"') + icone(ic, x + 16, y + 14, LAR, 1.0) + txt(x + 40, y + 27, rot, 12, "#D9EAF0", 600)


def kpi(x, y, w, h, rot, ic, alerta=False):
    s = ret(x, y, w, h, CARD, 14, LINHA, 1, 'filter="url(#sombra)"')
    if alerta:
        s += f'<rect x="{x}" y="{y + 14}" width="4" height="{h - 28}" rx="2" fill="{LAR}"/>'
    return s + icone(ic, x + 16, y + 14, LAR if alerta else AZUL, 1.0) + txt(x + 40, y + 27, rot, 11.5, APOIO, 600)


def cartao(x, y, w, h, titulo, ic, dica=""):
    s = ret(x, y, w, h, CARD, 14, LINHA, 1, 'filter="url(#sombra)"') + icone(ic, x + 16, y + 15, AZUL, 1.0) + txt(x + 40, y + 28, titulo, 13.5, TEXTO, 700)
    if dica:
        s += txt(x + 52 + len(titulo) * 8.3, y + 28, dica, 10.5, SUAVE)
    return s


def navegacao(p):
    x = X_ABAS
    for (chave, rot, _), w in zip(ABAS, ABA_W):
        p.link(x - 2, 10, w - 4, 40, chave, rot)
        x += w
    p.link(10, 8, 280, 42, "capa", "Voltar à capa")


F_INV = C("dInventario", "Inventário")
F_SIGLA = C("dProduto", "Sigla")
F_NOME = C("dProduto", "Nome do Produto")
F_CAT = C("dProduto", "Categoria")
F_SIT = C("dProduto", "Situação Resumida")
DEV, LIC_, SEAP_ = "Desenvolvido internamente", "Adquirido: licença", "Adquirido: contrato (SEAP)"


def gera_relatorio():
    paginas, svgs = [], {}

    def kpi_padrao(p, s, x, y, w, rot, ic, med, ctx, cor_ctx=None, alerta=False, ctx_fixo=None, h=96):
        s += kpi(x, y, w, h, rot, ic, alerta)
        p.valor(x + 12, y + 32, w - 20, 40, med, 17, LAR if alerta else AZUL_ESC)
        if ctx:
            p.contexto(x + 12, y + 68, w - 20, 24, ctx, cor_ctx, LAR if (alerta and not cor_ctx) else APOIO)
        if ctx_fixo:
            s += txt(x + 16, y + h - 12, ctx_fixo, 9.5, APOIO, 600)
        return s

    def heroi(p, s, rot, ic, med, ctx, cor_ctx="Cor Var Valor (escuro)"):
        s += kpi_heroi(20, 146, 300, 96, rot, ic)
        p.valor(32, 172, 284, 46, med, 21, "#FFFFFF")
        if ctx:
            p.contexto(32, 214, 284, 24, ctx, cor_ctx, CINZA_CL if cor_ctx is None else APOIO, 10)
        return s

    # ===== CAPA =====
    capa = Pagina("capa")
    foto = Image.open(ASSETS / "capa_foto_equipe.jpg").convert("RGB")
    esc_ = max(1280 / foto.width, 720 / foto.height)
    foto = foto.resize((round(foto.width * esc_), round(foto.height * esc_)), Image.LANCZOS)
    l, t = (foto.width - 1280) // 2, (foto.height - 720) // 2
    foto = foto.crop((l, t, l + 1280, t + 720)).filter(ImageFilter.GaussianBlur(1.6))
    b = io.BytesIO()
    foto.save(b, "JPEG", quality=85)
    FOTO = base64.b64encode(b.getvalue()).decode()
    defs = (f'<linearGradient id="deg" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{AZUL_ESC}" stop-opacity="0.97"/>'
            f'<stop offset="0.48" stop-color="{AZUL}" stop-opacity="0.86"/><stop offset="1" stop-color="{AZUL}" stop-opacity="0.18"/></linearGradient>'
            f'<linearGradient id="base" x1="0" y1="0" x2="0" y2="1"><stop offset="0.55" stop-color="{AZUL_ESC}" stop-opacity="0"/>'
            f'<stop offset="1" stop-color="{AZUL_ESC}" stop-opacity="0.9"/></linearGradient>')
    s = f'<image x="0" y="0" width="1280" height="720" preserveAspectRatio="xMidYMid slice" href="data:image/jpeg;base64,{FOTO}"/>'
    s += '<rect width="1280" height="720" fill="url(#deg)"/><rect width="1280" height="720" fill="url(#base)"/>'
    s += logo(64, 36, 60)
    s += ret(64, 120, 300, 28, LAR, 14, None, extra='fill-opacity="0.18"') + txt(80, 139, "CIABI · PORTARIA Nº 124/2026/SEPLAG", 11, LAR, 700, 'letter-spacing="1.6"')
    s += icone("documento", 66, 158, "#FFFFFF", 0.95) + txt(88, 171, "Processo SEPLAG-PRO-2026/20317-V01 (Sigadoc) ↗", 12.5, "#FFFFFF", 600, 'text-decoration="underline"')
    s += txt(62, 238, "Catálogo de Produtos", 54, "#FFFFFF", 800)
    s += f'<text x="62" y="296" style="{FONTE_SVG};font-size:54px;font-weight:800;fill:{LAR}">de Software</text>'
    s += txt(64, 334, "O ativo que ninguém vê: o que a SEPLAG construiu, adquiriu e mantém, quanto vale,", 16.5, "#FFFFFF")
    s += txt(64, 357, "quanto custou e o que falta para que cada valor tenha lastro. Inventário de Bens Intangíveis 2026.", 16.5, "#FFFFFF")
    s += ret(64, 380, 212, 50, LAR, 25, None) + txt(92, 411, "Iniciar análises", 16, "#FFFFFF", 700) + icone("seta", 240, 398, "#FFFFFF", 1.05)
    s += icone("documento", 300, 397, "#E3F0F4", 1.0) + txt(322, 403, "Fonte: 41 Laudos Técnicos de Avaliação, relatórios sintéticos e analíticos,", 11.5, "#E3F0F4")
    s += txt(322, 420, "Relatório Resumido do Valor Apurado e 3ª Nota Técnica Consultiva", 11.5, "#E3F0F4")
    ACH = [("cubo", "Valor Atual (R$)", "% Variação Valor", "Cor Var Valor (escuro)", "valor total dos 58 bens intangíveis", "geral", 19),
           ("codigo", "Qtde Desenvolvidos", "Valor Atual (contexto)", None, "softwares desenvolvidos internamente", "dev", 26),
           ("porquinho", "% Economia", "Economia vs Mercado (R$)", None, "economia vs preço de mercado do PF (R$)", "eco", 26),
           ("alerta", "Qtde Sem Documentação", "Valor Sem Documentação (R$)", None, "sistemas sem documentação funcional (R$)", "ope", 26)]
    for i, (ic, med, med2, cor2, rot, destino, tam) in enumerate(ACH):
        x, y, w, h = 64 + i * 292, 462, 280, 168
        s += ret(x, y, w, h, AZUL_ESC, 16, "#FFFFFF", 1, 'fill-opacity="0.72" stroke-opacity="0.25"')
        s += ret(x + 16, y + 16, 36, 36, LAR, 10, None, extra='fill-opacity="0.22"') + icone(ic, x + 26, y + 26, LAR, 1.0)
        s += txt(x + 18, y + 126, rot, 11.5, "#FFFFFF")
        s += txt(x + 18, y + 152, PAGINAS[destino][1] + " →", 11, LAR, 700)
        capa.valor(x + 60, y + 12, w - 66, 46, med, tam, "#FFFFFF")
        capa.contexto(x + 14, y + 66, w - 24, 30, med2, cor2, "#FFFFFF", 11.5)
        capa.link(x, y, w, h, destino, f"Abrir {PAGINAS[destino][1]}")
    s += txt(1216, 690, "CIABI/SEPLAG-MT", 10, "#CFE3EA", 600, 'text-anchor="end"')
    capa.link(64, 380, 212, 50, "geral", "Iniciar análises")
    capa.link_web(62, 154, 390, 24, URL_PROCESSO, "Abrir o processo SEPLAG-PRO-2026/20317-V01 no Sigadoc")
    svgs["capa"] = svg_doc(s, AZUL_ESC, defs=defs)
    paginas.append(capa)

    # ===== VISÃO GERAL =====
    p = Pagina("geral")
    s = cabecalho("geral") + barra_filtros([("calendario", "Inventário", 20), ("camadas", "Categoria", 238)]) + leitura()
    s = heroi(p, s, "Valor apurado no inventário", "cubo", "Valor Atual (R$)", "% Variação Valor")
    KP = [("Produtos avaliados", "camadas", "Qtde Produtos Atual", "Var Qtde Produtos", "Cor Var Qtde"),
          ("Tamanho funcional (PF)", "regua", "PF Atual", "% Variação PF", "Cor Var PF"),
          ("Desenvolvidos internamente", "codigo", "Valor Desenvolvidos (R$)", "% Var Desenvolvidos", "Cor Var Desenvolvidos"),
          ("Adquiridos (licenças e SEAP)", "licenca", "Valor Adquiridos (R$)", "% Var Adquiridos", "Cor Var Adquiridos")]
    for i, (rot, ic, med, ctx, cor) in enumerate(KP):
        s = kpi_padrao(p, s, 332 + i * 232, 146, 220, rot, ic, med, ctx, cor)
    s += cartao(20, 254, 610, 222, "Evolução do valor por inventário", "linha", "R$ milhões, por categoria")
    s += cartao(642, 254, 290, 222, "Composição", "pizza", "por categoria")
    s += cartao(944, 254, 316, 456, "Governança do catálogo", "escudo", "3ª Nota Técnica")
    s += cartao(20, 488, 912, 222, "Produtos por valor", "trofeu")
    FX = ["até 100 mil", "100-300 mil", "300-600 mil", "600-900 mil", "0,9-1,2 mi", "1,2-2,2 mi", "2,2-5,2 mi", "5,2-10 mi", "acima de 10 mi"]
    CORES_FX = ["#CFE3EA", "#B4D3DE", "#98C2D1", "#7BAFC2", "#5F9BB2", "#4787A1", "#33748F", "#22617D", "#0E3A4D"]
    for i, (rot, cor) in enumerate(zip(FX, CORES_FX)):
        xx = 222 + i * 78
        s += f'<rect x="{xx}" y="507" width="10" height="10" rx="2" fill="{cor}"/>' + txt(xx + 14, 516, rot, 8.5, APOIO)
    GOV = [("Sem documentação funcional", "alerta", "Qtde Sem Documentação", "% Sistemas Sem Documentação"),
           ("Sem uso ou suspensos", "alerta", "Qtde Sem Uso ou Suspensos", "% Valor Sem Uso"),
           ("Em desenvolvimento (art. 9º)", "engrenagem", "Qtde Em Desenvolvimento", "Valor Em Desenvolvimento (R$)"),
           ("Licenças com cessão encerrada", "licenca", "Qtde Licenças Encerradas", "% Licenças Encerradas"),
           ("Diligências aplicáveis (de 19)", "lupa", "Qtde Diligências", "Prioritárias (contexto)")]
    for i, (rot, ic, med, med2) in enumerate(GOV):
        y = 296 + i * 80
        s += ret(958, y, 288, 70, "#F1F6F5", 10, None) + icone(ic, 970, y + 12, LAR if ic == "alerta" else AZUL, 0.95) + txt(992, y + 24, rot, 11.5, APOIO, 600)
        p.valor(968, y + 30, 62, 36, med, 17, LAR if ic == "alerta" else AZUL_ESC)
        p.contexto(1032, y + 36, 210, 28, med2, None, TEXTO, 10)
    svgs["geral"] = svg_doc(s)
    p.slicer(110, 62, 110, 32, "dInventario", "Inventário", unico=True)
    p.slicer(320, 62, 250, 32, "dProduto", "Categoria")
    navegacao(p)
    p.texto_longo(150, 103, 1112, 42, "Leitura Visão Geral", 10, TEXTO, PORC, True)
    p.grafico("columnChart", 30, 290, 590, 180, F_INV, [M("Valor Final (R$)")], serie=F_CAT, rotulos=True, precisao="2L")
    p.rosca(652, 288, 270, 182, F_CAT, M("Valor Atual (R$)"))
    p.barras(30, 524, 892, 180, F_SIGLA, M("Valor Atual (R$)"), cor_medida="Cor Faixa Valor", dica="tt_prod", unidades="1D", precisao="2L")
    paginas.append(p)

    # ===== DESENVOLVIDOS =====
    p = Pagina("dev")
    p.filtros = [filtro_in("dProduto", "Categoria", [DEV], "filtroCategoriaDev")]
    s = cabecalho("dev") + barra_filtros([("calendario", "Inventário", 20), ("engrenagem", "Situação", 238), ("codigo", "Tecnologia", 520), ("trofeu", "Valor Institucional", 750)]) + leitura()
    s = heroi(p, s, "Valor dos desenvolvidos", "codigo", "Valor Atual (R$)", "% Variação Valor")
    KP = [("Sistemas", "camadas", "Qtde Produtos Atual", "Var Qtde Produtos", "Cor Var Qtde", False),
          ("Pontos de função", "regua", "PF Atual", "% Variação PF", "Cor Var PF", False),
          ("Variação de PF", "linha", "Variação PF", "% Variação PF", "Cor Var PF", False),
          ("Sem documentação", "alerta", "Qtde Sem Documentação", "% Sistemas Sem Documentação", None, True),
          ("Sem uso ou suspensos", "alerta", "Qtde Sem Uso ou Suspensos", "% Valor Sem Uso", None, True)]
    for i, (rot, ic, med, ctx, cor, al) in enumerate(KP):
        s = kpi_padrao(p, s, 332 + i * 186, 146, 176, rot, ic, med, ctx, cor, al)
    s += cartao(20, 254, 790, 456, "Ranking dos sistemas", "trofeu", "💎 🥇 🥈 🥉 os quatro maiores · situação em laranja indica ressalva")
    s += cartao(822, 254, 438, 222, "Valor e tamanho por inventário", "linha", "colunas: R$ milhões · linha: PF")
    s += cartao(822, 488, 438, 222, "Valor por tecnologia", "codigo", "R$ milhões")
    svgs["dev"] = svg_doc(s)
    p.slicer(110, 62, 110, 32, "dInventario", "Inventário", unico=True)
    p.slicer(318, 62, 190, 32, "dProduto", "Situação Resumida")
    p.slicer(604, 62, 130, 32, "dProduto", "Tecnologia")
    p.slicer(888, 62, 150, 32, "dProduto", "Faixa Valor Institucional")
    navegacao(p)
    p.texto_longo(150, 103, 1112, 42, "Leitura Desenvolvidos", 10, TEXTO, PORC, True)
    p.tabela(30, 290, 770, 412, [M("Posição"), F_SIGLA, F_SIT, C("dProduto", "Tecnologia"), C("dProduto", "Nível de Medição"),
                                 M("PF Atual"), M("VI Atual"), M("Valor Atual (R$)"), M("Var % (tabela)"), C("dProduto", "Documentação")],
             nomes={0: "Posição", 1: "Sistema", 2: "Situação", 3: "Tecnologia", 4: "Nível", 5: "PF", 6: "VI", 7: "Valor 2026", 8: "Variação", 9: "Documentação"},
             ordenar=M("Valor Atual (R$)"), cor_por=[(F_SIT, "Cor Situação"), (C("dProduto", "Documentação"), "Cor Documentação"), (M("Var % (tabela)"), "Cor Var Valor")],
             dica="tt_prod")
    p.combo(832, 290, 418, 180, F_INV, [M("Valor Final (R$)")], [M("Tamanho Funcional (PF)")], rotulos=False, secundario=True)
    p.barras(832, 524, 418, 180, C("dProduto", "Tecnologia"), M("Valor Atual (R$)"))
    paginas.append(p)

    # ===== ADQUIRIDOS =====
    p = Pagina("adq")
    p.filtros = [filtro_in("dProduto", "Categoria", [LIC_, SEAP_], "filtroCategoriaAdq")]
    s = cabecalho("adq") + barra_filtros([("calendario", "Inventário", 20), ("licenca", "Categoria", 238), ("engrenagem", "Situação", 560)]) + leitura()
    s = heroi(p, s, "Valor dos adquiridos", "licenca", "Valor Atual (R$)", "% Variação Valor")
    KP = [("Licenças e prateleira", "licenca", "Valor Licenças (R$)", "% Var Licenças", "Cor Var Licenças", False),
          ("SEAP (contrato)", "documento", "Valor SEAP (R$)", "% Var SEAP", "Cor Var SEAP", False),
          ("Cessões encerradas", "alerta", "Valor Licenças Encerradas (R$)", "% Licenças Encerradas", None, True),
          ("SEAP líquido em 31/12/2026", "calendario", "Valor Líquido SEAP 31/12 (R$)", "% SEAP Líquido", None, False)]
    for i, (rot, ic, med, ctx, cor, al) in enumerate(KP):
        s = kpi_padrao(p, s, 332 + i * 232, 146, 220, rot, ic, med, ctx, cor, al)
    s += cartao(20, 254, 790, 456, "Licenças, contratos e vigências", "licenca", "valor de aquisição (SIGPAT) · cessões encerradas em laranja")
    s += cartao(822, 254, 438, 222, "Evolução por inventário", "linha", "R$ milhões")
    s += cartao(822, 488, 438, 222, "Amortização do SEAP", "calendario", "R$ milhões ao fim de cada parcela")
    svgs["adq"] = svg_doc(s)
    p.slicer(110, 62, 110, 32, "dInventario", "Inventário", unico=True)
    p.slicer(320, 62, 226, 32, "dProduto", "Categoria")
    p.slicer(640, 62, 230, 32, "dProduto", "Situação Resumida")
    navegacao(p)
    p.texto_longo(150, 103, 1112, 42, "Leitura Adquiridos", 10, TEXTO, PORC, True)
    p.tabela(30, 290, 770, 412, [C("dProduto", "Patrimônio"), F_NOME, C("dProduto", "Fornecedor"), C("dProduto", "Tipo de Licença"),
                                 C("dProduto", "Data de Aquisição"), C("dProduto", "Data Fim"), F_SIT, M("Valor Atual (R$)"), M("Var % (tabela)")],
             nomes={0: "Patrimônio", 1: "Bem", 2: "Fornecedor", 3: "Tipo", 4: "Aquisição", 5: "Fim", 6: "Situação", 7: "Valor 2026", 8: "Variação"},
             ordenar=M("Valor Atual (R$)"), cor_por=[(F_SIT, "Cor Situação"), (M("Var % (tabela)"), "Cor Var Valor")], tam=8.5)
    p.grafico("columnChart", 832, 290, 418, 180, F_INV, [M("Valor Final (R$)")], serie=F_CAT, rotulos=True, precisao="2L")
    p.combo(832, 524, 418, 180, C("fAmortizacaoSEAP", "Fim do Período"), [M("Amortização do Mês (R$)")], [M("Valor Líquido SEAP (R$)")],
            rotulos=False)
    paginas.append(p)

    # ===== ECONOMICIDADE =====
    p = Pagina("eco")
    p.filtros = [filtro_in("dProduto", "Tem Custo de Projeto", ["Sim"], "filtroComCusto")]
    s = cabecalho("eco") + barra_filtros([("codigo", "Sistema", 20)], "Fonte: custo de projeto dos laudos (painel Custos de Projetos, TRDs até 07/2026)") + leitura()
    s = heroi(p, s, "Economia vs preço de mercado", "porquinho", "Economia vs Mercado (R$)", "% Economia (contexto)", None)
    KP = [("Pago à fábrica de software", "moeda", "Custo Pago (R$)", "Sistemas com Custo (contexto)", None),
          ("Serviço a preço de mercado", "alvo", "Custo a Preço de Mercado (R$)", "Mercado sobre Pago", None),
          ("Valor do produto por R$ 1,00", "cubo", "Retorno Produto por R$ 1", None, "VT 2026 para cada R$ 1,00 pago"),
          ("Valor do ativo por R$ 1,00", "trofeu", "Retorno Ativo por R$ 1", None, "VA 2026 para cada R$ 1,00 pago")]
    for i, (rot, ic, med, ctx, fixo) in enumerate(KP):
        s = kpi_padrao(p, s, 332 + i * 232, 146, 220, rot, ic, med, ctx, None, False, fixo)
    s += cartao(20, 254, 620, 236, "Custo pago x mesmo serviço a preço de mercado", "regua", "R$ milhões por sistema")
    s += cartao(652, 254, 608, 236, "Quanto cada R$ 1,00 pago gerou", "trofeu", "valor do produto (VT) e do ativo (VA)")
    s += cartao(20, 502, 820, 208, "Detalhe por sistema", "lista", "custo pago, mercado, economia e retorno")
    s += cartao(852, 502, 408, 208, "Como ler", "documento")
    NOTAS = ["Custo pago: o que a SEPLAG pagou à fábrica do Contrato nº 014/2022",
             "(desenvolvimento, tickets e PFT), segundo os laudos.",
             "Mercado: o mesmo serviço a R$ 1.215,09 por PF (referência 2026) em",
             "vez do preço do contrato no laudo; conservador para pagamentos antigos.",
             "Retorno: VT e VA de 2026 divididos pelo custo pago.",
             "Limite: não inclui a equipe interna da SEPLAG; os 30 sistemas",
             "sem custo registrado ficam fora (ver diligência D15)."]
    for i, l_ in enumerate(NOTAS):
        s += txt(870, 552 + i * 21, l_, 11, TEXTO if i % 2 == 0 else APOIO, 600 if i in (0, 2, 4, 5) else 400)
    svgs["eco"] = svg_doc(s)
    p.slicer(96, 62, 220, 32, "dProduto", "Sigla")
    navegacao(p)
    p.texto_longo(150, 103, 1112, 42, "Leitura Economicidade", 10, TEXTO, PORC, True)
    p.grafico("clusteredColumnChart", 30, 290, 600, 194, F_SIGLA, [M("Custo Pago (R$)"), M("Custo a Preço de Mercado (R$)")],
              ordenar=M("Custo Pago (R$)"), rotulos=True, dica="tt_eco", cores=[AZUL, LAR], precisao="2L")
    p.grafico("clusteredBarChart", 662, 290, 588, 194, F_SIGLA, [M("Retorno Produto por R$ 1"), M("Retorno Ativo por R$ 1")],
              ordenar=M("Retorno Ativo por R$ 1"), rotulos=True, unidades="1D", dica="tt_eco", rot_y=False, cores=[AZUL, LAR], precisao="2L")
    p.tabela(30, 538, 800, 166, [F_SIGLA, M("PF Faturado"), M("Custo Pago (R$)"), M("Custo Médio por PF Faturado (R$)"), M("Custo a Preço de Mercado (R$)"),
                                 M("Economia vs Mercado (R$)"), M("% Economia"), M("VA Sistemas com Custo (R$)"), M("Retorno Ativo por R$ 1")],
             nomes={0: "Sistema", 1: "PF faturado", 2: "Custo pago", 3: "R$/PF", 4: "A preço de mercado", 5: "Economia", 6: "%", 7: "VA 2026", 8: "VA por R$ 1"},
             ordenar=M("Custo Pago (R$)"), barras=M("Economia vs Mercado (R$)"), tam=8.5)
    paginas.append(p)

    # ===== CENÁRIOS (placar) =====
    p = Pagina("cen")
    s = cabecalho("cen") + barra_filtros([("alvo", "Cenário A", 20), ("alvo", "Cenário B", 470)], "Desenvolvidos internamente · fonte: aba Avaliação 2026 e Dados.xlsx") + leitura()
    for x, lado, cor in ((20, "A", LAR), (960, "B", AZUL)):
        s += ret(x, 146, 300, 564, CARD, 16, LINHA, 1, 'filter="url(#sombra)"') + f'<rect x="{x}" y="146" width="300" height="6" rx="3" fill="{cor}"/>'
        s += txt(x + 18, 176, f"CENÁRIO {lado} · escolha no seletor", 10, cor, 800, 'letter-spacing="1"')
        s += txt(x + 18, 420, "Valor no cenário", 11, APOIO, 600) + txt(x + 18, 498, "Diferença para o Real 2026", 11, APOIO, 600)
        s += txt(x + 18, 576, "Diferença para o Real 2025", 11, APOIO, 600)
        p.texto_longo(x + 12, 184, 276, 60, f"Nome Cenário {lado}", 15, AZUL_ESC, CARD, True)
        p.texto_longo(x + 12, 246, 276, 84, f"Pergunta Cenário {lado}", 10.5, TEXTO, CARD)
        p.texto_longo(x + 12, 332, 276, 64, f"Premissas Cenário {lado}", 9.5, APOIO, CARD)
        p.valor(x + 14, 428, 276, 46, f"Valor Cenário {lado}", 20, cor)
        p.valor(x + 14, 506, 276, 40, f"Dif Real 2026 Cenário {lado}", 15, TEXTO)
        p.valor(x + 14, 584, 276, 40, f"Dif Real 2025 Cenário {lado}", 15, TEXTO)
    s += ret(332, 146, 616, 112, AZUL, 16, None, extra='filter="url(#sombra)"')
    s += txt(640, 172, "PLACAR DOS CENÁRIOS", 11, LAR, 800, 'text-anchor="middle" letter-spacing="2"')
    s += txt(640, 214, "×", 30, "#FFFFFF", 800, 'text-anchor="middle"')
    p.valor(344, 180, 270, 44, "Valor Cenário A", 18, "#FFFFFF")
    p.valor(668, 180, 270, 44, "Valor Cenário B", 18, "#FFFFFF")
    p.texto_longo(346, 224, 590, 30, "Placar Cenários", 10.5, "#FFFFFF", AZUL, True)
    IND = [("Valor (R$)", "Valor Cenário"), ("Tamanho funcional (PF)", "PF Cenário"), ("Preço do PF (R$)", "Preço PF Cenário"),
           ("Sistemas", "Sistemas Cenário"), ("Valor por PF (R$)", "Valor por PF"), ("Valor por sistema (R$)", "Valor por Sistema")]
    s += ret(332, 270, 616, 226, CARD, 16, LINHA, 1, 'filter="url(#sombra)"')
    for i, (rot, base) in enumerate(IND):
        y = 282 + i * 35
        if i:
            s += f'<line x1="348" y1="{y - 2}" x2="932" y2="{y - 2}" stroke="{LINHA}"/>'
        s += ret(552, y + 4, 176, 24, AZUL_CL, 12, None) + txt(640, y + 21, rot.upper(), 9.5, AZUL_ESC, 800, 'text-anchor="middle"')
        p.valor(346, y, 200, 32, f"{base} A", 13, TEXTO, f"Cor {base} A")
        p.valor(740, y, 200, 32, f"{base} B", 13, TEXTO, f"Cor {base} B")
    s += txt(640, 490, "laranja: lado com o maior valor no indicador", 9, SUAVE, 400, 'text-anchor="middle"')
    s += cartao(332, 508, 616, 202, "Todos os cenários", "grafico", "valor dos desenvolvidos, R$ milhões")
    svgs["cen"] = svg_doc(s)
    p.slicer(110, 62, 340, 32, "dCenarioA", "Cenário", unico=True)
    p.slicer(560, 62, 340, 32, "dCenarioB", "Cenário", unico=True)
    navegacao(p)
    p.texto_longo(150, 103, 1112, 42, "Leitura Placar", 10, TEXTO, PORC, True)
    p.barras(342, 542, 596, 162, C("fCenario", "Cenário"), M("Valor do Cenário (R$)"), cor=AZUL, margem=45)
    paginas.append(p)

    # ===== PONTE 2025-2026 =====
    p = Pagina("ponte")
    s = cabecalho("ponte") + barra_filtros([("codigo", "Sistema", 20), ("linha", "Movimento do tamanho", 330)], "Desenvolvidos internamente · decomposição sequencial: preço, tamanho e VI") + leitura()
    s = heroi(p, s, "Valor dos desenvolvidos em 2025", "cubo", "Efeito Base 2025", None, None)
    s += txt(36, 236, "31 sistemas · 26.660 PF · R$ 943,25 por PF", 10, "#E3F0F4")
    KP = [("Novo preço do PF", "moeda", "Efeito Preço", "% Efeito Preço"), ("Sistemas novos (8)", "cubo", "Efeito Novos", "% Efeito Novos"),
          ("Revisão do Valor Institucional", "trofeu", "Efeito VI", "% Efeito VI"), ("Tamanho funcional", "regua", "Efeito Tamanho", "% Efeito Tamanho")]
    for i, (rot, ic, med, ctx) in enumerate(KP):
        s = kpi_padrao(p, s, 332 + i * 232, 146, 220, rot, ic, med, ctx, None)
    s += cartao(20, 254, 620, 236, "Do valor de 2025 ao de 2026", "linha", "R$ milhões por fator")
    s += cartao(652, 254, 608, 236, "Variação do tamanho nos sistemas mantidos", "regua", "PF de 2025 para 2026")
    s += cartao(20, 502, 1240, 208, "Ponte por sistema", "lista", "efeitos de preço, tamanho, VI e entrada de sistemas novos")
    svgs["ponte"] = svg_doc(s)
    p.slicer(96, 62, 220, 32, "dProduto", "Sigla")
    p.slicer(500, 62, 220, 32, "fPonte", "Movimento do Tamanho")
    navegacao(p)
    p.texto_longo(150, 103, 1112, 42, "Leitura Ponte", 9.5, TEXTO, PORC, True)
    p.cascata(30, 290, 600, 194, C("fPonteFator", "Fator"), M("Efeito Fator (R$)"))
    p.barras(662, 290, 588, 194, F_SIGLA, M("Variação PF Sistemas"), cor_medida="Cor Variação PF Sistema", unidades="1D", precisao="1L",
             filtros=[filtro_in("fPonte", "Situação no Período", ["Mantido"], "filtroMantidos")])
    p.tabela(30, 538, 1220, 166, [F_SIGLA, C("fPonte", "Situação no Período"), C("fPonte", "PF 2025"), C("fPonte", "PF 2026"), C("fPonte", "Variação PF"),
                                  C("fPonte", "VI 2025"), C("fPonte", "VI 2026"), C("fPonte", "VA 2025 (R$)"), C("fPonte", "Efeito Preço (R$)"),
                                  C("fPonte", "Efeito Tamanho (R$)"), C("fPonte", "Efeito VI (R$)"), C("fPonte", "Efeito Novo Sistema (R$)"), C("fPonte", "VA 2026 (R$)")],
             nomes={0: "Sistema", 1: "Período", 2: "PF 2025", 3: "PF 2026", 4: "Var. PF", 5: "VI 2025", 6: "VI 2026", 7: "VA 2025", 8: "Efeito preço",
                    9: "Efeito tamanho", 10: "Efeito VI", 11: "Sistema novo", 12: "VA 2026"},
             ordenar=C("fPonte", "VA 2026 (R$)"), tam=8.5)
    paginas.append(p)

    # ===== OPERACIONAL =====
    p = Pagina("ope")
    s = cabecalho("ope") + barra_filtros([("camadas", "Categoria", 20), ("engrenagem", "Situação", 290), ("documento", "Documentação", 560), ("lupa", "Diligência", 820)]) + leitura()
    s += cartao(20, 150, 1240, 352, "Catálogo detalhado", "lista", "uma linha por produto · passe o mouse para a ficha resumida")
    s += cartao(20, 514, 1240, 196, "Diligências da 3ª Nota Técnica", "lupa", "filtre o catálogo para ver as diligências aplicáveis")
    svgs["ope"] = svg_doc(s)
    p.slicer(96, 62, 180, 32, "dProduto", "Categoria")
    p.slicer(360, 62, 190, 32, "dProduto", "Situação Resumida")
    p.slicer(656, 62, 150, 32, "dProduto", "Documentação")
    p.slicer(900, 62, 110, 32, "dDiligencia", "Código")
    navegacao(p)
    p.texto_longo(150, 103, 1112, 42, "Leitura Operacional", 10, TEXTO, PORC, True)
    p.tabela(30, 186, 1220, 310, [F_SIGLA, F_NOME, F_CAT, F_SIT, C("dProduto", "Tecnologia"), C("dProduto", "Documentação"), M("PF Atual"),
                                  M("VI Atual"), M("Valor Atual (R$)"), M("Var % (tabela)"), C("dProduto", "Principal Achado"), C("dProduto", "Diligências"),
                                  C("dProduto", "Laudo")],
             nomes={0: "Sigla", 1: "Produto", 2: "Categoria", 3: "Situação", 4: "Tecnologia", 5: "Documentação", 6: "PF", 7: "VI", 8: "Valor 2026",
                    9: "Variação", 10: "Principal achado", 11: "Diligências", 12: "Laudo"},
             ordenar=M("Valor Atual (R$)"), cor_por=[(F_SIT, "Cor Situação"), (C("dProduto", "Documentação"), "Cor Documentação"), (M("Var % (tabela)"), "Cor Var Valor")],
             dica="tt_prod", tam=8.5)
    p.tabela(30, 550, 1220, 154, [C("dDiligencia", "Código"), C("dDiligencia", "Objeto"), C("dDiligencia", "Destinatário"), C("dDiligencia", "Prazo Sugerido"),
                                  M("Produtos Alcançados")],
             nomes={0: "Nº", 1: "Objeto", 2: "Destinatário", 3: "Prazo", 4: "Produtos"}, ordenar=C("dDiligencia", "Código"), desc=False, tam=8.5)
    paginas.append(p)

    # ===== FICHA DO PRODUTO =====
    p = Pagina("ficha")
    s = cabecalho("ficha") + barra_filtros([("lupa", "Produto", 20)], "Fonte: Laudo Técnico de Avaliação do produto")
    s += ret(20, 110, 1240, 84, AZUL, 14, None, extra='filter="url(#sombra)"') + icone("cubo", 36, 128, LAR, 1.3)
    KP = [("Valor no inventário", "cubo", "Valor Atual (R$)", "% Variação Valor", "Cor Var Valor"), ("Pontos de função", "regua", "PF Atual", "% Variação PF", "Cor Var PF"),
          ("Valor Institucional", "trofeu", "VI Atual", "VI Anterior", None), ("Integrações", "conexao", "Qtde Integrações", "Qtde Módulos (contexto)", None)]
    for i, (rot, ic, med, ctx, cor) in enumerate(KP):
        s = kpi_padrao(p, s, 20 + i * 196, 204, 184, rot, ic, med, ctx, cor)
    s += cartao(20, 310, 772, 190, "Finalidade e benefício", "documento")
    s += cartao(804, 204, 456, 296, "Tamanho por módulo", "camadas", "PF (laudo)")
    s += cartao(20, 512, 380, 198, "Funções por tipo", "grafico", "quantidade")
    s += cartao(412, 512, 380, 198, "Evolução no inventário", "linha", "R$ milhões e PF")
    s += cartao(804, 512, 456, 198, "Achado, diligências e laudo", "lupa")
    svgs["ficha"] = svg_doc(s)
    p.slicer(96, 62, 420, 32, "dProduto", "Nome do Produto", unico=True)
    navegacao(p)
    p.texto_longo(72, 114, 900, 40, "Ficha Produto", 15, "#FFFFFF", AZUL, True)
    p.texto_longo(72, 154, 1170, 36, "Ficha Categoria", 10, "#E3F0F4", AZUL)
    p.texto_longo(980, 116, 270, 36, "Ficha Situação", 10.5, LAR, AZUL, True)
    p.texto_longo(32, 344, 752, 110, "Ficha Finalidade", 9, TEXTO)
    p.texto_longo(32, 456, 752, 40, "Ficha Benefício", 9, APOIO, CARD, True)
    p.barras(812, 240, 440, 254, C("fModulo", "Módulo"), M("PF Módulo"), unidades="1D", precisao="1L", margem=55)
    p.grafico("columnChart", 30, 548, 360, 156, C("dTipoFuncao", "Tipo de Função"), [M("Qtde Funções")], cor_unica=AZUL, rotulos=True, unidades="1D", legenda=False,
              precisao="0L")
    p.combo(422, 548, 360, 156, F_INV, [M("Valor Final (R$)")], [M("Tamanho Funcional (PF)")], rotulos=False, secundario=True)
    p.texto_longo(816, 546, 436, 46, "Ficha Achado", 9.5, TEXTO, CARD, True)
    p.texto_longo(816, 594, 436, 26, "Ficha Diligências", 10, LAR, CARD, True)
    p.texto_longo(816, 622, 436, 40, "Ficha Documentação", 9, APOIO)
    p.texto_longo(816, 664, 436, 40, "Ficha Laudo", 8.5, AZUL, CARD, True)
    paginas.append(p)

    # ===== TOOLTIPS =====
    t = Pagina("tt_prod", 320, 240, tooltip=True)
    s = ret(0, 0, 320, 240, CARD, 0, None) + f'<rect x="0" y="0" width="320" height="6" fill="{LAR}"/>' + icone("cubo", 14, 18, AZUL, 1.0)
    s += txt(14, 112, "Valor", 10, SUAVE) + txt(124, 112, "PF", 10, SUAVE) + txt(214, 112, "Variação", 10, SUAVE)
    s += f'<line x1="14" y1="156" x2="306" y2="156" stroke="{LINHA}"/>'
    svgs["tt_prod"] = svg_doc(s, CARD, 320, 240)
    t.texto_longo(34, 10, 282, 30, "Ficha Sigla", 12, AZUL_ESC, CARD, True)
    t.texto_longo(10, 40, 302, 56, "Ficha Produto", 9, APOIO, CARD)
    t.valor(10, 116, 112, 34, "Valor Atual (R$)", 10.5)
    t.valor(120, 116, 90, 34, "PF Atual", 10.5)
    t.valor(210, 116, 106, 34, "Var % (tabela)", 10.5, TEXTO, "Cor Var Valor")
    t.texto_longo(10, 160, 302, 26, "Ficha Situação", 9, LAR, CARD, True)
    t.texto_longo(10, 186, 302, 50, "Ficha Achado", 8.5, TEXTO)
    paginas.append(t)

    t = Pagina("tt_eco", 320, 240, tooltip=True)
    s = ret(0, 0, 320, 240, CARD, 0, None) + f'<rect x="0" y="0" width="320" height="6" fill="{LAR}"/>' + icone("porquinho", 14, 18, AZUL, 1.0)
    for i, rot in enumerate(["Custo pago", "PF faturado", "Custo por PF faturado", "A preço de mercado", "Economia", "VA por R$ 1,00"]):
        s += txt(14, 70 + i * 28, rot, 10.5, APOIO)
    svgs["tt_eco"] = svg_doc(s, CARD, 320, 240)
    t.texto_longo(34, 10, 282, 30, "Ficha Sigla", 12, AZUL_ESC, CARD, True)
    for i, med in enumerate(["Custo Pago (R$)", "PF Faturado", "Custo Médio por PF Faturado (R$)", "Custo a Preço de Mercado (R$)", "Economia vs Mercado (R$)",
                             "Retorno Ativo por R$ 1"]):
        t.valor(150, 52 + i * 28, 166, 28, med, 10.5, LAR if i == 4 else AZUL_ESC)
    paginas.append(t)

    # ---- grava páginas, tema e metadados do relatório
    arquivos = [pg.grava(svgs[pg.chave]) for pg in paginas]
    tema = {"name": "CIABI Catálogo 60-30-10", "dataColors": CORES_DADOS, "foreground": TEXTO, "background": CARD, "tableAccent": AZUL,
            "good": AZUL, "bad": LAR, "neutral": "#6FA0B3", "maximum": AZUL, "center": "#B9D3DA", "minimum": PORC,
            "textClasses": {"label": {"fontFace": "Segoe UI", "color": APOIO}, "title": {"fontFace": "Segoe UI Semibold", "color": TEXTO},
                            "callout": {"fontFace": "Segoe UI Bold", "color": AZUL_ESC}}}
    gravar(RES / "CIABI_Catalogo_60-30-10.json", json.dumps(tema, ensure_ascii=False, indent=2))
    base = RES.parent / "SharedResources" / "BaseThemes"
    base.mkdir(parents=True, exist_ok=True)
    shutil.copy(ASSETS / "CY23SU11.json", base / "CY23SU11.json")
    versao = {"visual": "1.8.86", "report": "2.0.86", "page": "1.3.86"}
    rep = {"$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/report/3.1.0/schema.json",
           "themeCollection": {"baseTheme": {"name": "CY23SU11", "reportVersionAtImport": versao, "type": "SharedResources"},
                               "customTheme": {"name": "CIABI_Catalogo_60-30-10.json", "reportVersionAtImport": versao, "type": "RegisteredResources"}},
           "objects": {"section": [{"properties": {"verticalAlignment": S("Top")}}], "outspacePane": [{"properties": {"expanded": L("false")}}]},
           "resourcePackages": [{"name": "SharedResources", "type": "SharedResources", "items": [{"name": "CY23SU11", "path": "BaseThemes/CY23SU11.json", "type": "BaseTheme"}]},
                                {"name": "RegisteredResources", "type": "RegisteredResources",
                                 "items": [{"name": a, "path": a, "type": "Image"} for a in arquivos]
                                 + [{"name": "CIABI_Catalogo_60-30-10.json", "path": "CIABI_Catalogo_60-30-10.json", "type": "CustomTheme"}]}],
           "settings": {"useStylableVisualContainerHeader": True, "exportDataMode": "AllowSummarized", "defaultDrillFilterOtherVisuals": True,
                        "allowChangeFilterTypes": True, "useEnhancedTooltips": True, "useDefaultAggregateDisplayName": True}}
    gravar(DEF / "report.json", json.dumps(rep, ensure_ascii=False, indent=2))
    gravar(DEF / "version.json", json.dumps({"$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/versionMetadata/1.0.0/schema.json",
                                             "version": "2.0.0"}, indent=2))
    gravar(DEF / "pages" / "pages.json", json.dumps({"$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.0.0/schema.json",
                                                     "pageOrder": [pg.id for pg in paginas], "activePageName": PAGINAS["capa"][0]}, ensure_ascii=False, indent=2))
    gravar(REP / "definition.pbir", json.dumps({"$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definitionProperties/2.0.0/schema.json",
                                                "version": "4.0", "datasetReference": {"byPath": {"path": f"../{NOME}.SemanticModel"}}}, ensure_ascii=False, indent=2))
    gravar(REP / ".platform", json.dumps({"$schema": "https://developer.microsoft.com/json-schemas/fabric/gitIntegration/platformProperties/2.0.0/schema.json",
                                          "metadata": {"type": "Report", "displayName": NOME}, "config": {"version": "2.0", "logicalId": tag()}}, ensure_ascii=False, indent=2))
    gravar(RAIZ / f"{NOME}.pbip", json.dumps({"$schema": "https://developer.microsoft.com/json-schemas/fabric/pbip/pbipProperties/1.0.0/schema.json",
                                              "version": "1.0", "artifacts": [{"report": {"path": f"{NOME}.Report"}}], "settings": {"enableAutoRecovery": True}},
                                             ensure_ascii=False, indent=2))
    gravar(RAIZ / ".gitignore", "**/.pbi/localSettings.json\n**/.pbi/cache.abf\n")
    # prévias das páginas (SVG) para conferência visual fora do Power BI
    prev = RAIZ / "previas"
    prev.mkdir(exist_ok=True)
    for pg in paginas:
        gravar(prev / f"{pg.chave}.svg", svgs[pg.chave])
    return paginas


if __name__ == "__main__":
    for pasta in (REP, SMD):
        shutil.rmtree(pasta, ignore_errors=True)
    tabelas = gera_modelo()
    paginas = gera_relatorio()
    print(f"  modelo: {len(tabelas)} tabelas + Medidas ({len(MEDIDAS)} medidas), {len(RELACOES)} relacionamentos")
    print(f"  relatório: {len(paginas)} páginas, {sum(len(p.visuais) for p in paginas)} visuais -> {RAIZ}")
