# Conferência dos dados de financiamento

## Seleção e contagem

| Etapa | Documentos |
|---|---:|
| Exportação original da Scopus | 1.513 |
| Fora de 2000–2025 ou com ano inválido | 0 |
| Excluídos por tipo documental | 208 |
| Elegíveis (1.212 artigos e 93 revisões) | 1.305 |
| Linhas redundantes após checagem de identificadores | 0 |
| Com financiamento declarado | 1.159 (88,81%) |
| Sem informação em Funding Details | 146 |
| Sem país identificado | 1 |

Todos os documentos elegíveis têm EID e os EIDs são únicos. Um documento não tem DOI. Entre os elegíveis, dois têm **Funding Details** preenchido e **Funding Texts** vazio e continuam classificados como tendo financiamento declarado. Nenhum apresenta a combinação inversa.

O registro `2-s2.0-85201005966` tem **Funding Details** preenchido e os dois campos de afiliação vazios. Está incluído no resumo geral. Os registros `2-s2.0-85084329567`, `2-s2.0-85129693896` e `2-s2.0-86000432474` têm trechos de endereço sem país reconhecido, mas também contêm endereços suficientes para atribuir, respectivamente, Marrocos, China e China/Singapura/Reino Unido. O campo de autores não acrescentou países na base atual.

Em 18 documentos, ao menos uma afiliação terminada em “China” continha componentes de endereço de Hong Kong. Essas afiliações foram atribuídas a Hong Kong. Afiliações com endereço em Shenzhen foram atribuídas à China, inclusive as de universidades sediadas em Hong Kong. No EID `2-s2.0-85216207393`, a exportação associa um endereço em Boston à Tailândia. A afiliação publicada confirma Boston, Massachusetts, EUA. [Artigo publicado](https://doi.org/10.3390/atmos16010095)

Foram identificados 58 países e territórios. A conferência encontrou 285 documentos associados a mais de um país, nenhuma repetição do par documento–país e nenhum percentual fora de 0% a 100%. Nos dez países encomendados para o gráfico, todos os valores estão presentes e seguem a ordem solicitada.

## Comparação com a análise anterior

O notebook anterior registrava 1.200 declarações em 1.366 documentos (87,8%) e processava a base carregada no Colab sem aplicar filtros explícitos de ano e tipo ao resultado geral. O CSV carregado, `scopus_resfriamento_2000_2025.csv.csv`, não está versionado, o que impede comparar os documentos individualmente. Os dois CSVs históricos e o gráfico foram conferidos no commit `6fa9a2a`. O gráfico representava a mesma seleção de dez países do CSV histórico, em ordem de percentual. A comparação histórica de 2015–2025 permanece disponível nesse commit.

| País ou território | Anterior, declarações / total (%) | Atual, declarações / total (%) |
|---|---:|---:|
| China | 851 / 921 (92,4%) | 818 / 882 (92,74%) |
| United States | 157 / 197 (79,7%) | 149 / 178 (83,71%) |
| South Korea | 82 / 85 (96,5%) | 82 / 85 (96,47%) |
| Hong Kong | 81 / 83 (97,6%) | 93 / 94 (98,94%) |
| India | 20 / 42 (47,6%) | 19 / 41 (46,34%) |
| Singapore | 36 / 36 (100%) | 35 / 35 (100%) |

A troca de base, a seleção documental e o tratamento dos endereços podem afetar as contagens. Na base atual, a leitura literal do último trecho da afiliação conta 889 documentos para China e 76 para Hong Kong, frente a 882 e 94 após o tratamento geográfico. Alguns documentos têm afiliações em ambos. Canadá e Taiwan aparecem na lista solicitada pelo grupo e não estavam entre os dez países da tabela anterior.

## Compatibilidade com os dados do grupo

A exportação da Mariane usa dois termos documentados de busca. No repositório, os scripts de distribuição geográfica de Odeilson usam por padrão a busca A, com quatro termos, e aceitam a busca G, com termos históricos adicionais e exclusões temáticas. A auditoria cruzou os EIDs únicos após aplicar a todas as bases os mesmos filtros de ano e tipo. [Buscas e critérios de Odeilson](../../README.md)

| Base de Odeilson | CSV original | Elegíveis | Também na base de Gabriel | Só em Gabriel | Só em Odeilson |
|---|---:|---:|---:|---:|---:|
| A | 1.658 | 1.434 | 1.305 | 0 | 129 |
| G | 2.154 | 1.840 | 1.269 | 36 | 571 |

Por exemplo, os CSVs geográficos atribuem à China 970 documentos na busca A e 1.250 na G, frente aos 882 da análise de financiamento. A versão final do gráfico coletivo com volume, impacto e financiamento não está no repositório consultado. Os resultados geográficos disponíveis identificam a base de cada variante, mas não permitem determinar qual será usada na versão final. O script de impacto da Mariane usa o mesmo CSV de origem e inclui todos os 1.513 registros com ano e citações disponíveis, sem restringir o tipo a *Article* e *Review*. [Resultados geográficos](../../Odeilson/analise/resultados/) · [Script de impacto](../../Mariane/Analise_Bibliometrica/c%C3%B3digos/04_impacto_cientifico.py)

Para uma comparação direta, o grupo precisa fixar a consulta e a lista de EIDs, aplicar os mesmos filtros e a mesma regra de atribuição de países às três métricas. Se escolher a busca A ou G, será necessário obter **Funding Details** também para os documentos elegíveis fora da exportação da Mariane e recalcular a fração nessa base. Os campos de financiamento da API têm outro formato e exigiriam uma definição comum validada antes de substituir o indicador. O arquivo [financiamento_top10_grupo.csv](financiamento_top10_grupo.csv) fornece os percentuais da exportação da Mariane na ordem solicitada.
