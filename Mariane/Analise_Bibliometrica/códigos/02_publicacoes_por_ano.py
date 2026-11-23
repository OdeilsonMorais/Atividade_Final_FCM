#Teste
#calcular a média de citações por ano de cada publicação.


import pandas as pd
from pathlib import Path

# Localiza as pastas e o arquivo CSV
pasta = Path(__file__).resolve().parent.parent
arquivo = pasta.parent.parent / "dados" / "artigos_scopus_G.csv"

# Lê os dados exportados da Scopus
df = pd.read_csv(arquivo, encoding="utf-8-sig")

# Conta as publicações por ano
publicacoes = df.groupby("ano").size()

# Cria todos os anos de 2000 a 2025
todos_os_anos = range(2000, 2026)

# Preenche os anos sem publicações com zero
publicacoes = publicacoes.reindex(todos_os_anos, fill_value=0)

# Organiza os dados em uma tabela
publicacoes = publicacoes.reset_index()
publicacoes.columns = ["Ano", "Quantidade"]

# Exibe os resultados no terminal
print("\nPUBLICAÇÕES POR ANO")
print(publicacoes.to_string(index=False))

# Calcula o total de publicações
print("\nTotal de publicações:", publicacoes["Quantidade"].sum())

# Salva o arquivo em formato CSV compatível com Excel em português
saida = pasta / "resultados" / "publicacoes_por_ano.csv"

publicacoes.to_csv(
    saida,
    index=False,
    sep=";",
    encoding="utf-8-sig"
)

print("\nArquivo salvo em:", saida)
