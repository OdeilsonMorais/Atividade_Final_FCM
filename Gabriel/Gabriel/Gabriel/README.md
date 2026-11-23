# Financiamento declarado por país no resfriamento radiativo passivo

A análise estima a proporção de artigos e revisões sobre resfriamento radiativo passivo com financiamento declarado na Scopus, por país ou território de afiliação, entre 2000 e 2025. A fonte é a exportação usada pela Mariane, descrita em [dados/README.md](dados/README.md).

## Método

1. Selecionam-se os tipos *Article* e *Review* com ano inteiro de 2000 a 2025, inclusive. O EID identifica cada documento. Quando falta EID, usa-se o DOI normalizado. Se o DOI aponta para um único EID, as linhas são reunidas sob esse EID. Se aponta para vários EIDs, preservam-se os EIDs distintos e mantêm-se separadas as linhas sem EID. Na ausência dos dois identificadores, cada linha é mantida e pode representar uma duplicata que os metadados não permitem resolver.
2. Extraem-se os países de **Affiliations** pelos componentes finais dos endereços. **Authors with affiliations** complementa a extração quando a afiliação está vazia ou contém trechos cujo país não foi reconhecido. A lista do `pycountry` e as variantes observadas padronizam nomes, como `USA` para `United States` e `Republic of Korea` para `South Korea`. Hong Kong e Taiwan são contabilizados separadamente da China. Em endereços terminados em `China`, componentes explícitos de localização, como `Hong Kong SAR`, permitem distinguir Hong Kong de um campus na China continental.
3. Classifica-se o documento como tendo financiamento declarado quando **Funding Details** contém informação. Espaços, valores ausentes, pontuação isolada e marcadores como `N/A` ou `No funding` não contam como informação. **Funding Texts** é usado para conferência, sem alterar a classificação. Ao consolidar linhas do mesmo documento, unem-se os países e considera-se suficiente um registro válido de **Funding Details**. Divergências de ano ou tipo entre linhas elegíveis com a mesma chave interrompem a execução para conferência.
4. Para cada país, o percentual é **100 × documentos com financiamento declarado ÷ total de documentos atribuídos ao país**. Cada documento conta uma vez em cada país participante, mesmo que tenha várias instituições no mesmo país. O denominador inclui registros sem declaração. Documentos sem país identificado entram no resumo geral e ficam de fora das tabelas por país.

## Resultados e limitações

Dos **1.305 documentos elegíveis**, **1.159 (88,81%)** têm financiamento declarado. Foram identificados **58 países e territórios**. A China tem 818 declarações em 882 documentos (92,74%), os Estados Unidos têm 149 em 178 (83,71%) e a Coreia do Sul tem 82 em 85 (96,47%). Entre os dez países da tabela solicitada, Singapura tem o maior percentual (35 de 35) e a Índia tem o menor (19 de 41).

O indicador mede a presença de informação indexada na Scopus. Um campo vazio é compatível com financiamento não registrado na exportação. O indicador também não informa o valor investido nem identifica qual país financiou o trabalho. Percentuais de países com poucos documentos são mais sensíveis a alterações no conjunto analisado. A cobertura depende da busca e da qualidade dos metadados de afiliação e financiamento.

## Reprodução

Da raiz do repositório, com Python 3.12:

~~~bash
python -m pip install pandas==2.2.3 pycountry==26.2.16
python Gabriel/codigos/analise_financiamento.py
~~~

O script localiza a base em relação à própria pasta, imprime as verificações e gera os dois CSVs em `Gabriel/resultados/`. Os CSVs têm codificação UTF-8, vírgula como separador e ponto decimal. Os percentuais estão na escala de 0 a 100, com seis casas decimais na exportação. O [relatório de conferência](resultados/conferencia_dados.md) registra a auditoria desta versão. O notebook, os CSVs e o gráfico anteriores podem ser consultados no commit `6fa9a2a`.

## Integração com o gráfico coletivo

Odeilson deve usar [financiamento_top10_grupo.csv](resultados/financiamento_top10_grupo.csv), com junção pela coluna `pais` e o valor de `percentual_financiamento` na terceira coluna do gráfico. A tabela [financiamento_por_pais.csv](resultados/financiamento_por_pais.csv) contém todos os países identificados. Se um país do grupo estiver ausente em uma nova execução, seus campos numéricos ficarão em branco.

Os resultados de volume da busca A e da busca G e a análise de impacto publicada no repositório abrangem conjuntos diferentes de documentos. Para comparar os três indicadores diretamente, o grupo precisa usar a mesma lista de EIDs elegíveis para calcular volume, impacto e financiamento, com a mesma atribuição de países por documento. A comparação entre as bases está no [relatório de conferência](resultados/conferencia_dados.md).
