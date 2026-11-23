#AJUSTE EXPONENCIAL DO CRESCIMENTO (reta em escala logarítmica)
# Depois de 2014, o número de publicações cresce em proporção ao que já existe:
# a cada ano soma-se uma fração quase fixa do ano anterior. Esse comportamento é
# exponencial, e uma reta y = ax + b não o descreve bem (prevê valores negativos
# em 2014 e erra sempre para o mesmo lado no meio do período).
#
# Modelo exponencial: N = N0 * e^(k*ano)
# Tirando o logaritmo:  ln(N) = k*ano + c   ->  é uma reta em ln(N) x ano
#     k = taxa de crescimento contínua (por ano);
#     crescimento anual = e^k - 1 (fração a mais a cada ano);
#     tempo de duplicação = ln(2) / k (anos para o número de publicações dobrar).
#
# Anos com zero publicações não têm logaritmo e ficam fora do ajuste
# (só acontece antes de 2014: 2004 e 2008).
#
# O ajuste linear antigo continua sendo calculado, só para comparação.


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Localiza as pastas
pasta = Path(__file__).resolve().parent.parent

# Lê a tabela de publicações por ano (gerada pelo 02_publicacoes_por_ano.py)
arquivo = pasta / "resultados" / "publicacoes_por_ano.csv"
df = pd.read_csv(arquivo, sep=";", encoding="utf-8-sig")

anos = df["Ano"].to_numpy()
quantidades = df["Quantidade"].to_numpy()

periodos = {
    "2000-2013": df[(df["Ano"] >= 2000) & (df["Ano"] <= 2013)],
    "2014-2025": df[(df["Ano"] >= 2014) & (df["Ano"] <= 2025)],
}


def calcular_r2(observado, estimado):
    soma_residuos = np.sum((observado - estimado) ** 2)
    soma_total = np.sum((observado - np.mean(observado)) ** 2)
    return 1 - (soma_residuos / soma_total)


resultados = []
curvas = {}

print("\nANÁLISE DO CRESCIMENTO DAS PUBLICAÇÕES")

for nome, p in periodos.items():
    x_todos = p["Ano"].to_numpy()
    y_todos = p["Quantidade"].to_numpy()

    # Ajuste exponencial: reta em ln(N), só com anos que têm publicações
    com_publicacao = y_todos > 0
    x = x_todos[com_publicacao]
    y = y_todos[com_publicacao]
    k, c = np.polyfit(x, np.log(y), 1)
    r2_log = calcular_r2(np.log(y), k * x + c)
    crescimento_anual = np.exp(k) - 1
    duplicacao = np.log(2) / k if k > 0 else np.nan

    # Ajuste linear (antigo), para comparação
    a, b = np.polyfit(x_todos, y_todos, 1)
    r2_linear = calcular_r2(y_todos, a * x_todos + b)

    curvas[nome] = (x_todos, np.exp(k * x_todos + c))

    print(f"\nPeríodo de {nome}:")
    print(f"Anos sem publicações (fora do ajuste exponencial): {(~com_publicacao).sum()}")
    print(f"Crescimento anual: {100 * crescimento_anual:.1f}% ao ano")
    print(f"Tempo de duplicação: {duplicacao:.1f} anos")
    print(f"R² do ajuste exponencial (em ln N): {r2_log:.4f}")
    print(f"Comparação - ajuste linear: {a:.2f} publicações por ano, R² = {r2_linear:.4f}")

    resultados.append({
        "Periodo": nome,
        "Crescimento_anual_pct": round(100 * crescimento_anual, 1),
        "Tempo_duplicacao_anos": round(duplicacao, 2),
        "R2_exponencial_lnN": round(r2_log, 4),
        "Inclinacao_linear_pub_por_ano": round(a, 2),
        "R2_linear": round(r2_linear, 4),
    })

# Gráfico com dois painéis: escala comum e escala logarítmica
fig, eixos = plt.subplots(1, 2, figsize=(14, 5.5))

# Na escala log, zero não pode ser desenhado: esses anos ficam como lacuna
quantidades_log = np.where(quantidades > 0, quantidades, np.nan)

for eixo, y_plot in zip(eixos, [quantidades, quantidades_log]):
    eixo.plot(anos, y_plot, marker="o", color="#1f77b4", label="Publicações por ano")
    eixo.plot(*curvas["2000-2013"], linestyle="--", color="#ff7f0e", label="Ajuste exponencial 2000–2013")
    eixo.plot(*curvas["2014-2025"], linestyle="--", color="#2ca02c", label="Ajuste exponencial 2014–2025")
    eixo.axvline(x=2014, linestyle=":", color="gray", label="Marco de 2014")
    eixo.set_xlabel("Ano")
    eixo.set_xticks(range(2000, 2026, 2))
    eixo.tick_params(axis="x", labelrotation=45)
    eixo.grid(True, alpha=0.3)

eixos[0].set_title("Escala comum")
eixos[0].set_ylabel("Quantidade de publicações")
eixos[0].legend(loc="upper left")

# Na escala log, a curva exponencial vira reta. Anos com zero (2004 e 2008) ficam em branco.
eixos[1].set_yscale("log")
eixos[1].set_title("Escala logarítmica (exponencial vira reta)")
eixos[1].set_ylabel("Quantidade de publicações (escala log)")

p2 = resultados[1]
fig.suptitle(
    "Evolução das publicações (artigos e revisões, 2000–2025) — "
    f"após 2014: +{p2['Crescimento_anual_pct']:.0f}% ao ano, "
    f"dobra a cada {p2['Tempo_duplicacao_anos']:.1f} anos".replace(".", ",")
)
fig.tight_layout()

saida_grafico = pasta / "resultados" / "grafico_crescimento.png"
fig.savefig(saida_grafico, dpi=300)
plt.close(fig)

# Salva os resultados das tendências
saida_tendencias = pasta / "resultados" / "tendencias_crescimento.csv"
pd.DataFrame(resultados).to_csv(
    saida_tendencias,
    index=False,
    sep=";",
    encoding="utf-8-sig"
)

print("\nArquivos salvos na pasta resultados:")
print("- grafico_crescimento.png")
print("- tendencias_crescimento.csv")
