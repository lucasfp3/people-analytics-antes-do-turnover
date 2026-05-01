import os

import numpy as np
import pandas as pd


# =========================
# 1. CONFIGURAÇÕES
# =========================

np.random.seed(42)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSADA_DIR = os.path.join(BASE_DIR, "data", "processada")
OUTPUTS_TABLES_DIR = os.path.join(BASE_DIR, "outputs", "tables")

os.makedirs(PROCESSADA_DIR, exist_ok=True)
os.makedirs(OUTPUTS_TABLES_DIR, exist_ok=True)

CAMINHO_ENTRADA = os.path.join(PROCESSADA_DIR, "dataset_colaborador_mes.csv")
CAMINHO_SAIDA = os.path.join(PROCESSADA_DIR, "dataset_colaborador_mes_enriquecido.csv")


# =========================
# 2. LEITURA DA BASE
# =========================

df = pd.read_csv(CAMINHO_ENTRADA, encoding="utf-8-sig")

df["mes_referencia"] = pd.to_datetime(df["mes_referencia"])
df["fim_mes"] = pd.to_datetime(df["fim_mes"])
df["data_admissao"] = pd.to_datetime(df["data_admissao"], errors="coerce")
df["data_desligamento"] = pd.to_datetime(df["data_desligamento"], errors="coerce")

df = df.sort_values(["id_colaborador", "mes_referencia"]).copy()

print("Dataset colaborador/mês carregado com sucesso!")
print(f"Linhas: {len(df)}")
print(f"Colaboradores únicos: {df['id_colaborador'].nunique()}")
print(f"Targets positivos: {df['target_turnover_voluntario_3m'].sum()}")


# =========================
# 3. ATRIBUTOS FIXOS POR COLABORADOR
# =========================

colaboradores = (
    df[
        [
            "id_colaborador",
            "nome_area",
            "diretoria",
            "nivel_cargo",
            "tipo_desligamento",
            "data_admissao",
            "data_desligamento",
        ]
    ]
    .drop_duplicates("id_colaborador")
    .copy()
)

# Fator individual sintético.
# Como a base é fictícia, este fator ajuda a simular diferenças estruturais entre colaboradores.
colaboradores["fator_individual_salario"] = np.random.normal(
    loc=1.0,
    scale=0.10,
    size=len(colaboradores)
)

# Colaboradores com desligamento voluntário recebem, em média, um fator salarial um pouco menor.
# Isso simula uma hipótese comum em RH: remuneração relativa pode influenciar risco de saída.
colaboradores.loc[
    colaboradores["tipo_desligamento"] == "Voluntário",
    "fator_individual_salario"
] -= 0.05

colaboradores["fator_individual_salario"] = colaboradores["fator_individual_salario"].clip(0.70, 1.30)


# =========================
# 4. TIPO DE JORNADA E ESCALA
# =========================

def definir_tipo_jornada(row):
    area = row["nome_area"]
    nivel = row["nivel_cargo"]

    if area == "Enfermagem":
        return np.random.choice(["Plantão", "Turno"], p=[0.75, 0.25])
    if area in ["Atendimento", "Logística"]:
        return np.random.choice(["Turno", "Administrativa"], p=[0.70, 0.30])
    if nivel == "Liderança":
        return "Administrativa"
    return np.random.choice(["Administrativa", "Turno"], p=[0.85, 0.15])


def definir_escala(row):
    jornada = row["tipo_jornada"]
    area = row["nome_area"]

    if jornada == "Plantão":
        return np.random.choice(["12x36", "Plantão variável"], p=[0.70, 0.30])
    if jornada == "Turno":
        if area in ["Atendimento", "Logística"]:
            return np.random.choice(["6x1", "5x2"], p=[0.65, 0.35])
        return np.random.choice(["6x1", "5x2"], p=[0.40, 0.60])
    return "5x2"


colaboradores["tipo_jornada"] = colaboradores.apply(definir_tipo_jornada, axis=1)
colaboradores["escala_trabalho"] = colaboradores.apply(definir_escala, axis=1)


