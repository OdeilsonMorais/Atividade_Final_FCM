import os
import pandas as pd
import matplotlib.pyplot as plt

pasta_julio = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
pasta_projeto = os.path.dirname(pasta_julio)

arquivo_scopus = os.path.join(pasta_projeto, "dados", "artigos_scopus_G.csv")
arquivo_total_pais = os.path.join(pasta_projeto, "dados", "total_scopus_por_pais.csv")
pasta_resultados = os.path.join(pasta_julio, "resultados")

os.makedirs(pasta_resultados, exist_ok=True)

scopus = pd.read_csv(arquivo_scopus, encoding="utf-8-sig")
scopus = scopus[scopus["tipo_doc"].isin(["Article", "Review"])].copy()
scopus["ano"] = pd.to_numeric(scopus["ano"], errors="coerce")
scopus["citacoes"] = pd.to_numeric(scopus["citacoes"], errors="coerce")
scopus = scopus.dropna(subset=["ano", "citacoes"]).copy()
scopus["citacoes_por_ano"] = scopus["citacoes"] / (2026 - scopus["ano"])
media_ano = scopus.groupby("ano")["citacoes"].transform("mean")
scopus["impacto_norm_ano"] = scopus["citacoes"] / media_ano.replace(0, float("nan"))
scopus["tem_financiamento"] = (
    scopus[["fund_sponsor", "fund_acr", "fund_no"]]
    .fillna("")
    .astype(str)
    .apply(lambda col: col.str.strip().ne(""))
    .any(axis=1)
)
scopus["lista_paises"] = scopus["paises"].fillna("").apply(
    lambda s: sorted({p.strip() for p in str(s).split(";") if p.strip()})
)

por_pais = scopus.explode("lista_paises").dropna(subset=["lista_paises"]).rename(columns={"lista_paises": "pais"})

volume = por_pais.groupby("pais")["eid"].nunique().reset_index(name="total_artigos")
impacto = por_pais.groupby("pais").agg(
    citacoes_por_ano=("citacoes_por_ano", "mean"),
    impacto_norm_ano=("impacto_norm_ano", "mean")
).reset_index()
financiamento = por_pais.groupby("pais")["tem_financiamento"].mean().mul(100).round(1).reset_index(name="porcentagem_financiada")

total_pais = pd.read_csv(arquivo_total_pais, encoding="utf-8-sig")

# junta todas as tabelas pelo nome do país
dados = pd.merge(volume, impacto, on="pais")
dados = pd.merge(dados, financiamento, on="pais")
dados = pd.merge(dados, total_pais, on="pais", how="left")

# normaliza pelo total de publicações de cada país na Scopus
dados["artigos_por_100k"] = dados["total_artigos"] / dados["total_scopus_2000_2025"] * 100000
dados = dados[dados["total_artigos"] >= 10]
dados = dados.sort_values("total_artigos", ascending=False).reset_index(drop=True)

corr_vol_impacto = dados["total_artigos"].corr(dados["impacto_norm_ano"], method="spearman")

lider_volume = dados["pais"].iloc[0]
lider_impacto = dados.sort_values("impacto_norm_ano", ascending=False)["pais"].iloc[0]
lider_normalizado = dados.sort_values("artigos_por_100k", ascending=False)["pais"].iloc[0]

tem_financiamento = dados["porcentagem_financiada"].max() > 0

if tem_financiamento:
    corr_vol_financiamento = dados["total_artigos"].corr(dados["porcentagem_financiada"], method="spearman")
    lider_financiamento = dados.sort_values("porcentagem_financiada", ascending=False)["pais"].iloc[0]
else:
    lider_financiamento = "Aguardando os dados do Gabriel"

print("Resultado da hipótese 2:")
print("1o lugar em volume:", lider_volume)
print("1o lugar em foco relativo (por 100 mil):", lider_normalizado)
print("1o lugar em impacto normalizado (FWCI):", lider_impacto)
print("1o lugar em financiamento:", lider_financiamento)
print(f"Correlação volume x impacto normalizado: {corr_vol_impacto:.2f}")

if tem_financiamento:
    print(f"Correlação volume x financiamento: {corr_vol_financiamento:.2f}")

print("")
print(dados[["pais", "total_artigos", "artigos_por_100k", "impacto_norm_ano", "porcentagem_financiada"]].head(10))

# gráfico 1: bruto vs normalizado (cores fixas pros principais países)
cores_destaque = {
    "China": "#c0392b",
    "Hong Kong": "#8e44ad",
    "Singapore": "#2e8b57",
    "South Korea": "#e67e22",
    "United States": "#2980b9"
}

top10_bruto = dados.head(10).sort_values("total_artigos", ascending=True)
dados_com_total = dados.dropna(subset=["artigos_por_100k"])
top10_norm = dados_com_total.sort_values("artigos_por_100k", ascending=False).head(10)
top10_norm = top10_norm.sort_values("artigos_por_100k", ascending=True)

cores_bruto = []
for pais in top10_bruto["pais"]:
    if pais in cores_destaque:
        cores_bruto.append(cores_destaque[pais])
    else:
        cores_bruto.append("#95a5a6")

cores_norm = []
for pais in top10_norm["pais"]:
    if pais in cores_destaque:
        cores_norm.append(cores_destaque[pais])
    else:
        cores_norm.append("#95a5a6")

fig1, eixos1 = plt.subplots(1, 2, figsize=(12, 5))

eixos1[0].barh(top10_bruto["pais"], top10_bruto["total_artigos"], color=cores_bruto)
eixos1[0].set_title("Top 10 - Quantidade bruta de artigos")
eixos1[0].set_xlabel("Total de artigos (2000-2025)")
eixos1[0].grid(axis="x", alpha=0.3)

eixos1[1].barh(top10_norm["pais"], top10_norm["artigos_por_100k"], color=cores_norm)
eixos1[1].set_title("Top 10 - Foco relativo (normalizado)")
eixos1[1].set_xlabel("Artigos a cada 100 mil publicações do país")
eixos1[1].grid(axis="x", alpha=0.3)

fig1.suptitle("Volume bruto vs. foco relativo por país", fontsize=11.5)
plt.tight_layout()
plt.savefig(os.path.join(pasta_resultados, "fig_bruto_vs_normalizado.png"), dpi=300, transparent=True)
plt.close()

# gráfico 2: comparação geral (volume e impacto)
top10 = top10_bruto

fig2, eixos2 = plt.subplots(1, 2, figsize=(11, 5), sharey=True)

eixos2[0].barh(top10["pais"], top10["total_artigos"], color="#2b6cb0")
eixos2[0].set_title("Quantidade de artigos")
eixos2[0].set_xlabel("Total de artigos")
eixos2[0].grid(axis="x", alpha=0.3)

eixos2[1].barh(top10["pais"], top10["impacto_norm_ano"], color="#dd6b20")
eixos2[1].axvline(1.0, color="#c53030", linestyle="--", linewidth=1.4, label="Média da área (1,0)")
eixos2[1].set_title("Impacto normalizado (estilo FWCI)")
eixos2[1].set_xlabel("Razão em relação à média do ano")
eixos2[1].set_xlim(0, 2.15)
eixos2[1].legend(loc="upper right")
eixos2[1].grid(axis="x", alpha=0.3)

fig2.suptitle("Comparação dos 10 países que mais publicam: volume e impacto", fontsize=12)
plt.tight_layout()
plt.savefig(os.path.join(pasta_resultados, "fig_sintese_hipotese2.png"), dpi=300, transparent=True)
plt.close()
