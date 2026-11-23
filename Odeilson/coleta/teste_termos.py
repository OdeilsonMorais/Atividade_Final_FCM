"""
Compara quantos registros diferentes conjuntos de termos retornam na Scopus,
separando antes de 2014 e de 2014 em diante. Usa só contagens (count=1),
gasta pouquíssima cota. Também salva títulos de amostra pré-2014 de cada
busca para conferir se são mesmo sobre resfriamento radiativo terrestre.

Uso: python teste_termos.py   (com SCOPUS_API_KEY definida e na VPN)
"""

import os
import sys
from pathlib import Path

import requests

URL = "https://api.elsevier.com/content/search/scopus"
ANOS = "PUBYEAR > 1999 AND PUBYEAR < 2026"

ATUAL = ('"passive radiative cooling" OR "daytime radiative cooling" OR '
         '"radiative sky cooling" OR "sub-ambient radiative cooling"')

ANTIGOS = ('"nocturnal radiative cooling" OR "night sky radiation" OR '
           '"sky radiator" OR "sky radiative cooling" OR "radiative cooler" OR '
           '"radiative cooling material" OR "radiative cooling coating" OR '
           '"radiative cooling film"')

# "radiative cooling" sozinho pega astrofísica e plasma; exige contexto terrestre
CONTEXTO = ('"radiative cooling" AND ("atmospheric window" OR "sky" OR '
            '"sub-ambient" OR "building" OR "thermal emitter" OR "solar reflect*" '
            'OR "8-13" OR "infrared emissiv*")')

ANTIGOS_SEM_SKY = ANTIGOS.replace('"sky radiative cooling" OR ', '')
RUIDO = ('"clear-sky" OR "cloud feedback" OR "boundary layer" OR galax* OR '
         'telescope OR spacecraft OR satellite OR plasma OR aerosol*')

BUSCAS = {
    "F_atual+antigos_sem_sky": f"TITLE-ABS-KEY({ATUAL} OR {ANTIGOS_SEM_SKY})",
    "G_F_sem_ruido": f"TITLE-ABS-KEY({ATUAL} OR {ANTIGOS_SEM_SKY}) AND NOT TITLE-ABS-KEY({RUIDO})",
}
BUSCAS_ANTERIORES = {
    "A_atual": f"TITLE-ABS-KEY({ATUAL})",
    "B_termos_antigos": f"TITLE-ABS-KEY({ANTIGOS})",
    "C_rc_com_contexto": f"TITLE-ABS-KEY({CONTEXTO})",
    "D_atual+antigos": f"TITLE-ABS-KEY({ATUAL} OR {ANTIGOS})",
    "E_atual+antigos+contexto": f"TITLE-ABS-KEY({ATUAL} OR {ANTIGOS}) OR TITLE-ABS-KEY({CONTEXTO})",
}

h = {"X-ELS-APIKey": os.environ.get("SCOPUS_API_KEY", ""), "Accept": "application/json"}
if not h["X-ELS-APIKey"]:
    sys.exit("Defina SCOPUS_API_KEY.")
if os.environ.get("SCOPUS_INSTTOKEN"):
    h["X-ELS-Insttoken"] = os.environ["SCOPUS_INSTTOKEN"]


def buscar(q, n=1, sort=None):
    p = {"query": q, "count": n}
    if sort:
        p["sort"] = sort
    r = requests.get(URL, params=p, headers=h, timeout=60)
    if not r.ok:
        sys.exit(f"Erro {r.status_code}: {r.text[:300]}")
    return r.json()["search-results"]


def total(q):
    return int(buscar(q)["opensearch:totalResults"])


linhas = []
amostras = []
print(f"{'busca':28s} {'total':>7s} {'<2014':>7s} {'>=2014':>7s}")
for nome, q in BUSCAS.items():
    tot = total(f"({q}) AND {ANOS}")
    pre = total(f"({q}) AND PUBYEAR > 1999 AND PUBYEAR < 2014")
    print(f"{nome:28s} {tot:7d} {pre:7d} {tot - pre:7d}")
    linhas.append(f"{nome}\t{tot}\t{pre}\t{tot - pre}\t{q}")
    res = buscar(f"({q}) AND PUBYEAR > 1999 AND PUBYEAR < 2014", n=25, sort="-citedby-count")
    amostras.append(f"\n=== {nome} (pré-2014, 25 mais citados) ===")
    for e in res.get("entry", []):
        if "error" in e:
            continue
        amostras.append(f"{e.get('prism:coverDate', '')[:4]}  {e.get('citedby-count', '')}  "
                        f"{e.get('dc:title', '')}  |  {e.get('prism:publicationName', '')}")

DADOS = Path(__file__).resolve().parent / "dados"
DADOS.mkdir(exist_ok=True)
(DADOS / "teste_termos2.tsv").write_text(
    "busca\ttotal\tpre2014\tpos2014\tquery\n" + "\n".join(linhas), encoding="utf-8")
(DADOS / "teste_termos2_amostras.txt").write_text("\n".join(amostras), encoding="utf-8")
print(f"\nSalvo em {DADOS / 'teste_termos2.tsv'} e {DADOS / 'teste_termos2_amostras.txt'}")
