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
    id_area,
    nome_area,
    diretoria,
    mes_referencia,
    headcount_inicio_mes,
    headcount_fim_mes,
    headcount_medio,
    qtd_eventos_ausencia,
    qtd_colaboradores_com_ausencia,
    total_dias_ausencia,
    total_horas_ausencia,
    total_dias_falta_injustificada,
    total_horas_falta_injustificada,
    qtd_lancamentos_horas_extras,
    qtd_colaboradores_com_hora_extra,
    total_horas_extras,
    total_horas_banco,
    media_horas_extras_por_lancamento,
    qtd_desligamentos,
    qtd_desligamentos_voluntarios,
    qtd_desligamentos_involuntarios,
    taxa_absenteismo,
    taxa_falta_injustificada,
    horas_extras_por_colaborador,
    taxa_turnover,
    taxa_turnover_voluntario
FROM dbo.vw_dataset_area_mes
WHERE headcount_medio >= 10
ORDER BY mes_referencia, nome_area;
"""

df = pd.read_sql(query, engine)

caminho_saida = os.path.join(PASTA_PROCESSADA, "dataset_area_mes.csv")
df.to_csv(caminho_saida, index=False, encoding="utf-8-sig")

print("Dataset exportado com sucesso!")
print(f"Linhas exportadas: {len(df)}")
print(f"Arquivo salvo em: {caminho_saida}")

print("\nPrévia dos dados:")
print(df.head())