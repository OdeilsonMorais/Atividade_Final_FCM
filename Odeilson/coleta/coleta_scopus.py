"""
Coleta de artigos da Scopus Search API para a análise bibliométrica
sobre resfriamento radiativo passivo (2000-2025).

Uso:
    $env:SCOPUS_API_KEY = "sua_chave"          # https://dev.elsevier.com
    python coleta_scopus.py --contar            # só mostra quantos resultados a busca retorna
    python coleta_scopus.py                     # baixa tudo -> dados/artigos_scopus.csv
"""

import argparse
import csv
import json
import os
import sys
import time
from pathlib import Path

import requests

URL = "https://api.elsevier.com/content/search/scopus"
DADOS = Path(__file__).resolve().parent.parent.parent / "dados"

TERMOS = [
    "passive radiative cooling",
    "daytime radiative cooling",
    "radiative sky cooling",
    "sub-ambient radiative cooling",
]
ANO_INI, ANO_FIM = 2000, 2025

ANOS = f" AND PUBYEAR > {ANO_INI - 1} AND PUBYEAR < {ANO_FIM + 1}"
QUERY_PADRAO = "TITLE-ABS-KEY(" + " OR ".join(f'"{t}"' for t in TERMOS) + ")" + ANOS

# Busca G (ver teste_termos.py): termos atuais + termos antigos, sem ruído de
# climatologia/astrofísica.
TERMOS_ANTIGOS = [
    "nocturnal radiative cooling", "night sky radiation", "sky radiator",
    "radiative cooler", "radiative cooling material", "radiative cooling coating",
    "radiative cooling film",
]
RUIDO = ('"clear-sky" OR "cloud feedback" OR "boundary layer" OR galax* OR '
         'telescope OR spacecraft OR satellite OR plasma OR aerosol*')
QUERY_G = ("(TITLE-ABS-KEY(" + " OR ".join(f'"{t}"' for t in TERMOS + TERMOS_ANTIGOS) + ")"
           f" AND NOT TITLE-ABS-KEY({RUIDO}))" + ANOS)
# Os registros que a busca G descarta, para triagem manual
QUERY_G_EXCLUIDOS = ("(TITLE-ABS-KEY(" + " OR ".join(f'"{t}"' for t in TERMOS + TERMOS_ANTIGOS) + ")"
                     f" AND TITLE-ABS-KEY({RUIDO}))" + ANOS)

BUSCAS = {"A": QUERY_PADRAO, "G": QUERY_G, "G_excluidos": QUERY_G_EXCLUIDOS}

COLUNAS = [
    "eid", "doi", "titulo", "autores", "ano", "data_capa", "revista", "tipo_doc",
    "citacoes", "paises", "n_paises", "fund_sponsor", "fund_acr", "fund_no",
    "palavras_chave_autor",
]


def cabecalhos():
    chave = os.environ.get("SCOPUS_API_KEY")
    if not chave:
        sys.exit("Defina a variável de ambiente SCOPUS_API_KEY.")
    h = {"X-ELS-APIKey": chave, "Accept": "application/json"}
    token = os.environ.get("SCOPUS_INSTTOKEN")
    if token:
        h["X-ELS-Insttoken"] = token
    return h


def requisitar(params, h, tentativas=5):
    for i in range(tentativas):
        r = requests.get(URL, params=params, headers=h, timeout=60)
        if r.status_code == 429:  # limite de taxa: espera e tenta de novo
            time.sleep(2 ** i)
            continue
        return r
    r.raise_for_status()
    return r


def extrair(e):
    afils = e.get("affiliation") or []
    paises = sorted({a.get("affiliation-country") for a in afils if a.get("affiliation-country")})
    autores_raw = e.get("author") or []
    if isinstance(autores_raw, dict):
        autores_raw = [autores_raw]
    autores = "; ".join(a.get("authname", "") for a in autores_raw if a.get("authname"))
    if not autores:
        autores = e.get("dc:creator", "")
    data = e.get("prism:coverDate", "")
    return {
        "eid": e.get("eid", ""),
        "doi": e.get("prism:doi", ""),
        "titulo": e.get("dc:title", ""),
        "autores": autores,
        "ano": data[:4],
        "data_capa": data,
        "revista": e.get("prism:publicationName", ""),
        "tipo_doc": e.get("subtypeDescription", ""),
        "citacoes": e.get("citedby-count", ""),
        "paises": "; ".join(paises),
        "n_paises": len(paises),
        "fund_sponsor": e.get("fund-sponsor", ""),
        "fund_acr": e.get("fund-acr", ""),
        "fund_no": e.get("fund-no", ""),
        "palavras_chave_autor": e.get("authkeywords", ""),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--busca", choices=BUSCAS, default="A",
                    help="busca pré-definida (A = original, G = ampliada)")
    ap.add_argument("--query", help="query livre (substitui --busca)")
    ap.add_argument("--contar", action="store_true", help="só conta os resultados")
    ap.add_argument("--saida", help="CSV de saída (padrão: dados/artigos_scopus[_BUSCA].csv)")
    args = ap.parse_args()
    args.query = args.query or BUSCAS[args.busca]
    if not args.saida:
        nome = "artigos_scopus.csv" if args.busca == "A" else f"artigos_scopus_{args.busca}.csv"
        args.saida = DADOS / nome
    h = cabecalhos()

    print("Query:", args.query)
    r = requisitar({"query": args.query, "count": 1}, h)
    r.raise_for_status()
    total = int(r.json()["search-results"]["opensearch:totalResults"])
    print(f"Total de resultados: {total}")
    if args.contar:
        return

    view = "COMPLETE"
    teste = requisitar({"query": args.query, "count": 1, "view": view}, h)
    if teste.status_code in (401, 403):
        print("Aviso: view COMPLETE negada (sem acesso institucional). "
              "Usando STANDARD: sem dados de financiamento e só a 1ª afiliação.")
        view = "STANDARD"

    saida = Path(args.saida)
    bruto = saida.parent / ("bruto" if saida.stem == "artigos_scopus" else f"bruto_{saida.stem}")
    bruto.mkdir(parents=True, exist_ok=True)

    # Paginação por deslocamento (start): o cursor exige acesso de assinante.
    # Funciona até 5000 resultados, o que basta para esta busca.
    if total > 5000:
        sys.exit("Mais de 5000 resultados: divida a busca por intervalos de anos.")

    linhas, pagina = [], 0
    for inicio in range(0, total, 25):
        r = requisitar({"query": args.query, "view": view, "count": 25,
                        "start": inicio}, h)
        if not r.ok:
            sys.exit(f"\nErro {r.status_code} em start={inicio}: {r.text[:500]}")
        res = r.json()["search-results"]
        entradas = [e for e in res.get("entry", []) if "error" not in e]
        if not entradas:
            break
        (bruto / f"pagina_{pagina:04d}.json").write_text(
            json.dumps(entradas, ensure_ascii=False), encoding="utf-8")
        linhas.extend(extrair(e) for e in entradas)
        pagina += 1
        print(f"\r{len(linhas)}/{total}", end="", flush=True)
        time.sleep(0.15)

    with saida.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=COLUNAS)
        w.writeheader()
        w.writerows(linhas)
    print(f"\n{len(linhas)} registros salvos em {saida} (view {view}).")


if __name__ == "__main__":
    main()
