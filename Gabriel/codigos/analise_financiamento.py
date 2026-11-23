"""Calcule a fração de artigos e revisões com Funding Details por país."""

import re
from pathlib import Path

import pandas as pd
import pycountry

GABRIEL = Path(__file__).resolve().parents[1]
FONTE = GABRIEL.parent / "Mariane/Analise_Bibliometrica/dados/dadosexportados.csv"
SAIDA = GABRIEL / "resultados"
TIPOS = ("Article", "Review")
PAISES_GRUPO = (
    "China", "United States", "South Korea", "India", "Singapore",
    "Spain", "Italy", "Canada", "Australia", "Taiwan",
)
COLUNAS = [
    "Year", "Document Type", "EID", "DOI", "Affiliations",
    "Authors with affiliations", "Funding Details", "Funding Texts",
]
VAZIOS = {"", "-", "–", "—", "na", "n/a", "n.a.", "nan", "null", "none", "<na>"}
SEM_DECLARACAO = VAZIOS | {"no funding", "no funding declared", "not applicable"}

NOMES_PADRAO = {
    "IRN": "Iran", "KOR": "South Korea", "MAC": "Macao",
    "PRK": "North Korea", "RUS": "Russian Federation", "TUR": "Turkey",
    "TWN": "Taiwan", "USA": "United States", "VNM": "Viet Nam",
}
PAISES = {}
for pais in pycountry.countries:
    nome = NOMES_PADRAO.get(pais.alpha_3, pais.name)
    variantes = (nome, pais.name, getattr(pais, "official_name", None), getattr(pais, "common_name", None))
    for variante in variantes:
        if variante:
            PAISES[variante.casefold()] = nome

PAISES.update({
    "usa": "United States", "u.s.a": "United States", "us": "United States",
    "u.s": "United States", "uk": "United Kingdom", "u.k": "United Kingdom",
    "republic of korea": "South Korea", "korea, republic of": "South Korea",
    "pr china": "China", "p.r. china": "China", "mainland china": "China",
    "hong kong sar": "Hong Kong", "hong kong s.a.r": "Hong Kong",
    "macau": "Macao", "macao sar": "Macao", "macau sar": "Macao",
    "russia": "Russian Federation", "vietnam": "Viet Nam",
})
# Endereço divergente na exportação, conferido no artigo 10.3390/atmos16010095.
CORRECOES_AFILIACAO = {
    ("department of mechanical and industrial engineering, northeastern university, "
     "ma, boston, 02115, thailand"): "United States",
}
LOCALIDADES = {
    "hong kong": "Hong Kong", "hong kong sar": "Hong Kong",
    "hong kong s.a.r": "Hong Kong", "kowloon hong kong": "Hong Kong",
    "kowloon": "Hong Kong", "kowloon tong": "Hong Kong",
    "taiwan": "Taiwan", "macao": "Macao", "macau": "Macao",
    "macao sar": "Macao", "macau sar": "Macao",
}


def normalizar(texto):
    return " ".join(texto.casefold().split())


def presente(serie, vazios=VAZIOS):
    return ~serie.map(normalizar).isin(vazios)


def pais_da_afiliacao(afiliacao):
    endereco = normalizar(afiliacao)
    if endereco in CORRECOES_AFILIACAO:
        return CORRECOES_AFILIACAO[endereco]

    partes = [normalizar(parte).rstrip(".") for parte in afiliacao.split(",")]
    if len(partes) > 1:
        # Reconhece nomes com uma vírgula, como "Korea, Republic of".
        nome_composto = ", ".join(partes[-2:])
        if nome_composto in PAISES:
            return PAISES[nome_composto]

    pais = PAISES.get(partes[-1])
    if pais == "China":
        # Considere componentes do endereço. O nome da instituição, por si só,
        # não localiza um campus (por exemplo, em Shenzhen).
        for local in reversed(partes[-4:-1]):
            if local in LOCALIDADES:
                return LOCALIDADES[local]
    if pais:
        return pais

    # Exportação sem a vírgula entre o código postal e o país.
    final = re.search(r"\b\d{4,6}\s+([^\d]+)$", partes[-1])
    return PAISES.get(final[1]) if final else None


def extrair_paises(campo):
    afiliacoes = [trecho.strip() for trecho in campo.split(";") if trecho.strip()]
    paises = set()
    sem_pais = []
    for afiliacao in afiliacoes:
        pais = pais_da_afiliacao(afiliacao)
        if pais:
            paises.add(pais)
        else:
            sem_pais.append(afiliacao)
    return paises, sem_pais


def selecionar(dados):
    ano = pd.to_numeric(dados["Year"], errors="coerce")
    ano_valido = ano.between(2000, 2025) & ano.mod(1).eq(0)
    tipo_valido = dados["Document Type"].isin(TIPOS)
    selecionados = dados.loc[ano_valido & tipo_valido].copy()
    selecionados["ano"] = ano.loc[selecionados.index].astype(int)
    print(f"Registros originais: {len(dados)}")
    print(f"Fora do recorte ou com ano inválido: {(~ano_valido).sum()}")
    print(f"Excluídos por tipo no recorte de anos: {(ano_valido & ~tipo_valido).sum()}")
    print(f"Após os filtros: {len(selecionados)} ({selecionados['Document Type'].value_counts().to_dict()})")
    return selecionados


