#Teste - IMPACTO CIENTÍFICO


import pandas as pd
from pathlib import Path

# Localiza as pastas do projeto
pasta = Path(__file__).resolve().parent.parent

# Lê os dados exportados da Scopus
arquivo = pasta / "dados" / "dadosexportados.csv"
df = pd.read_csv(arquivo)

# Garante que ano e citações sejam valores numéricos
df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
df["Cited by"] = pd.to_numeric(df["Cited by"], errors="coerce")

# Remove registros sem ano ou número de citações
df = df.dropna(subset=["Year", "Cited by"]).copy()

# Calcula a taxa anualizada de citações
df["Impacto anualizado"] = (
    df["Cited by"] / (2026 - df["Year"])
)

# Ii= Ci/ (2026 - Ai), sendo:
    # Ii = impacto anualizado do artigo i;
    # Ci = número de citações do artigo i;
    # Ai = ano de publicação do artigo i;


# Organiza os artigos do maior para o menor impacto
df = df.sort_values(
    by="Impacto anualizado",
    ascending=False
)

# Seleciona as informações principais
resultado = df[
    [
        "Authors",
        "Title",
        "Year",
        "Cited by",
        "Impacto anualizado"
    ]
].copy()

# Arredonda o impacto anualizado para duas casas decimais
resultado["Impacto anualizado"] = resultado["Impacto anualizado"].round(2)

# Exibe os 20 artigos com maior impacto anualizado
print("\n20 ARTIGOS COM MAIOR IMPACTO ANUALIZADO")
print(resultado.head(20).to_string(index=False))

# Calcula estatísticas gerais
print("\nESTATÍSTICAS GERAIS")
print("Total de artigos analisados:", len(resultado))
print(
    "Média de impacto anualizado:",
    round(resultado["Impacto anualizado"].mean(), 2)
)
print(
    "Mediana de impacto anualizado:",
    round(resultado["Impacto anualizado"].median(), 2)
)

# Cria a pasta de resultados, caso ainda não exista
saida = pasta / "resultados"
saida.mkdir(parents=True, exist_ok=True)

# Salva todos os artigos com seus impactos
arquivo_completo = saida / "impacto_por_artigo.csv"
resultado.to_csv(
    arquivo_completo,
    index=False,
    sep=";",
    encoding="utf-8-sig"
)

# Salva somente os 20 artigos com maior impacto
arquivo_top20 = saida / "top20_impacto.csv"
resultado.head(20).to_csv(
    arquivo_top20,
    index=False,
    sep=";",
    encoding="utf-8-sig"
)

print("\nArquivos salvos na pasta resultados:")
print("- impacto_por_artigo.csv")
print("- top20_impacto.csv")


#Hakuna Matata