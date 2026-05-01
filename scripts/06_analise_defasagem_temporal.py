import os
import pandas as pd


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSADA_DIR = os.path.join(BASE_DIR, "data", "processada")
OUTPUTS_TABLES_DIR = os.path.join(BASE_DIR, "outputs", "tables")

os.makedirs(OUTPUTS_TABLES_DIR, exist_ok=True)

caminho_dataset = os.path.join(PROCESSADA_DIR, "dataset_area_mes.csv")
df = pd.read_csv(caminho_dataset, encoding="utf-8-sig")

df["mes_referencia"] = pd.to_datetime(df["mes_referencia"])

df = df.sort_values(["nome_area", "mes_referencia"]).copy()

# Defasagem de 1 mês por área
df["taxa_absenteismo_lag1"] = df.groupby("nome_area")["taxa_absenteismo"].shift(1)
df["horas_extras_por_colaborador_lag1"] = df.groupby("nome_area")["horas_extras_por_colaborador"].shift(1)
df["taxa_falta_injustificada_lag1"] = df.groupby("nome_area")["taxa_falta_injustificada"].shift(1)

df_lag = df.dropna(subset=[
    "taxa_absenteismo_lag1",
    "horas_extras_por_colaborador_lag1",
    "taxa_falta_injustificada_lag1",
    "taxa_turnover_voluntario"
]).copy()

# Correlação temporal
correlacoes_lag = pd.DataFrame({
    "variavel": [
        "taxa_absenteismo_lag1",
        "horas_extras_por_colaborador_lag1",
        "taxa_falta_injustificada_lag1"
    ],
    "pearson_com_turnover_voluntario": [
        df_lag["taxa_absenteismo_lag1"].corr(df_lag["taxa_turnover_voluntario"], method="pearson"),
        df_lag["horas_extras_por_colaborador_lag1"].corr(df_lag["taxa_turnover_voluntario"], method="pearson"),
        df_lag["taxa_falta_injustificada_lag1"].corr(df_lag["taxa_turnover_voluntario"], method="pearson")
    ],
    "spearman_com_turnover_voluntario": [
        df_lag["taxa_absenteismo_lag1"].corr(df_lag["taxa_turnover_voluntario"], method="spearman"),
        df_lag["horas_extras_por_colaborador_lag1"].corr(df_lag["taxa_turnover_voluntario"], method="spearman"),
        df_lag["taxa_falta_injustificada_lag1"].corr(df_lag["taxa_turnover_voluntario"], method="spearman")
    ]
})

caminho_saida = os.path.join(OUTPUTS_TABLES_DIR, "correlacoes_defasagem_lag1.csv")
correlacoes_lag.to_csv(caminho_saida, index=False, encoding="utf-8-sig")

print("Análise de defasagem temporal concluída com sucesso!")
print(f"Arquivo salvo em: {caminho_saida}")
print("\nCorrelação com turnover voluntário do mês atual:")
print(correlacoes_lag)