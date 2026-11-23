"""
Distribuição geográfica da produção sobre resfriamento radiativo passivo
(Scopus, 2000-2025), em dois períodos separados pelo marco de 2014.

Lê os CSVs da pasta ../coleta/dados.

Uso:
    python analise.py             # busca A
    python analise.py --busca G   # busca G

Saídas: resultados/2_paises_por_periodo[_G].csv e figuras/2_paises_por_periodo[_G].png

Escolhas (ajuste as constantes abaixo se o grupo decidir diferente):
- Tipos de documento: Article e Review.
- Marco: 2014. Períodos: 2000-2013 e 2014-2025.
- Contagem inteira: cada país presente nas afiliações conta 1 vez por artigo
  (por isso as porcentagens de um período somam mais de 100%).
- Hong Kong mantido separado da China, como na Scopus.
"""

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

TIPOS = ["Article", "Review"]
MARCO = 2014
ANO_INI, ANO_FIM = 2000, 2025
JUNTAR_HK_CHINA = False
TOP = 10

BASE = Path(__file__).resolve().parent
DADOS = BASE.parent / "coleta" / "dados"

ap = argparse.ArgumentParser()
ap.add_argument("--busca", default="A", help="A (original) ou G (ampliada)")
args = ap.parse_args()
args.sufixo = "" if args.busca == "A" else f"_{args.busca}"
arq = DADOS / f"artigos_scopus{args.sufixo}.csv"

R = BASE / "resultados"; R.mkdir(exist_ok=True)
F = BASE / "figuras"; F.mkdir(exist_ok=True)

df = pd.read_csv(arq, encoding="utf-8-sig")
n0 = len(df)
df = df[df["tipo_doc"].isin(TIPOS)].copy()
df["ano"] = df["ano"].astype(int)
df["paises"] = df["paises"].fillna("")
if JUNTAR_HK_CHINA:
    df["paises"] = df["paises"].str.replace("Hong Kong", "China")
df["lista_paises"] = df["paises"].apply(lambda s: sorted({p.strip() for p in s.split(";") if p.strip()}))
periodos = [f"{ANO_INI}-{MARCO - 1}", f"{MARCO}-{ANO_FIM}"]
df["periodo"] = np.where(df["ano"] < MARCO, periodos[0], periodos[1])

print(f"Registros: {n0} no CSV, {len(df)} após filtrar tipos {TIPOS}")
print(f"Sem país: {(df['lista_paises'].str.len() == 0).sum()}")

# Uma linha por (artigo, país)
ap_ = df.explode("lista_paises").dropna(subset=["lista_paises"]).rename(columns={"lista_paises": "pais"})

geo = ap_.groupby(["pais", "periodo"]).size().unstack(fill_value=0).reindex(columns=periodos, fill_value=0)
geo["total"] = geo.sum(axis=1)
n_per = df["periodo"].value_counts()
for c in periodos:
    geo[f"{c} (%)"] = 100 * geo[c] / n_per.get(c, 1)
geo = geo.sort_values("total", ascending=False)
geo.to_csv(R / f"2_paises_por_periodo{args.sufixo}.csv", index_label="pais")

print("\nDISTRIBUIÇÃO GEOGRÁFICA — % dos artigos do período em que o país aparece")
for p in periodos:
    n = n_per.get(p, 0)
    top = geo[p].sort_values(ascending=False).head(TOP)
    print(f"  {p} ({n} artigos): " + ", ".join(f"{k} {v} ({100 * v / n:.0f}%)" for k, v in top.items() if v > 0))

fig, axs = plt.subplots(1, 2, figsize=(11, 5))
for ax, p in zip(axs, periodos):
    n = n_per.get(p, 0)
    top = (100 * geo[p] / max(n, 1)).sort_values(ascending=False).head(TOP)[::-1]
    top = top[top > 0]
    ax.barh(top.index, top.values, color="#4a7")
    ax.set_title(f"{p} (n = {n})"); ax.set_xlabel("% dos artigos do período")
fig.suptitle("Países com mais artigos, por período (contagem inteira)")
fig.tight_layout(); fig.savefig(F / f"2_paises_por_periodo{args.sufixo}.png", dpi=200); plt.close(fig)

print(f"\nSalvo em analise/resultados/2_paises_por_periodo{args.sufixo}.csv e analise/figuras/2_paises_por_periodo{args.sufixo}.png")
