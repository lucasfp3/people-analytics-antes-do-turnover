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


# =========================
# 1. RESUMO POR ÁREA
# =========================

matriz = (
    df.groupby(["nome_area", "diretoria"])
    .agg(
        meses_analisados=("mes_referencia", "nunique"),
        headcount_medio=("headcount_medio", "mean"),
        media_taxa_absenteismo=("taxa_absenteismo", "mean"),
        media_taxa_falta_injustificada=("taxa_falta_injustificada", "mean"),
        media_horas_extras_por_colaborador=("horas_extras_por_colaborador", "mean"),
        media_taxa_turnover_voluntario=("taxa_turnover_voluntario", "mean"),
        total_desligamentos_voluntarios=("qtd_desligamentos_voluntarios", "sum"),
        total_horas_ausencia=("total_horas_ausencia", "sum"),
        total_horas_extras=("total_horas_extras", "sum"),
    )
    .reset_index()
)


# =========================
# 2. CRIAÇÃO DE RANKINGS
# =========================
# Quanto maior o valor, maior o risco relativo dentro da própria base.

matriz["rank_absenteismo"] = matriz["media_taxa_absenteismo"].rank(
    method="dense",
    ascending=True,
    pct=True
)

matriz["rank_horas_extras"] = matriz["media_horas_extras_por_colaborador"].rank(
    method="dense",
    ascending=True,
    pct=True
)

matriz["rank_turnover_voluntario"] = matriz["media_taxa_turnover_voluntario"].rank(
    method="dense",
    ascending=True,
    pct=True
)


# =========================
# 3. SCORE DE RISCO
# =========================
# Pesos sugeridos:
# - Absenteísmo: 35%
# - Horas extras: 35%
# - Turnover voluntário: 30%
#
# A lógica é simples:
# absenteísmo e horas extras são sinais operacionais;
# turnover voluntário é o desfecho observado.

matriz["score_risco"] = (
    matriz["rank_absenteismo"] * 0.35
    + matriz["rank_horas_extras"] * 0.35
    + matriz["rank_turnover_voluntario"] * 0.30
)


# =========================
# 4. CLASSIFICAÇÃO DE RISCO
# =========================

def classificar_risco(score):
    if score >= 0.75:
        return "Crítica"
    elif score >= 0.50:
        return "Atenção"
    else:
        return "Monitoramento"


matriz["classificacao_risco"] = matriz["score_risco"].apply(classificar_risco)

matriz = matriz.sort_values("score_risco", ascending=False)


# =========================
# 5. EXPORTAÇÃO DA MATRIZ
# =========================

caminho_matriz = os.path.join(OUTPUTS_TABLES_DIR, "matriz_risco_area.csv")
matriz.to_csv(caminho_matriz, index=False, encoding="utf-8-sig")


print("Matriz de risco gerada com sucesso!")
print(f"Arquivo salvo em: {caminho_matriz}")

print("\nMatriz de risco por área:")
print(
    matriz[
        [
            "nome_area",
            "diretoria",
            "media_taxa_absenteismo",
            "media_horas_extras_por_colaborador",
            "media_taxa_turnover_voluntario",
            "score_risco",
            "classificacao_risco",
        ]
    ]
)


# =========================
# 6. GRÁFICO DA MATRIZ DE RISCO
# =========================

plt.figure(figsize=(10, 6))

plt.scatter(
    matriz["media_taxa_absenteismo"],
    matriz["media_horas_extras_por_colaborador"],
    s=matriz["media_taxa_turnover_voluntario"] * 10000 + 50,
    alpha=0.7
)

for _, row in matriz.iterrows():
    plt.text(
        row["media_taxa_absenteismo"],
        row["media_horas_extras_por_colaborador"],
        row["nome_area"],
        fontsize=8,
        ha="left",
        va="bottom"
    )

plt.xlabel("Média da taxa de absenteísmo")
plt.ylabel("Média de horas extras por colaborador")
plt.title("Matriz de risco por área: absenteísmo, horas extras e turnover voluntário")
plt.grid(True, alpha=0.3)
plt.tight_layout()

caminho_grafico = os.path.join(OUTPUTS_CHARTS_DIR, "matriz_risco_area.png")
plt.savefig(caminho_grafico, dpi=150)
plt.close()

print(f"\nGráfico salvo em: {caminho_grafico}")