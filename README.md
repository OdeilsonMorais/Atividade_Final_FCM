# Análise bibliométrica: resfriamento radiativo passivo (2000–2025)

Trabalho final da disciplina de Ferramentas Computacionais de Modelagem (FCM).

O **resfriamento radiativo passivo** é uma forma de climatização que não gasta energia. A superfície reflete a radiação solar e emite radiação térmica para o espaço pela janela atmosférica do infravermelho (8–13 µm). O interesse pela área cresceu depois de 2014, ano da primeira demonstração de resfriamento abaixo da temperatura ambiente sob luz solar direta (Raman et al., *Nature*, 2014).

Este trabalho analisa a produção científica sobre o tema entre 2000 e 2025. Os dados vêm da base **Scopus**, coletados pela API da Elsevier, e são processados em **Python**.

## Perguntas do trabalho

1. Marcos científicos, como o de 2014, mudam o ritmo de crescimento da área?
2. Os países que mais publicam são também os de maior impacto e os que mais declaram financiamento?

## Divisão do trabalho

| Pasta | Responsável | Análise |
|---|---|---|
| [`Odeilson/`](Odeilson/) | Odeilson | Coleta dos dados pela API da Scopus e distribuição geográfica da produção em dois períodos (gráfico e mapa interativo) |
| [`Julio/`](Julio/) | Julio | Evolução temporal normalizada pelo total da Scopus e síntese por país: volume, foco relativo, impacto normalizado e financiamento |
| [`Mariane/`](Mariane/) | Mariane | Ajuste exponencial do crescimento antes e depois de 2014 e impacto por artigo (citações por ano desde a publicação) |
| [`Gabriel/`](Gabriel/) | Gabriel | Fração de artigos com financiamento declarado, por país, em 2000–2025 e 2014–2025 |

## Base de dados

Todas as análises usam a mesma base: **`dados/artigos_scopus_G.csv`**, gerada por `Odeilson/coleta/coleta_scopus.py`.

A busca foi feita em título, resumo e palavras-chave (`TITLE-ABS-KEY`), de 2000 a 2025, com dois grupos de termos:

- **Termos atuais:** `"passive radiative cooling"`, `"daytime radiative cooling"`, `"radiative sky cooling"` e `"sub-ambient radiative cooling"`.
- **Termos usados antes de 2014:** `"nocturnal radiative cooling"`, `"night sky radiation"`, `"sky radiator"`, `"radiative cooler"` e `"radiative cooling material/coating/film"`.

Ficam de fora os registros que citam termos típicos de climatologia e astrofísica (`"clear-sky"`, `"cloud feedback"`, `"boundary layer"`, `galax*`, `telescope`, `spacecraft`, `satellite`, `plasma`, `aerosol*`).

Os termos antigos foram incluídos porque os termos atuais só passaram a ser usados depois do marco de 2014. Só com eles (busca A), a Scopus retorna 1658 registros, dos quais apenas 15 são anteriores a 2014. Com os termos antigos (busca G), são 2154 registros, 50 deles anteriores a 2014.

Das 2154 entradas, as análises usam **1840 documentos dos tipos *Article* e *Review*** (33 de 2000–2013 e 1807 de 2014–2025).

**A base não está neste repositório.** Os termos de uso da Scopus não permitem redistribuir publicamente os registros por artigo. Por isso, `dados/artigos_scopus_G.csv` e as tabelas por artigo da Mariane (`impacto_por_artigo.csv` e `top20_impacto.csv`) estão no `.gitignore` e ficam só nas máquinas do grupo. Para reproduzir as análises, gere a base com o script de coleta (passo 1 de "Como reproduzir"). O repositório traz apenas resultados agregados: contagens, percentuais, tabelas por país e figuras.

A pasta `dados/` traz dois arquivos usados pelo Julio para normalizar os resultados: `total_scopus_por_ano.csv` (total de publicações na Scopus por ano) e `total_scopus_por_pais.csv` (total de publicações de cada país em 2000–2025).