def identificar_documentos(dados):
    eid = dados["EID"].str.casefold().where(presente(dados["EID"]), "")
    doi = dados["DOI"].str.casefold().str.replace(
        r"^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)", "", regex=True,
    ).str.strip()
    doi = doi.where(presente(doi), "")
    pares = pd.DataFrame({"doi": doi, "eid": eid})
    eids_por_doi = pares.query("doi != '' and eid != ''").groupby("doi")["eid"].agg(set)
    doi_univoco = {chave: next(iter(eids)) for chave, eids in eids_por_doi.items() if len(eids) == 1}

    chaves = []
    for linha, identificador, identificador_doi in zip(dados.index, eid, doi):
        if identificador:
            chave = f"EID {identificador}"
        elif identificador_doi in doi_univoco:
            chave = f"EID {doi_univoco[identificador_doi]}"
        elif identificador_doi and identificador_doi not in eids_por_doi:
            chave = f"DOI {identificador_doi}"
        else:
            chave = f"linha de dados {linha + 1}"
        chaves.append(chave)
    print(f"Sem EID: {eid.eq('').sum()}; sem DOI: {doi.eq('').sum()}")
    print(f"DOIs com mais de um EID: {sum(len(eids) > 1 for eids in eids_por_doi)}")
    print(f"Registros redundantes que serão consolidados: {len(chaves) - len(set(chaves))}")
    return chaves


def calcular(dados):
    dados["documento"] = identificar_documentos(dados)
    detalhes = dados["Funding Details"]
    dados["financiamento"] = presente(detalhes, SEM_DECLARACAO) & detalhes.str.contains(r"[^\W_]", regex=True)
    texto = presente(dados["Funding Texts"])
    print(f"Funding Details sem Funding Texts: {(dados['financiamento'] & ~texto).sum()}")
    print(f"Funding Texts sem Funding Details: {(texto & ~dados['financiamento']).sum()}")

    paises_por_linha = []
    recuperados = 0
    parciais = set()
    for chave, afiliacoes, autores in zip(
        dados["documento"], dados["Affiliations"], dados["Authors with affiliations"]
    ):
        paises, sem_pais = extrair_paises(afiliacoes)
        if not paises or sem_pais:
            adicionais, _ = extrair_paises(autores)
            recuperados += bool(adicionais - paises)
            paises.update(adicionais)
        if sem_pais:
            parciais.add(chave)
        paises_por_linha.append(paises)
    dados["paises"] = paises_por_linha
    print(f"Linhas com países acrescentados pelo campo de autores: {recuperados}")
    print(f"Documentos com fragmentos de afiliação sem país reconhecido: {sorted(parciais)}")

    # Um mesmo documento pode combinar metadados de registros redundantes.
    grupos = dados.groupby("documento")
    conflitos = grupos[["ano", "Document Type"]].nunique().gt(1).any(axis=1)
    if conflitos.any():
        raise ValueError(f"Identificadores repetidos com ano ou tipo divergente: {list(conflitos[conflitos].index)}")
    documentos = grupos.agg(
        financiamento=("financiamento", "any"),
        paises=("paises", lambda conjuntos: sorted(set().union(*conjuntos))),
    )
    sem_pais = documentos["paises"].str.len().eq(0)
    print(f"Documentos únicos: {len(documentos)}; com financiamento declarado: {documentos['financiamento'].sum()}")
    print(f"Sem país identificado ({sem_pais.sum()}): {list(documentos.index[sem_pais])}")

    por_pais = documentos.explode("paises").dropna(subset=["paises"]).reset_index()
    if por_pais.duplicated(["documento", "paises"]).any():
        raise ValueError("Há contagem repetida do mesmo documento para um país.")
    resultado = por_pais.groupby("paises").agg(
        total_artigos=("documento", "size"),
        artigos_com_financiamento=("financiamento", "sum"),
    ).rename_axis("pais").reset_index()
    total = resultado["total_artigos"]
    financiados = resultado["artigos_com_financiamento"]
    resultado["percentual_financiamento"] = 100 * financiados / total
    if (financiados > total).any() or not resultado["percentual_financiamento"].between(0, 100).all():
        raise ValueError("Há contagens ou percentuais de financiamento inválidos.")
    return resultado.sort_values(["total_artigos", "pais"], ascending=[False, True])


def main():
    dados = pd.read_csv(FONTE, usecols=COLUNAS, dtype=str, keep_default_na=False, encoding="utf-8-sig")
    dados = dados.apply(lambda coluna: coluna.str.strip())
    resultado = calcular(selecionar(dados))
    top10 = resultado.set_index("pais").reindex(PAISES_GRUPO).reset_index()
    ausentes = top10.loc[top10["total_artigos"].isna(), "pais"].tolist()
    if ausentes:
        print(f"Países do grupo ausentes na base (campos numéricos vazios): {ausentes}")
    for coluna in ("total_artigos", "artigos_com_financiamento"):
        top10[coluna] = top10[coluna].astype("Int64")
    SAIDA.mkdir(exist_ok=True)
    resultado.to_csv(SAIDA / "financiamento_por_pais.csv", index=False, float_format="%.6f")
    top10.to_csv(SAIDA / "financiamento_top10_grupo.csv", index=False, float_format="%.6f")
    print(f"Países e territórios identificados: {len(resultado)}")


if __name__ == "__main__":
    main()
