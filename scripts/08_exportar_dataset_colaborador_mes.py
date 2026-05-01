import os
from urllib.parse import quote_plus

import pandas as pd
from sqlalchemy import create_engine


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PASTA_PROCESSADA = os.path.join(BASE_DIR, "data", "processada")

os.makedirs(PASTA_PROCESSADA, exist_ok=True)

SERVIDOR = r"LAPTOP-DHNTIMEE"
BANCO = "PeopleAnalyticsBeforeTurnover"

string_conexao = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    f"SERVER={SERVIDOR};"
    f"DATABASE={BANCO};"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"
)

url_conexao = f"mssql+pyodbc:///?odbc_connect={quote_plus(string_conexao)}"
engine = create_engine(url_conexao)

query = """
SELECT
    id_colaborador,
    matricula,
    sexo,
    data_nascimento,
    data_admissao,
    data_desligamento,
    status_colaborador,
    tipo_desligamento,
    id_area,
    nome_area,
    diretoria,
    id_cargo,
    nome_cargo,
    nivel_cargo,
    mes_referencia,
    fim_mes,
    tempo_casa_meses,
    idade_aproximada,
    qtd_eventos_ausencia_ultimos_3m,
    dias_ausencia_ultimos_3m,
    horas_ausencia_ultimos_3m,
    qtd_faltas_injustificadas_ultimos_3m,
    horas_extras_ultimos_3m,
    horas_banco_ultimos_3m,
    target_turnover_voluntario_3m
FROM dbo.dataset_colaborador_mes
ORDER BY id_colaborador, mes_referencia;
"""

print("Conectando ao SQL Server...")
df = pd.read_sql(query, engine)

caminho_saida = os.path.join(PASTA_PROCESSADA, "dataset_colaborador_mes.csv")
df.to_csv(caminho_saida, index=False, encoding="utf-8-sig")

print("Dataset colaborador/mês exportado com sucesso!")
print(f"Linhas exportadas: {len(df)}")
print(f"Colaboradores únicos: {df['id_colaborador'].nunique()}")
print(f"Targets positivos: {df['target_turnover_voluntario_3m'].sum()}")
print(f"Arquivo salvo em: {caminho_saida}")

print("\nPrévia dos dados:")
print(df.head())