## Estrutura do repositório

```
dados/
  artigos_scopus_G.csv          base do grupo (busca G), gerada pela coleta; fora do repositório
  total_scopus_por_ano.csv      total de publicações na Scopus por ano
  total_scopus_por_pais.csv     total de publicações por país, 2000–2025
Odeilson/
  coleta/coleta_scopus.py       baixa os artigos pela API da Scopus
  analise/analise.py            publicações por país, antes e depois de 2014
  analise/mapa.py               mapa interativo (HTML) com o número de publicações por país
  analise/resultados/           tabelas por país e período
  analise/figuras/              gráfico por período e mapa
Julio/
  codigo/01_evolucao_temporal.py   publicações por ano, brutas e por milhão de publicações da Scopus
  codigo/02_hipotese2_paises.py    volume, foco relativo, impacto e financiamento por país
  resultados/                      figuras
Mariane/Analise_Bibliometrica/
  códigos/                      scripts 01–04 (conferência, publicações por ano, crescimento, impacto)
  resultados/                   tabelas, gráfico de crescimento e textos de interpretação (leia-me/)
Gabriel/
  Gabriel_Analise_Financiamento.ipynb   notebook da análise de financiamento
  *.csv, *.png                          tabelas e gráficos gerados pelo notebook
Planejamento.docx                   planejamento feito em reunião em 17/11/2026
Planejamento da aprensetação.txt    ordem e responsáveis da apresentação
```

## Como reproduzir

Requisitos: Python 3.12 e as bibliotecas abaixo.

```bash
pip install requests pandas numpy matplotlib plotly pycountry jupyter
```

Todos os comandos são executados a partir da raiz do repositório.

**1. Coleta (necessária, porque a base não está no repositório).** Todas as análises leem `dados/artigos_scopus_G.csv`. A coleta precisa de uma chave da API da Elsevier (dev.elsevier.com) e de acesso institucional (rede ou VPN da universidade). Sem esse acesso, a API não devolve o financiamento e traz só o país da primeira afiliação.

```bash
export SCOPUS_API_KEY="sua_chave"         # no Windows (PowerShell): $env:SCOPUS_API_KEY = "sua_chave"
python Odeilson/coleta/coleta_scopus.py   # busca G -> dados/artigos_scopus_G.csv
```

**2. Distribuição geográfica (Odeilson).**

```bash
python Odeilson/analise/analise.py
python Odeilson/analise/mapa.py
```

O mapa é gerado em `Odeilson/analise/figuras/mapa_publicacoes_G.html`. Abra no navegador e passe o cursor sobre um país para ver o número de publicações. Os botões alternam entre o total e os períodos 2000–2013 e 2014–2025. O arquivo precisa de internet para desenhar os contornos dos países.

**3. Crescimento e impacto por artigo (Mariane).** O script 02 precisa rodar antes do 03.

```bash
python Mariane/Analise_Bibliometrica/códigos/01_conferencia_dados.py
python Mariane/Analise_Bibliometrica/códigos/02_publicacoes_por_ano.py
python Mariane/Analise_Bibliometrica/códigos/03_grafico_crescimento.py
python Mariane/Analise_Bibliometrica/códigos/04_impacto_cientifico.py
```

**4. Evolução normalizada e síntese por país (Julio).**

```bash
python Julio/codigo/01_evolucao_temporal.py
python Julio/codigo/02_hipotese2_paises.py
```

**5. Financiamento (Gabriel).** O notebook lê `../dados/artigos_scopus_G.csv`, então precisa ser executado de dentro da pasta `Gabriel/`.

```bash
cd Gabriel
jupyter nbconvert --to notebook --execute --inplace Gabriel_Analise_Financiamento.ipynb
```

## Escolhas metodológicas

