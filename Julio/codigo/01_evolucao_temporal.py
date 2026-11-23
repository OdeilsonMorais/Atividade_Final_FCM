import os
import pandas as pd
import matplotlib.pyplot as plt

pasta_julio = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
pasta_projeto = os.path.dirname(pasta_julio)

arquivo_scopus = os.path.join(pasta_projeto, "dados", "artigos_scopus_G.csv")
arquivo_total_mundo = os.path.join(pasta_projeto, "dados", "total_scopus_por_ano.csv")
pasta_resultados = os.path.join(pasta_julio, "resultados")

os.makedirs(pasta_resultados, exist_ok=True)

tabela = pd.read_csv(arquivo_scopus, encoding="utf-8-sig")
total_mundo = pd.read_csv(arquivo_total_mundo, encoding="utf-8-sig")

tabela = tabela[tabela["tipo_doc"].isin(["Article", "Review"])]
tabela = tabela[(tabela["ano"] >= 2000) & (tabela["ano"] <= 2025)]

# conta quantos artigos saíram em cada ano
todos_os_anos = list(range(2000, 2026))
contagem = []
for ano in todos_os_anos:
    qtd = int((tabela["ano"] == ano).sum())
    contagem.append(qtd)

# junta com o total mundial da Scopus pra fazer a normalização
resumo_anual = pd.DataFrame({"ano": todos_os_anos, "artigos": contagem})
resumo_anual = pd.merge(resumo_anual, total_mundo, on="ano")
resumo_anual["por_milhao"] = resumo_anual["artigos"] / resumo_anual["total_scopus_mundo"] * 1000000

antes_2014 = resumo_anual[resumo_anual["ano"] <= 2013]
depois_2014 = resumo_anual[resumo_anual["ano"] >= 2014]

total_antes = int(antes_2014["artigos"].sum())
total_depois = int(depois_2014["artigos"].sum())
media_antes = float(antes_2014["artigos"].mean())
media_depois = float(depois_2014["artigos"].mean())
media_milhao_antes = float(antes_2014["por_milhao"].mean())
media_milhao_depois = float(depois_2014["por_milhao"].mean())

print("Resultado da evolução temporal (2000 a 2025):")
print(f"Total de artigos: {total_antes + total_depois}")
print(f"2000 a 2013: {total_antes} artigos (média de {media_antes:.1f}/ano | {media_milhao_antes:.2f} por milhão)")
print(f"2014 a 2025: {total_depois} artigos (média de {media_depois:.1f}/ano | {media_milhao_depois:.2f} por milhão)")

# dois gráficos lado a lado: bruto e normalizado
fig, eixos = plt.subplots(1, 2, figsize=(13, 5))

eixos[0].plot(resumo_anual["ano"], resumo_anual["artigos"], marker="o", color="steelblue", linewidth=2, label="Artigos por ano")
eixos[0].axvline(2014, color="red", linestyle="--", linewidth=1.8, label="Marco de 2014")
eixos[0].set_title("Volume bruto anual")
eixos[0].set_xlabel("Ano de publicação")
eixos[0].set_ylabel("Número de artigos")
eixos[0].set_ylim(bottom=0)
eixos[0].legend()
eixos[0].grid(True, alpha=0.3)

eixos[1].plot(resumo_anual["ano"], resumo_anual["por_milhao"], marker="o", color="green", linewidth=2, label="Artigos por milhão no mundo")
eixos[1].axvline(2014, color="red", linestyle="--", linewidth=1.8, label="Marco de 2014")
eixos[1].set_title("Normalizado pelo total mundial da Scopus")
eixos[1].set_xlabel("Ano de publicação")
eixos[1].set_ylabel("Artigos por milhão de publicações no mundo")
eixos[1].set_ylim(bottom=0)
eixos[1].legend()
eixos[1].grid(True, alpha=0.3)

fig.suptitle("Evolução das publicações sobre resfriamento radiativo passivo (2000-2025)", fontsize=12)
plt.tight_layout()
plt.savefig(pasta_resultados + "/fig_evolucao_temporal.png", dpi=300)
plt.close()
