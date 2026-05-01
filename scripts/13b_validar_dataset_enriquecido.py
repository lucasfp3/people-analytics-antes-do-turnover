import os

import pandas as pd


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSADA_DIR = os.path.join(BASE_DIR, "data", "processada")
OUTPUTS_TABLES_DIR = os.path.join(BASE_DIR, "outputs", "tables")

os.makedirs(OUTPUTS_TABLES_DIR, exist_ok=True)

CAMINHO_DATASET = os.path.join(PROCESSADA_DIR, "dataset_colaborador_mes_enriquecido.csv")
TARGET = "target_turnover_voluntario_3m"

df = pd.read_csv(CAMINHO_DATASET, encoding="utf-8-sig")

features_modelo_enriquecido = [
    "tempo_casa_meses",
    "idade_aproximada",
    "qtd_eventos_ausencia_ultimos_3m",
    "horas_ausencia_ultimos_3m",
    "qtd_faltas_injustificadas_ultimos_3m",
    "horas_extras_ultimos_3m",
    "horas_banco_ultimos_3m",
    "salario_mensal",
    "percentual_salario_vs_mediana",
    "meses_desde_ultima_promocao",
    "teve_promocao_ultimos_12m",
    "mudou_gestor_ultimos_6m",
    "nota_desempenho",
    "sexo",
    "nome_area",
    "nivel_cargo",
    "tipo_jornada",
    "escala_trabalho",
    "faixa_desempenho",
]

colunas_proibidas_modelo = [
    "target_turnover_voluntario_3m",
    "tipo_desligamento",
    "data_desligamento",
    "status_colaborador",
]

print("Validação do dataset enriquecido")
print("=" * 80)

print(f"Linhas: {len(df)}")
print(f"Colaboradores únicos: {df['id_colaborador'].nunique()}")
print(f"Targets positivos: {df[TARGET].sum()}")
print(f"Taxa de target positivo: {df[TARGET].mean():.4%}")

print("\n1. Checagem de colunas esperadas")
colunas_ausentes = [col for col in features_modelo_enriquecido if col not in df.columns]

if colunas_ausentes:
    print("Colunas ausentes:")
    print(colunas_ausentes)
else:
    print("Todas as colunas do modelo estão presentes.")

print("\n2. Checagem de colunas proibidas nas features")
features_com_vazamento = [
    col for col in features_modelo_enriquecido if col in colunas_proibidas_modelo
]

if features_com_vazamento:
    print("Atenção: há colunas proibidas nas features!")
    print(features_com_vazamento)
else:
    print("Nenhuma coluna proibida está sendo usada como feature.")

print("\n3. Nulos nas features")
nulos = df[features_modelo_enriquecido].isna().sum()
nulos = nulos[nulos > 0]

if len(nulos) > 0:
    print(nulos)
else:
    print("Nenhum nulo encontrado nas features.")

print("\n4. Distribuição do target")
dist_target = (
    df[TARGET]
    .value_counts()
    .rename_axis("target")
    .reset_index(name="qtd_linhas")
)

dist_target["percentual"] = dist_target["qtd_linhas"] / len(df)

print(dist_target)

print("\n5. Target por área")
target_area = (
    df.groupby("nome_area")
    .agg(
        qtd_linhas=(TARGET, "count"),
        qtd_targets=(TARGET, "sum"),
        taxa_target=(TARGET, "mean"),
    )
    .reset_index()
    .sort_values("taxa_target", ascending=False)
)

print(target_area)

print("\n6. Target por tipo de jornada")
target_jornada = (
    df.groupby("tipo_jornada")
    .agg(
        qtd_linhas=(TARGET, "count"),
        qtd_targets=(TARGET, "sum"),
        taxa_target=(TARGET, "mean"),
    )
    .reset_index()
    .sort_values("taxa_target", ascending=False)
)

print(target_jornada)

print("\n7. Target por escala")
target_escala = (
    df.groupby("escala_trabalho")
    .agg(
        qtd_linhas=(TARGET, "count"),
        qtd_targets=(TARGET, "sum"),
        taxa_target=(TARGET, "mean"),
    )
    .reset_index()
    .sort_values("taxa_target", ascending=False)
)

print(target_escala)

print("\n8. Médias numéricas por target")
variaveis_numericas = [
    "tempo_casa_meses",
    "idade_aproximada",
    "qtd_eventos_ausencia_ultimos_3m",
    "horas_ausencia_ultimos_3m",
    "qtd_faltas_injustificadas_ultimos_3m",
    "horas_extras_ultimos_3m",
    "horas_banco_ultimos_3m",
    "salario_mensal",
    "percentual_salario_vs_mediana",
    "meses_desde_ultima_promocao",
    "teve_promocao_ultimos_12m",
    "mudou_gestor_ultimos_6m",
    "nota_desempenho",
]

medias_target = df.groupby(TARGET)[variaveis_numericas].mean().transpose()
print(medias_target)

print("\n9. Correlação das variáveis numéricas com o target")
correlacoes = (
    df[variaveis_numericas + [TARGET]]
    .corr(numeric_only=True)[TARGET]
    .drop(TARGET)
    .sort_values(key=lambda x: x.abs(), ascending=False)
    .reset_index()
)

correlacoes.columns = ["variavel", "correlacao_com_target"]

print(correlacoes)

caminho_target_area = os.path.join(OUTPUTS_TABLES_DIR, "validacao_target_por_area_enriquecido.csv")
caminho_target_jornada = os.path.join(OUTPUTS_TABLES_DIR, "validacao_target_por_jornada_enriquecido.csv")
caminho_target_escala = os.path.join(OUTPUTS_TABLES_DIR, "validacao_target_por_escala_enriquecido.csv")
caminho_medias = os.path.join(OUTPUTS_TABLES_DIR, "validacao_medias_por_target_enriquecido.csv")
caminho_correlacoes = os.path.join(OUTPUTS_TABLES_DIR, "validacao_correlacoes_target_enriquecido.csv")

target_area.to_csv(caminho_target_area, index=False, encoding="utf-8-sig")
target_jornada.to_csv(caminho_target_jornada, index=False, encoding="utf-8-sig")
target_escala.to_csv(caminho_target_escala, index=False, encoding="utf-8-sig")
medias_target.to_csv(caminho_medias, encoding="utf-8-sig")
correlacoes.to_csv(caminho_correlacoes, index=False, encoding="utf-8-sig")

print("\nArquivos de validação salvos em outputs/tables.")
print("\nValidação finalizada.")