# =========================
# 5. DATA SIMULADA DE ÚLTIMA PROMOÇÃO
# =========================

def gerar_meses_ate_primeira_promocao(row):
    admissao = row["data_admissao"]
    desligamento = row["data_desligamento"]
    tipo_desligamento = row["tipo_desligamento"]
    nivel = row["nivel_cargo"]

    if pd.isna(admissao):
        return np.nan

    if nivel in ["Liderança", "Especialista"]:
        base = np.random.randint(18, 48)
    elif nivel == "Técnico":
        base = np.random.randint(12, 42)
    else:
        base = np.random.randint(10, 36)

    # Em colaboradores com desligamento voluntário, simulamos maior chance
    # de promoção mais distante no tempo.
    if tipo_desligamento == "Voluntário":
        base += np.random.randint(6, 18)

    return base


colaboradores["meses_ate_promocao_simulada"] = colaboradores.apply(
    gerar_meses_ate_primeira_promocao,
    axis=1
)


# =========================
# 6. MERGE DOS ATRIBUTOS NA BASE MENSAL
# =========================

df = df.merge(
    colaboradores[
        [
            "id_colaborador",
            "fator_individual_salario",
            "tipo_jornada",
            "escala_trabalho",
            "meses_ate_promocao_simulada",
        ]
    ],
    on="id_colaborador",
    how="left"
)


# =========================
# 7. SALÁRIO SINTÉTICO
# =========================

salario_base_nivel = {
    "Operacional": 2600,
    "Técnico": 5200,
    "Especialista": 8500,
    "Liderança": 11500,
}

multiplicador_area = {
    "Atendimento": 0.95,
    "Enfermagem": 1.05,
    "Comercial": 1.00,
    "Financeiro": 1.02,
    "Tecnologia": 1.18,
    "Recursos Humanos": 0.98,
    "Logística": 0.92,
    "Faturamento": 0.96,
}

df["salario_base_nivel"] = df["nivel_cargo"].map(salario_base_nivel)
df["multiplicador_area"] = df["nome_area"].map(multiplicador_area)

# Crescimento leve com tempo de casa, limitado para não explodir.
df["fator_tempo_casa"] = (1 + (df["tempo_casa_meses"] * 0.002)).clip(1.00, 1.25)

df["salario_mensal"] = (
    df["salario_base_nivel"]
    * df["multiplicador_area"]
    * df["fator_individual_salario"]
    * df["fator_tempo_casa"]
)

df["salario_mensal"] = df["salario_mensal"].round(2)

# Salário relativo à mediana do grupo área/cargo/mês.
df["mediana_salario_area_cargo_mes"] = (
    df.groupby(["nome_area", "nivel_cargo", "mes_referencia"])["salario_mensal"]
    .transform("median")
)

df["percentual_salario_vs_mediana"] = (
    df["salario_mensal"] / df["mediana_salario_area_cargo_mes"]
).round(4)


# =========================
# 8. PROMOÇÃO
# =========================

df["meses_desde_ultima_promocao"] = (
    df["tempo_casa_meses"] - df["meses_ate_promocao_simulada"]
)

df["meses_desde_ultima_promocao"] = df["meses_desde_ultima_promocao"].apply(
    lambda x: 0 if x < 0 else x
)

df["teve_promocao_ultimos_12m"] = np.where(
    (df["meses_desde_ultima_promocao"] > 0)
    & (df["meses_desde_ultima_promocao"] <= 12),
    1,
    0
)


# =========================
# 9. MUDANÇA DE GESTOR
# =========================

# Probabilidade base por área.
prob_mudanca_gestor_area = {
    "Atendimento": 0.10,
    "Enfermagem": 0.09,
    "Comercial": 0.08,
    "Financeiro": 0.05,
    "Tecnologia": 0.07,
    "Recursos Humanos": 0.05,
    "Logística": 0.09,
    "Faturamento": 0.05,
}

