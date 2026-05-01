import os

import pandas as pd
import matplotlib.pyplot as plt

from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSADA_DIR = os.path.join(BASE_DIR, "data", "processada")
OUTPUTS_TABLES_DIR = os.path.join(BASE_DIR, "outputs", "tables")
OUTPUTS_CHARTS_DIR = os.path.join(BASE_DIR, "outputs", "charts")

os.makedirs(OUTPUTS_TABLES_DIR, exist_ok=True)
os.makedirs(OUTPUTS_CHARTS_DIR, exist_ok=True)

CAMINHO_DATASET = os.path.join(PROCESSADA_DIR, "dataset_colaborador_mes_enriquecido.csv")
TARGET = "target_turnover_voluntario_3m"


def criar_pipeline(features_numericas, features_categoricas):
    preprocessador = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), features_numericas),
            ("cat", OneHotEncoder(handle_unknown="ignore"), features_categoricas),
        ]
    )

    modelo = LogisticRegression(
        max_iter=1000,
        class_weight="balanced",
        random_state=42,
    )

    return Pipeline(
        steps=[
            ("preprocessador", preprocessador),
            ("modelo", modelo),
        ]
    )


def avaliar(nome_modelo, descricao, df, features_numericas, features_categoricas):
    features = features_numericas + features_categoricas

    df_modelo = df[features + [TARGET]].dropna().copy()

    X = df_modelo[features]
    y = df_modelo[TARGET]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.25,
        random_state=42,
        stratify=y,
    )

    pipeline = criar_pipeline(features_numericas, features_categoricas)
    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)
    y_proba = pipeline.predict_proba(X_test)[:, 1]

    tn, fp, fn, tp = confusion_matrix(y_test, y_pred).ravel()

    return {
        "modelo": nome_modelo,
        "descricao": descricao,
        "accuracy": accuracy_score(y_test, y_pred),
        "roc_auc": roc_auc_score(y_test, y_proba),
        "precision_classe_1": precision_score(y_test, y_pred, pos_label=1, zero_division=0),
        "recall_classe_1": recall_score(y_test, y_pred, pos_label=1, zero_division=0),
        "f1_classe_1": f1_score(y_test, y_pred, pos_label=1, zero_division=0),
        "verdadeiros_negativos": tn,
        "falsos_positivos": fp,
        "falsos_negativos": fn,
        "verdadeiros_positivos": tp,
        "total_teste": len(y_test),
        "positivos_teste": int(y_test.sum()),
    }


df = pd.read_csv(CAMINHO_DATASET, encoding="utf-8-sig")

print("Dataset enriquecido carregado com sucesso!")
print(f"Linhas: {len(df)}")
print(f"Colaboradores únicos: {df['id_colaborador'].nunique()}")
print(f"Targets positivos: {df[TARGET].sum()}")


# Modelo operacional escolhido anteriormente: modelo 2 sem dias de ausência
features_num_operacional = [
    "tempo_casa_meses",
    "idade_aproximada",
    "qtd_eventos_ausencia_ultimos_3m",
    "horas_ausencia_ultimos_3m",
    "qtd_faltas_injustificadas_ultimos_3m",
    "horas_extras_ultimos_3m",
    "horas_banco_ultimos_3m",
]

features_cat_operacional = [
    "sexo",
    "nome_area",
    "nivel_cargo",
]

features_num_enriquecido = [
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

features_cat_enriquecido = [
    "sexo",
    "nome_area",
    "nivel_cargo",
    "tipo_jornada",
    "escala_trabalho",
    "faixa_desempenho",
]

resultados = []

resultados.append(
    avaliar(
        nome_modelo="modelo_operacional",
        descricao="Modelo com sinais operacionais, área e cargo.",
        df=df,
        features_numericas=features_num_operacional,
        features_categoricas=features_cat_operacional,
    )
)

resultados.append(
    avaliar(
        nome_modelo="modelo_enriquecido",
        descricao="Modelo com sinais operacionais, carreira, remuneração, desempenho, jornada e escala.",
        df=df,
        features_numericas=features_num_enriquecido,
        features_categoricas=features_cat_enriquecido,
    )
)

df_resultados = pd.DataFrame(resultados)

df_resultados = df_resultados.sort_values(
    by=["roc_auc", "f1_classe_1", "recall_classe_1"],
    ascending=False,
)

caminho_saida = os.path.join(
    OUTPUTS_TABLES_DIR,
    "comparacao_modelo_operacional_vs_enriquecido.csv",
)

df_resultados.to_csv(caminho_saida, index=False, encoding="utf-8-sig")

print("\nComparação modelo operacional vs enriquecido:")
print(
    df_resultados[
        [
            "modelo",
            "accuracy",
            "roc_auc",
            "precision_classe_1",
            "recall_classe_1",
            "f1_classe_1",
            "falsos_positivos",
            "falsos_negativos",
            "verdadeiros_positivos",
        ]
    ]
)

print(f"\nArquivo salvo em: {caminho_saida}")


# Gráfico comparativo
plt.figure(figsize=(8, 6))

plt.bar(
    df_resultados["modelo"],
    df_resultados["roc_auc"],
)

plt.xlabel("Modelo")
plt.ylabel("ROC AUC")
plt.title("Comparação entre modelo operacional e modelo enriquecido")
plt.ylim(0, 1)
plt.grid(axis="y", alpha=0.3)
plt.tight_layout()

caminho_grafico = os.path.join(
    OUTPUTS_CHARTS_DIR,
    "comparacao_modelo_operacional_vs_enriquecido.png",
)

plt.savefig(caminho_grafico, dpi=150)
plt.close()

print(f"Gráfico salvo em: {caminho_grafico}")