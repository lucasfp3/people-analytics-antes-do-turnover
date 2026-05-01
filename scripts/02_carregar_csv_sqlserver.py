import os
from urllib.parse import quote_plus

import pandas as pd
from sqlalchemy import create_engine


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")

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

engine = create_engine(url_conexao, fast_executemany=True)

arquivos_tabelas = [
    ("areas.csv", "dim_area"),
    ("cargos.csv", "dim_cargo"),
    ("colaboradores.csv", "dim_colaborador"),
    ("absenteismo.csv", "fato_absenteismo"),
    ("horas_extras.csv", "fato_horas_extras"),
]


for arquivo, tabela in arquivos_tabelas:
    caminho_arquivo = os.path.join(RAW_DIR, arquivo)

    print(f"Carregando {arquivo} para dbo.{tabela}...")

    df = pd.read_csv(caminho_arquivo, encoding="utf-8-sig")

    df.to_sql(
        name=tabela,
        con=engine,
        schema="dbo",
        if_exists="append",
        index=False
    )

    print(f"{len(df)} linhas carregadas em dbo.{tabela}.")


print("Carga finalizada com sucesso!")