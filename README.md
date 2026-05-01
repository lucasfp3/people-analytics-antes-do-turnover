# People Analytics Antes do Turnover

Projeto prático de People Analytics com foco em investigação de sinais operacionais que podem anteceder o turnover voluntário.

A proposta é construir uma análise end-to-end utilizando SQL e Python, sem iniciar pelo dashboard. O objetivo é demonstrar como perguntas de negócio, qualidade de dados, modelagem analítica e análise estatística podem apoiar decisões mais preventivas em RH.

## Pergunta central

Quais sinais operacionais aparecem antes do turnover?

## Hipótese inicial

Áreas com maior absenteísmo e maior volume de horas extras podem apresentar maior risco de turnover voluntário, especialmente quando esses indicadores se repetem ao longo do tempo.

## Objetivos do projeto

- Criar um dataset fictício de RH com colaboradores, áreas, cargos, absenteísmo e horas extras
- Estruturar os dados em SQL Server
- Criar uma camada analítica mensal por área
- Investigar relações entre absenteísmo, horas extras e turnover
- Aplicar análise de correlação com Python
- Evoluir para uma matriz de risco por área
- Propor uma etapa futura de modelo preditivo e dashboard em BI

## Ferramentas utilizadas

- Python
- Pandas
- NumPy
- Faker
- SQL Server
- VSCode
- Git/GitHub

## Estrutura do projeto

```text
people-analytics-before-turnover/
│
├── artigo/
├── data/
│   ├── dicionario/
│   ├── processada/
│   └── raw/
├── docs/
├── notebooks/
├── outputs/
├── scripts/
├── sql/
├── README.md
└── requirements.txt
```

## Status do projeto

Em desenvolvimento.

## Etapas concluídas:

- Estrutura inicial do projeto
- Criação do ambiente Python
- Geração de dataset fictício
- Criação do banco SQL Server
- Criação das tabelas dimensionais e fatos iniciais

## Próximas etapas:

- Carga dos CSVs no SQL Server
- Validação de qualidade dos dados
- Criação da camada analítica por área e mês
- Análise exploratória em Python
- Correlação entre indicadores
- Matriz de risco
- Artigo técnico no LinkedIn

## Observação

Os dados utilizados neste projeto são fictícios e foram gerados exclusivamente para fins de estudo, portfólio e demonstração metodológica.