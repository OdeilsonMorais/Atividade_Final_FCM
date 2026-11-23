#Teste - IMPACTO CIENTÍFICO


import pandas as pd
from pathlib import Path

# Localiza as pastas e o arquivo CSV
pasta = Path(__file__).resolve().parent.parent
arquivo = pasta.parent.parent / "dados" / "artigos_scopus_G.csv"

# Lê os dados exportados da Scopus
df = pd.read_csv(arquivo, encoding="utf-8-sig")

# Garante que ano e citações sejam valores numéricos
df["ano"] = pd.to_numeric(df["ano"], errors="coerce")
df["citacoes"] = pd.to_numeric(df["citacoes"], errors="coerce")

# Remove registros sem ano ou número de citações
df = df.dropna(subset=["ano", "citacoes"]).copy()

# Calcula a taxa anualizada de citações
df["Impacto anualizado"] = (
    df["citacoes"] / (2026 - df["ano"])
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
        "autores",
        "titulo",
        "ano",
        "citacoes",
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