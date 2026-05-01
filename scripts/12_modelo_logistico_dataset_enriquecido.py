import os

import pandas as pd
import matplotlib.pyplot as plt

from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    roc_auc_score,
    RocCurveDisplay,
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


df = pd.read_csv(CAMINHO_DATASET, encoding="utf-8-sig")

print("Dataset enriquecido carregado com sucesso!")
print(f"Linhas: {len(df)}")
print(f"Colaboradores únicos: {df['id_colaborador'].nunique()}")
print(f"Targets positivos: {df[TARGET].sum()}")
print(f"Taxa de target positivo: {df[TARGET].mean():.4%}")


features_numericas = [
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

features_categoricas = [
    "sexo",
    "nome_area",
    "nivel_cargo",
    "tipo_jornada",
    "escala_trabalho",
    "faixa_desempenho",
]

features = features_numericas + features_categoricas

df_modelo = df[features + [TARGET]].copy()
df_modelo = df_modelo.dropna()

X = df_modelo[features]
y = df_modelo[TARGET]

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.25,
    random_state=42,
    stratify=y,
)

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

pipeline = Pipeline(
    steps=[
        ("preprocessador", preprocessador),
        ("modelo", modelo),
    ]
)

pipeline.fit(X_train, y_train)

y_pred = pipeline.predict(X_test)
y_proba = pipeline.predict_proba(X_test)[:, 1]

roc_auc = roc_auc_score(y_test, y_proba)

print("\nMatriz de confusão:")
print(confusion_matrix(y_test, y_pred))

print("\nRelatório de classificação:")
print(classification_report(y_test, y_pred, digits=4, zero_division=0))

print(f"ROC AUC: {roc_auc:.4f}")


# =========================
# Métricas
# =========================

relatorio = classification_report(
    y_test,
    y_pred,
    output_dict=True,
    zero_division=0,
)

metricas = pd.DataFrame(relatorio).transpose()
metricas.loc["roc_auc", "precision"] = roc_auc

caminho_metricas = os.path.join(
    OUTPUTS_TABLES_DIR,
    "metricas_modelo_logistico_enriquecido.csv",
)

metricas.to_csv(caminho_metricas, encoding="utf-8-sig")

print(f"\nMétricas salvas em: {caminho_metricas}")


# =========================
# Curva ROC
# =========================

RocCurveDisplay.from_predictions(y_test, y_proba)

plt.title("Curva ROC - Modelo Logístico Enriquecido")
plt.tight_layout()

caminho_roc = os.path.join(
    OUTPUTS_CHARTS_DIR,
    "curva_roc_modelo_logistico_enriquecido.png",
)

plt.savefig(caminho_roc, dpi=150)
plt.close()

print(f"Curva ROC salva em: {caminho_roc}")


# =========================
# Coeficientes
# =========================

modelo_treinado = pipeline.named_steps["modelo"]
preprocessador_treinado = pipeline.named_steps["preprocessador"]

nomes_features = preprocessador_treinado.get_feature_names_out()

coeficientes = pd.DataFrame({
    "feature": nomes_features,
    "coeficiente": modelo_treinado.coef_[0],
})

coeficientes["impacto_absoluto"] = coeficientes["coeficiente"].abs()

coeficientes = coeficientes.sort_values(
    "impacto_absoluto",
    ascending=False,
)

caminho_coeficientes = os.path.join(
    OUTPUTS_TABLES_DIR,
    "coeficientes_modelo_logistico_enriquecido.csv",
)

coeficientes.to_csv(caminho_coeficientes, index=False, encoding="utf-8-sig")

print(f"Coeficientes salvos em: {caminho_coeficientes}")

print("\nTop 20 coeficientes por impacto absoluto:")
print(coeficientes.head(20))