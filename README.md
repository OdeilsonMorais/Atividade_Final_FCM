# Análise bibliométrica: resfriamento radiativo passivo (2000–2025)

Trabalho final da disciplina de FCM.

O **resfriamento radiativo passivo** é uma forma de climatização que não gasta energia. A superfície reflete a radiação solar e emite radiação térmica para o espaço pela janela atmosférica do infravermelho (8–13 µm). O interesse pela área cresceu depois de 2014, ano da primeira demonstração de resfriamento abaixo da temperatura ambiente sob luz solar direta.

Este trabalho analisa a produção científica sobre o tema entre 2000 e 2025. Os dados vêm da base **Scopus** e são processados em **Python**.

## Perguntas do trabalho

- Marcos científicos, como o de 2014, mudam o ritmo de crescimento da área?
- Os países que mais publicam são também os de maior impacto e os que mais declaram financiamento?

## Divisão do trabalho

| Pasta | Responsável | Análise |
|---|---|---|
| — | Julio | Evolução temporal do número de publicações, com ajustes lineares separados antes e depois de 2014 |
| [`Odeilson/`](Odeilson/) | Odeilson | Coleta dos dados pela API da Scopus e distribuição geográfica da produção em dois períodos |
| [`Mariane/`](Mariane/) | Mariane | Crescimento da área e impacto (citações normalizadas pelo tempo desde a publicação) |
| [`Gabriel/`](Gabriel/) | Gabriel | Fração de artigos com financiamento declarado, por país |

## Estrutura do repositório

```
Gabriel/                    notebook (Colab) e resultados da análise de financiamento
Mariane/
  Analise_Bibliometrica/
    códigos/                scripts 01–04 (conferência, publicações por ano, crescimento, impacto)
    dados/                  exportação da Scopus usada nas análises
    resultados/             tabelas, gráficos e textos de interpretação (leia-me/)
Odeilson/
  coleta/
    coleta_scopus.py        baixa os artigos pela API da Scopus
    teste_termos.py         compara diferentes conjuntos de termos de busca
    dados/                  CSVs coletados (buscas A e G) e resultados dos testes de termos
  analise/
    analise.py              publicações por país, antes e depois de 2014
    mapa.py                 mapa interativo (HTML) com o número de publicações por país
    resultados/             tabelas por país e período
    figuras/                gráficos e mapas
Planejamento.docx           planejamento feito em reunião em 17/11/2026
```

## Parte do Odeilson: coleta e distribuição geográfica

### Buscas na Scopus

Foram feitas duas buscas em título, resumo e palavras-chave (`TITLE-ABS-KEY`), de 2000 a 2025:

- **Busca A:** `"passive radiative cooling"`, `"daytime radiative cooling"`, `"radiative sky cooling"` e `"sub-ambient radiative cooling"`. Retornou 1658 registros, mas só 15 são anteriores a 2014. Esses termos passaram a ser usados justamente depois do marco de 2014, então a busca subestima a produção antiga.
- **Busca G:** os termos da A mais termos usados antes de 2014, como `"nocturnal radiative cooling"`, `"night sky radiation"`, `"sky radiator"`, `"radiative cooler"` e `"radiative cooling material/coating/film"`. Ficam excluídos os registros que citam termos típicos de climatologia e astrofísica (`"clear-sky"`, `"cloud feedback"`, `galax*`, `telescope`, `satellite`, `plasma`, `aerosol*` etc.). Retornou 2154 registros, 50 deles anteriores a 2014.

A comparação entre as buscas está em `Odeilson/coleta/dados/teste_termos*.tsv`, com amostras de títulos em `teste_termos*_amostras.txt`.

### Como reproduzir

Requisitos: Python 3.12 e as bibliotecas abaixo.

```powershell
pip install requests pandas matplotlib plotly pycountry
```

**1. Coleta (opcional, os CSVs já estão no repositório).** Precisa de uma chave da API da Elsevier (dev.elsevier.com) e de acesso institucional (rede ou VPN da universidade). Sem esse acesso, a API não devolve o financiamento e traz só o país da primeira afiliação.

```powershell
$env:SCOPUS_API_KEY = "sua_chave"
python Odeilson/coleta/coleta_scopus.py --busca G
```

**2. Análise e mapa.** Use `--busca A` ou `--busca G`. Sem a opção, os scripts usam a busca A.

```powershell
python Odeilson/analise/analise.py --busca G
python Odeilson/analise/mapa.py --busca G
```

O mapa é gerado em `Odeilson/analise/figuras/mapa_publicacoes_G.html`. Abra no navegador e passe o cursor sobre um país para ver o número de publicações. Os botões alternam entre o total e os períodos 2000–2013 e 2014–2025. O arquivo precisa de internet para desenhar os contornos dos países.

### Escolhas metodológicas

- Entram só documentos dos tipos *Article* e *Review*.
- **Contagem inteira:** cada país presente nas afiliações conta uma vez por artigo. Por isso as porcentagens de um período somam mais de 100%.
- Hong Kong aparece separado da China, como na Scopus. Para juntar os dois, troque `JUNTAR_HK_CHINA = True` em `analise.py`.

### Principais resultados (busca G)

| Período | Artigos | Países com mais artigos (% dos artigos do período) |
|---|---|---|
| 2000–2013 | 33 | EUA 21%, Japão 15%, China, Irã e Nigéria 9% cada |
| 2014–2025 | 1807 | China 69%, EUA 12%, Hong Kong 8%, Coreia do Sul 6% |

Depois de 2014, a China passa a dominar a produção. Antes de 2014, a produção era pequena e mais espalhada, com presença de países de clima quente que pesquisavam resfriamento noturno. Os registros anteriores a 2014 ainda não foram conferidos manualmente.

## Limitações

- **Cobertura da Scopus:** a base favorece revistas em inglês e de grandes editoras.
- **Termos de busca:** a escolha dos termos afeta o resultado, principalmente antes de 2014, como mostra a comparação entre as buscas A e G.
- **Citações:** são um indicador indireto de qualidade.
- **Dados de 2025:** podem estar incompletos por causa do atraso de indexação.
- **Uso dos dados:** os termos de uso da API da Elsevier restringem a redistribuição dos dados da Scopus.
