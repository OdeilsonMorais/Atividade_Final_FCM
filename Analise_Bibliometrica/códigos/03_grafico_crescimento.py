#Teste - INCLINAÇÃO DAS RETAS DE TENDÊNCIA E R²
# y=ax+b
    # y = quantidade estimada de publicações;
    # x = ano;
    # a = inclinação da reta;
    # b = ponto de interseção com o eixo y.



import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Localiza as pastas
pasta = Path(__file__).resolve().parent.parent

# Lê a tabela de publicações por ano
arquivo = pasta / "resultados" / "publicacoes_por_ano.csv"
df = pd.read_csv(arquivo, sep=";")

# Organiza os dados
anos = df["Ano"].to_numpy()
quantidades = df["Quantidade"].to_numpy()

# Separa os períodos
periodo_1 = df[(df["Ano"] >= 2000) & (df["Ano"] <= 2013)]
periodo_2 = df[(df["Ano"] >= 2014) & (df["Ano"] <= 2025)]

# Calcula as retas de tendência
coef_1 = np.polyfit(periodo_1["Ano"], periodo_1["Quantidade"], 1)
coef_2 = np.polyfit(periodo_2["Ano"], periodo_2["Quantidade"], 1)

# Calcula os valores estimados pelas retas
reta_1 = np.polyval(coef_1, periodo_1["Ano"])
reta_2 = np.polyval(coef_2, periodo_2["Ano"])

# Calcula o R² de cada período
def calcular_r2(observado, estimado):
    soma_residuos = np.sum((observado - estimado) ** 2)
    soma_total = np.sum((observado - np.mean(observado)) ** 2)
    return 1 - (soma_residuos / soma_total)

r2_1 = calcular_r2(periodo_1["Quantidade"].to_numpy(), reta_1)
r2_2 = calcular_r2(periodo_2["Quantidade"].to_numpy(), reta_2)

# Mostra os resultados no terminal
print("\nANÁLISE DO CRESCIMENTO DAS PUBLICAÇÕES")

print("\nPeríodo de 2000 a 2013:")
print(f"Inclinação da reta: {coef_1[0]:.2f} publicações por ano")
print(f"R²: {r2_1:.4f}")

print("\nPeríodo de 2014 a 2025:")
print(f"Inclinação da reta: {coef_2[0]:.2f} publicações por ano")
print(f"R²: {r2_2:.4f}")

# Cria o gráfico
plt.figure(figsize=(12, 6))

# Publicações observadas
plt.plot(
    anos,
    quantidades,
    marker="o",
    label="Publicações por ano"
)

# Retas de tendência
plt.plot(
    periodo_1["Ano"],
    reta_1,
    linestyle="--",
    label="Tendência 2000–2013"
)

plt.plot(
    periodo_2["Ano"],
    reta_2,
    linestyle="--",
    label="Tendência 2014–2025"
)

# Identifica o ano de 2014
plt.axvline(x=2014, linestyle=":", label="Marco de 2014")

# Configurações do gráfico
plt.title("Evolução das publicações científicas (2000–2025)")
plt.xlabel("Ano")
plt.ylabel("Quantidade de publicações")
plt.xticks(range(2000, 2026, 2))
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()

# Salva o gráfico
saida_grafico = pasta / "resultados" / "grafico_crescimento.png"
plt.savefig(saida_grafico, dpi=300)
plt.show()

# Salva os resultados das tendências
resumo = pd.DataFrame({
    "Periodo": ["2000-2013", "2014-2025"],
    "Inclinacao": [coef_1[0], coef_2[0]],
    "R2": [r2_1, r2_2]
})

saida_tendencias = pasta / "resultados" / "tendencias_crescimento.csv"
resumo.to_csv(
    saida_tendencias,
    index=False,
    sep=";",
    encoding="utf-8-sig"
)

print("\nArquivos salvos na pasta resultados:")
print("- grafico_crescimento.png")
print("- tendencias_crescimento.csv")