df["prob_mudanca_gestor"] = df["nome_area"].map(prob_mudanca_gestor_area)

# Simula maior instabilidade de gestor em meses com mais horas extras/ausência.
df["prob_mudanca_gestor"] = (
    df["prob_mudanca_gestor"]
    + np.where(df["horas_extras_ultimos_3m"] > df["horas_extras_ultimos_3m"].median(), 0.02, 0)
    + np.where(df["qtd_eventos_ausencia_ultimos_3m"] > 1, 0.01, 0)
).clip(0, 0.25)

df["mudou_gestor_ultimos_6m"] = np.random.binomial(
    n=1,
    p=df["prob_mudanca_gestor"]
)


# =========================
# 10. DESEMPENHO
# =========================

# Nota de desempenho sintética entre 1 e 5.
# A ideia é simular avaliações anuais/mensais derivadas de um padrão individual.
base_desempenho_nivel = {
    "Operacional": 3.15,
    "Técnico": 3.30,
    "Especialista": 3.55,
    "Liderança": 3.65,
}

df["base_desempenho"] = df["nivel_cargo"].map(base_desempenho_nivel)

ruido_desempenho = np.random.normal(loc=0, scale=0.35, size=len(df))

df["nota_desempenho"] = (
    df["base_desempenho"]
    + ruido_desempenho
    - np.where(df["qtd_eventos_ausencia_ultimos_3m"] >= 3, 0.10, 0)
    + np.where(df["teve_promocao_ultimos_12m"] == 1, 0.15, 0)
)

df["nota_desempenho"] = df["nota_desempenho"].clip(1, 5).round(2)

df["faixa_desempenho"] = pd.cut(
    df["nota_desempenho"],
    bins=[0, 2.5, 3.5, 4.2, 5],
    labels=["Baixo", "Médio", "Alto", "Excelente"],
    include_lowest=True
).astype(str)


# =========================
# 11. LIMPEZA DE COLUNAS AUXILIARES
# =========================

colunas_auxiliares = [
    "salario_base_nivel",
    "multiplicador_area",
    "fator_tempo_casa",
    "mediana_salario_area_cargo_mes",
    "meses_ate_promocao_simulada",
    "prob_mudanca_gestor",
    "base_desempenho",
]

df = df.drop(columns=colunas_auxiliares)


# =========================
# 12. EXPORTAÇÃO
# =========================

df.to_csv(CAMINHO_SAIDA, index=False, encoding="utf-8-sig")

resumo_enriquecimento = df[
    [
        "salario_mensal",
        "percentual_salario_vs_mediana",
        "meses_desde_ultima_promocao",
        "teve_promocao_ultimos_12m",
        "mudou_gestor_ultimos_6m",
        "nota_desempenho",
    ]
].describe()

CAMINHO_RESUMO = os.path.join(OUTPUTS_TABLES_DIR, "resumo_dataset_enriquecido.csv")
resumo_enriquecimento.to_csv(CAMINHO_RESUMO, encoding="utf-8-sig")

print("\nDataset enriquecido gerado com sucesso!")
print(f"Linhas: {len(df)}")
print(f"Colaboradores únicos: {df['id_colaborador'].nunique()}")
print(f"Targets positivos: {df['target_turnover_voluntario_3m'].sum()}")
print(f"Arquivo salvo em: {CAMINHO_SAIDA}")

print("\nNovas colunas criadas:")
novas_colunas = [
    "salario_mensal",
    "percentual_salario_vs_mediana",
    "meses_desde_ultima_promocao",
    "teve_promocao_ultimos_12m",
    "mudou_gestor_ultimos_6m",
    "nota_desempenho",
    "faixa_desempenho",
    "tipo_jornada",
    "escala_trabalho",
]

for coluna in novas_colunas:
    print(f"- {coluna}")

print("\nResumo das variáveis numéricas enriquecidas:")
print(resumo_enriquecimento)