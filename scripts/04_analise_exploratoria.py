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

print("Dataset carregado com sucesso!")
print(f"Linhas: {len(df)}")
print(f"Colunas: {len(df.columns)}")
print("\nColunas disponíveis:")
print(df.columns.tolist())

print("\nResumo inicial:")
print(df.describe())


# =========================
# 1. RESUMO POR ÁREA
# =========================

resumo_area = (
    df.groupby(["nome_area", "diretoria"])
    .agg(
        meses_analisados=("mes_referencia", "nunique"),
        headcount_medio=("headcount_medio", "mean"),
        total_desligamentos=("qtd_desligamentos", "sum"),
        total_desligamentos_voluntarios=("qtd_desligamentos_voluntarios", "sum"),
        total_horas_ausencia=("total_horas_ausencia", "sum"),
        total_horas_falta_injustificada=("total_horas_falta_injustificada", "sum"),
        total_horas_extras=("total_horas_extras", "sum"),
        media_taxa_absenteismo=("taxa_absenteismo", "mean"),
        media_taxa_falta_injustificada=("taxa_falta_injustificada", "mean"),
        media_horas_extras_por_colaborador=("horas_extras_por_colaborador", "mean"),
        media_taxa_turnover=("taxa_turnover", "mean"),
        media_taxa_turnover_voluntario=("taxa_turnover_voluntario", "mean"),
    )
    .reset_index()
    .sort_values("media_taxa_absenteismo", ascending=False)
)

caminho_resumo_area = os.path.join(OUTPUTS_TABLES_DIR, "resumo_area.csv")
resumo_area.to_csv(caminho_resumo_area, index=False, encoding="utf-8-sig")

print("\nResumo por área:")
print(resumo_area)


# =========================
# 2. CORRELAÇÕES
# =========================

variaveis_correlacao = [
    "taxa_absenteismo",
    "taxa_falta_injustificada",
    "horas_extras_por_colaborador",
    "taxa_turnover",
    "taxa_turnover_voluntario",
]

correlacao_pearson = df[variaveis_correlacao].corr(method="pearson")
correlacao_spearman = df[variaveis_correlacao].corr(method="spearman")

caminho_pearson = os.path.join(OUTPUTS_TABLES_DIR, "matriz_correlacao_pearson.csv")
caminho_spearman = os.path.join(OUTPUTS_TABLES_DIR, "matriz_correlacao_spearman.csv")

correlacao_pearson.to_csv(caminho_pearson, encoding="utf-8-sig")
correlacao_spearman.to_csv(caminho_spearman, encoding="utf-8-sig")

print("\nCorrelação de Pearson:")
print(correlacao_pearson)

print("\nCorrelação de Spearman:")
print(correlacao_spearman)


# =========================
# 3. GRÁFICOS DE DISPERSÃO
# =========================

def salvar_dispersao(x, y, titulo, nome_arquivo):
    plt.figure(figsize=(9, 6))
    plt.scatter(df[x], df[y], alpha=0.7)
    plt.xlabel(x)
    plt.ylabel(y)
    plt.title(titulo)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    caminho = os.path.join(OUTPUTS_CHARTS_DIR, nome_arquivo)
    plt.savefig(caminho, dpi=150)
    plt.close()

    print(f"Gráfico salvo em: {caminho}")


salvar_dispersao(
    x="taxa_absenteismo",
    y="horas_extras_por_colaborador",
    titulo="Relação entre absenteísmo e horas extras por colaborador",
    nome_arquivo="dispersao_absenteismo_horas_extras.png",
)

salvar_dispersao(
    x="horas_extras_por_colaborador",
    y="taxa_turnover_voluntario",
    titulo="Relação entre horas extras e turnover voluntário",
    nome_arquivo="dispersao_horas_extras_turnover_voluntario.png",
)

salvar_dispersao(
    x="taxa_absenteismo",
    y="taxa_turnover_voluntario",
    titulo="Relação entre absenteísmo e turnover voluntário",
    nome_arquivo="dispersao_absenteismo_turnover_voluntario.png",
)


print("\nAnálise exploratória finalizada com sucesso!")