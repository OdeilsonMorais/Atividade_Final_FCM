"""
Mapa interativo do número de publicações por país (sua parte: distribuição geográfica).
Abra o HTML no navegador: passe o cursor sobre um país para ver o número de publicações;
os botões alternam entre o total e os dois períodos.

Lê os CSVs da pasta ../coleta/dados.

Uso:
    python mapa.py              # busca G -> figuras/mapa_publicacoes_G.html
    python mapa.py --busca A    # busca A -> figuras/mapa_publicacoes.html (precisa de dados/artigos_scopus.csv)
"""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import pycountry

TIPOS = ["Article", "Review"]
MARCO = 2014

BASE = Path(__file__).resolve().parent
DADOS = BASE.parent.parent / "dados" 

ap = argparse.ArgumentParser()
ap.add_argument("--busca", default="G", help="G (ampliada, padrão) ou A (original)")
args = ap.parse_args()
sufixo = "" if args.busca == "A" else f"_{args.busca}"
args.rotulo = "" if args.busca == "A" else f"busca {args.busca}"
args.saida = BASE / "figuras" / f"mapa_publicacoes{sufixo}.html"
args.saida.parent.mkdir(exist_ok=True)

df = pd.read_csv(DADOS / f"artigos_scopus{sufixo}.csv", encoding="utf-8-sig")
df = df[df["tipo_doc"].isin(TIPOS)].copy()
df["periodo"] = np.where(df["ano"].astype(int) < MARCO, "2000-2013", "2014-2025")
df["pais"] = df["paises"].fillna("").apply(lambda s: sorted({p.strip() for p in s.split(";") if p.strip()}))
ap_ = df.explode("pais").dropna(subset=["pais"])
geo = ap_.groupby(["pais", "periodo"]).size().unstack(fill_value=0)
for c in ["2000-2013", "2014-2025"]:
    if c not in geo:
        geo[c] = 0
geo["total"] = geo["2000-2013"] + geo["2014-2025"]
geo = geo.reset_index()
n_per = df["periodo"].value_counts()
print(f"{len(df)} artigos e revisões: 2000-2013 = {n_per.get('2000-2013', 0)}, 2014-2025 = {n_per.get('2014-2025', 0)}")

CORRECOES = {"South Korea": "KOR", "Taiwan": "TWN", "Hong Kong": "HKG", "Macao": "MAC",
             "Iran": "IRN", "Russian Federation": "RUS", "Turkey": "TUR", "Viet Nam": "VNM"}


def iso3(nome):
    if nome in CORRECOES:
        return CORRECOES[nome]
    try:
        return pycountry.countries.lookup(nome).alpha_3
    except LookupError:
        try:
            return pycountry.countries.search_fuzzy(nome)[0].alpha_3
        except LookupError:
            return None


geo["iso3"] = geo["pais"].apply(iso3)
sem = geo[geo["iso3"].isna()]["pais"].tolist()
if sem:
    print("Países sem código (fora do mapa):", sem)
geo = geo.dropna(subset=["iso3"])

colunas = [("total", "2000–2025 (total)"), ("2000-2013", "2000–2013"), ("2014-2025", "2014–2025")]
fig = go.Figure()
for i, (col, rotulo) in enumerate(colunas):
    d = geo[geo[col] > 0]
    vmax = d[col].max()
    ticks = [v for v in [1, 2, 5, 10, 20, 50, 100, 200, 500, 1000] if v <= vmax]
    fig.add_trace(go.Choropleth(
        locations=d["iso3"], z=np.log10(d[col]), text=d["pais"],
        customdata=d[col], visible=(i == 0), colorscale="YlGnBu",
        zmin=0, zmax=np.log10(vmax),
        hovertemplate="<b>%{text}</b><br>%{customdata} publicações<extra></extra>",
        marker_line_color="white", marker_line_width=0.4,
        colorbar=dict(title="Publicações", tickvals=np.log10(ticks), ticktext=ticks),
    ))

extra = f" ({args.rotulo})" if args.rotulo else ""
titulo = "Publicações sobre resfriamento radiativo passivo por país — {}" + extra
botoes = [dict(label=rotulo, method="update",
               args=[{"visible": [j == i for j in range(len(colunas))]},
                     {"title.text": titulo.format(rotulo)}])
          for i, (_, rotulo) in enumerate(colunas)]

fig.update_layout(
    title=dict(text=titulo.format(colunas[0][1]), x=0.5),
    updatemenus=[dict(type="buttons", direction="right", buttons=botoes, x=0.5, xanchor="center", y=1.02, yanchor="bottom")],
    geo=dict(projection_type="natural earth", projection_rotation=dict(lon=10),
             center=dict(lon=10, lat=15), lataxis_range=[-58, 85], showframe=False, showcoastlines=False,
             showcountries=True, countrycolor="#ccc", landcolor="#f2f2f2", showland=True, resolution=50),
    margin=dict(l=0, r=0, t=90, b=10),
    annotations=[dict(text="Fonte: Scopus, artigos e revisões. Contagem inteira: um artigo conta para cada país das afiliações. Escala de cores logarítmica.",
                      x=0.5, y=0, xref="paper", yref="paper", showarrow=False, font=dict(size=11, color="#666"))],
)

fig.write_html(args.saida, include_plotlyjs=True)
print(f"Mapa salvo em {args.saida} ({len(geo)} países)")