- **Tipos de documento:** só *Article* e *Review*, em todas as análises.
- **Marco:** 2014. Os períodos comparados são 2000–2013 e 2014–2025.
- **Contagem inteira:** cada país presente nas afiliações conta uma vez por artigo. Por isso as porcentagens de um período somam mais de 100%.
- **Hong Kong** aparece separado da China, como na Scopus.
- **Financiamento declarado:** um artigo conta como financiado quando tem pelo menos um dos campos `fund_sponsor`, `fund_acr` ou `fund_no` preenchido.
- **Impacto por artigo (Mariane):** citações divididas pelos anos desde a publicação, Ci / (2026 − Ai).
- **Impacto por país (Julio):** citações de cada artigo divididas pela média de citações dos artigos do mesmo ano (estilo FWCI; 1,0 = média da área), e depois a média por país. Só entram países com pelo menos 10 artigos.
- **Foco relativo (Julio):** artigos sobre o tema a cada 100 mil publicações do país na Scopus.

## Principais resultados

### Pergunta 1: crescimento da área

| Período | Artigos | Comportamento |
|---|---|---|
| 2000–2013 | 33 | Produção pequena e irregular (0 a 6 por ano), sem tendência definida |
| 2014–2025 | 1807 | Crescimento exponencial de **58% ao ano**, dobrando a cada **1,5 ano** (R² = 0,98) |

O crescimento não é efeito do aumento geral da ciência: normalizada pelo total da Scopus, a produção passa de 1,1 para 34,5 artigos por milhão de publicações. A mudança de ritmo coincide com o marco de 2014, mas a análise mostra uma associação temporal, não uma relação de causa.

### Pergunta 2: volume, impacto e financiamento por país

| País | Artigos | Impacto normalizado | Financiamento declarado |
|---|---|---|---|
| China | 1250 | 1,06 | 90% |
| Estados Unidos | 228 | 1,55 | 79% |
| Hong Kong | 154 | 1,32 | 97% |
| Coreia do Sul | 112 | 1,24 | 96% |
| Reino Unido | 65 | 1,12 | 94% |
| Austrália | 55 | 0,83 | 84% |
| Índia | 54 | 0,45 | 41% |
| Singapura | 41 | 1,87 | 95% |
| Espanha | 36 | 0,83 | 94% |
| Itália | 33 | 1,02 | 76% |

- **Volume:** antes de 2014, a produção era pequena e espalhada (EUA 21%, Japão 15%, China, Irã e Nigéria 9% cada). Depois, a China passa a dominar, aparecendo em 69% dos artigos.
- **Impacto:** liderar em volume não significa liderar em impacto. A China fica perto da média da área, enquanto Singapura e os EUA ficam bem acima.
- **Financiamento:** a declaração de financiamento é alta na maioria dos países. Índia e Japão são as exceções entre os que mais publicam.
- **Foco relativo:** Hong Kong, China, Singapura e Coreia do Sul são os que mais concentram sua produção científica no tema.
- As correlações entre volume e impacto (0,36) e entre volume e financiamento (0,19) são fracas e foram calculadas com só 19 países.

## Limitações

- **Cobertura da Scopus:** a base favorece revistas em inglês e de grandes editoras.
- **Termos de busca:** a escolha dos termos afeta o resultado, principalmente antes de 2014, como mostra a diferença entre as buscas A e G. Os registros anteriores a 2014 ainda não foram conferidos manualmente.
- **Amostras pequenas:** com 33 artigos em 2000–2013, as porcentagens desse período mudam muito com poucos artigos. O mesmo vale para países com poucos artigos.
- **Citações:** são um indicador indireto de qualidade, e a média por país é sensível a poucos artigos muito citados.
- **Financiamento:** o indicador mede se o financiamento foi declarado na Scopus, não o valor investido.
- **Dados de 2025:** podem estar incompletos por causa do atraso de indexação.
- **Uso dos dados:** os termos de uso da Scopus restringem a redistribuição dos dados. Por isso a base por artigo não está no repositório, e a reprodução exige acesso à Scopus. Os dados são da Scopus (Elsevier), usados sob a licença institucional da universidade.
