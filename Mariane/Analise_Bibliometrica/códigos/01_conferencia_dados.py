#Teste
#Esse primeiro código não altera os dados. Apenas verifica se conseguimos ler a planilha e identificar as informações necessárias.


#Pandas é uma biblioteca do Python criada para trabalhar com dados, principalmente tabelas e planilhas.

#python -m pip install pandas

import pandas as pd
from pathlib import Path

# Localização dos arquivos
pasta = Path(__file__).resolve().parent.parent
arquivo = pasta.parent.parent / "dados" / "artigos_scopus_G.csv"

# Leitura dos dados
df = pd.read_csv(arquivo, encoding="utf-8-sig")

# Conferência inicial
print("Quantidade de documentos:", len(df))

print("\nColunas disponíveis:")
print(df.columns.tolist())

print("\nPeríodo das publicações:")
print(df["ano"].min(), "-", df["ano"].max())

print("\nPrimeiros artigos:")
print(df[["titulo", "ano", "citacoes"]].head())

print("\nDados ausentes:")
print(df[["ano", "citacoes", "autores", "paises", "fund_sponsor"]].isna().sum())
