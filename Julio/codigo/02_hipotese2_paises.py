import os
import pandas as pd
import matplotlib.pyplot as plt

arquivo_volume = ""
arquivo_impacto = ""
arquivo_financiamento = ""
arquivo_total_pais = ""
pasta_resultados = ""

os.makedirs(pasta_resultados, exist_ok=True)

volume = pd.read_csv(arquivo_volume)
impacto = pd.read_csv(arquivo_impacto)
financiamento = pd.read_csv(arquivo_financiamento)
total_pais = pd.read_csv(arquivo_total_pais)

# junta todas as tabelas pelo nome do país
dados = pd.merge(volume, impacto, on="pais")
dados = pd.merge(dados, financiamento, on="pais")
dados = pd.merge(dados, total_pais, on="pais", how="left")

# normaliza pelo total de publicações de cada país na Scopus
dados["artigos_por_100k"] = dados["total_artigos"] / dados["total_scopus_2000_2025"] * 100000
dados = dados.sort_values("total_artigos", ascending=False).reset_index(drop=True)

corr_vol_impacto = dados["total_artigos"].corr(dados["citacoes_por_ano"], method="spearman")

lider_volume = dados["pais"].iloc[0]
lider_impacto = dados.sort_values("citacoes_por_ano", ascending=False)["pais"].iloc[0]
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
print("1o lugar em citações por ano:", lider_impacto)
print("1o lugar em financiamento:", lider_financiamento)
print(f"Correlação volume x citações: {corr_vol_impacto:.2f}")

if tem_financiamento:
    print(f"Correlação volume x financiamento: {corr_vol_financiamento:.2f}")

print("")
print(dados[["pais", "total_artigos", "artigos_por_100k", "citacoes_por_ano", "porcentagem_financiada"]].head(10))

# gráfico 1: bruto vs normalizado (cores fixas pros principais países)
cores_destaque = {
    "China": "red",
    "Singapore": "green",
    "South Korea": "orange",
    "United States": "steelblue"
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
        cores_bruto.append("gray")

cores_norm = []
for pais in top10_norm["pais"]:
    if pais in cores_destaque:
        cores_norm.append(cores_destaque[pais])
    else:
        cores_norm.append("gray")

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
plt.savefig(pasta_resultados + "/fig_bruto_vs_normalizado.png", dpi=300)
plt.close()

# gráfico 2: comparação geral (volume, impacto e financiamento)
top10 = top10_bruto

fig2, eixos2 = plt.subplots(1, 3, figsize=(12, 5), sharey=True)

eixos2[0].barh(top10["pais"], top10["total_artigos"], color="steelblue")
eixos2[0].set_title("Quantidade de artigos")
eixos2[0].set_xlabel("Total de artigos")
eixos2[0].grid(axis="x", alpha=0.3)

eixos2[1].barh(top10["pais"], top10["citacoes_por_ano"], color="orange")
eixos2[1].set_title("Impacto (citações por ano)")
eixos2[1].set_xlabel("Média de citações/ano")
eixos2[1].grid(axis="x", alpha=0.3)

eixos2[2].barh(top10["pais"], top10["porcentagem_financiada"], color="green")
eixos2[2].set_title("Artigos com financiamento")
eixos2[2].set_xlabel("Porcentagem (%)")
eixos2[2].set_xlim(0, 100)
eixos2[2].grid(axis="x", alpha=0.3)

if not tem_financiamento:
    eixos2[2].text(50, 4.5, "Vou tentar encaixar esse grafico \n com os dados q o gabriel tratar", ha="center", va="center", fontsize=10, color="gray")

fig2.suptitle("Comparação dos 10 países que mais publicam: volume, impacto e financiamento", fontsize=12)
plt.tight_layout()
plt.savefig(pasta_resultados + "/fig_sintese_hipotese2.png", dpi=300)
plt.close()
