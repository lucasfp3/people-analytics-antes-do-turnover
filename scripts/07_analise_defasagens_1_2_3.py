import os

import pandas as pd
import matplotlib.pyplot as plt


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSADA_DIR = os.path.join(BASE_DIR, "data", "processada")
OUTPUTS_TABLES_DIR = os.path.join(BASE_DIR, "outputs", "tables")
OUTPUTS_CHARTS_DIR = os.path.join(BASE_DIR, "outputs", "charts")

os.makedirs(OUTPUTS_TABLES_DIR, exist_ok=True)
os.makedirs(OUTPUTS_CHARTS_DIR, exist_ok=True)


caminho_dataset = os.path.join(PROCESSADA_DIR, "dataset_area_mes.csv")

df = pd.read_csv(caminho_dataset, encoding="utf-8-sig")
df["mes_referencia"] = pd.to_datetime(df["mes_referencia"])

df = df.sort_values(["nome_area", "mes_referencia"]).copy()


variaveis_sinais = [
    "taxa_absenteismo",
    "horas_extras_por_colaborador",
    "taxa_falta_injustificada",
]

variavel_alvo = "taxa_turnover_voluntario"

resultados = []

for lag in [1, 2, 3]:
    df_lag = df.copy()

    for variavel in variaveis_sinais:
        nome_lag = f"{variavel}_lag{lag}"
        df_lag[nome_lag] = df_lag.groupby("nome_area")[variavel].shift(lag)

        base_corr = df_lag.dropna(subset=[nome_lag, variavel_alvo]).copy()

        pearson = base_corr[nome_lag].corr(base_corr[variavel_alvo], method="pearson")
        spearman = base_corr[nome_lag].corr(base_corr[variavel_alvo], method="spearman")

        resultados.append({
            "variavel_sinal": variavel,
            "lag_meses": lag,
            "pearson_com_turnover_voluntario": pearson,
            "spearman_com_turnover_voluntario": spearman,
            "qtd_linhas_analisadas": len(base_corr),
        })


df_resultados = pd.DataFrame(resultados)

caminho_saida = os.path.join(
    OUTPUTS_TABLES_DIR,
    "correlacoes_defasagens_1_2_3.csv"
)

df_resultados.to_csv(caminho_saida, index=False, encoding="utf-8-sig")

print("Análise de defasagens concluída com sucesso!")
print(f"Arquivo salvo em: {caminho_saida}")
print("\nResultados:")
print(df_resultados)


# =========================
# Gráfico comparativo - Pearson
# =========================

plt.figure(figsize=(10, 6))

for variavel in variaveis_sinais:
    dados_variavel = df_resultados[df_resultados["variavel_sinal"] == variavel]

    plt.plot(
        dados_variavel["lag_meses"],
        dados_variavel["pearson_com_turnover_voluntario"],
        marker="o",
        label=variavel
    )

plt.xlabel("Defasagem em meses")
plt.ylabel("Correlação de Pearson com turnover voluntário")
plt.title("Correlação com turnover voluntário por defasagem temporal")
plt.xticks([1, 2, 3])
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()

caminho_grafico_pearson = os.path.join(
    OUTPUTS_CHARTS_DIR,
    "correlacao_pearson_defasagens_1_2_3.png"
)

plt.savefig(caminho_grafico_pearson, dpi=150)
plt.close()

print(f"\nGráfico Pearson salvo em: {caminho_grafico_pearson}")


# =========================
# Gráfico comparativo - Spearman
# =========================

plt.figure(figsize=(10, 6))

for variavel in variaveis_sinais:
    dados_variavel = df_resultados[df_resultados["variavel_sinal"] == variavel]

    plt.plot(
        dados_variavel["lag_meses"],
        dados_variavel["spearman_com_turnover_voluntario"],
        marker="o",
        label=variavel
    )

plt.xlabel("Defasagem em meses")
plt.ylabel("Correlação de Spearman com turnover voluntário")
plt.title("Correlação por ranking com turnover voluntário por defasagem temporal")
plt.xticks([1, 2, 3])
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()

caminho_grafico_spearman = os.path.join(
    OUTPUTS_CHARTS_DIR,
    "correlacao_spearman_defasagens_1_2_3.png"
)

plt.savefig(caminho_grafico_spearman, dpi=150)
plt.close()

print(f"Gráfico Spearman salvo em: {caminho_grafico_spearman}")