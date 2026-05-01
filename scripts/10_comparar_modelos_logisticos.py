import os

import pandas as pd
import matplotlib.pyplot as plt

from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


# =========================
# 1. CONFIGURAÇÕES GERAIS
# =========================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSADA_DIR = os.path.join(BASE_DIR, "data", "processada")
OUTPUTS_TABLES_DIR = os.path.join(BASE_DIR, "outputs", "tables")
OUTPUTS_CHARTS_DIR = os.path.join(BASE_DIR, "outputs", "charts")

os.makedirs(OUTPUTS_TABLES_DIR, exist_ok=True)
os.makedirs(OUTPUTS_CHARTS_DIR, exist_ok=True)

CAMINHO_DATASET = os.path.join(PROCESSADA_DIR, "dataset_colaborador_mes.csv")

TARGET = "target_turnover_voluntario_3m"

FEATURES_CATEGORICAS = [
    "sexo",
    "nome_area",
    "nivel_cargo",
]

MODELOS = {
    "modelo_1_completo": {
        "features_numericas": [
            "tempo_casa_meses",
            "idade_aproximada",
            "qtd_eventos_ausencia_ultimos_3m",
            "dias_ausencia_ultimos_3m",
            "horas_ausencia_ultimos_3m",
            "qtd_faltas_injustificadas_ultimos_3m",
            "horas_extras_ultimos_3m",
            "horas_banco_ultimos_3m",
        ],
        "descricao": "Modelo completo com todas as variáveis numéricas iniciais.",
    },
    "modelo_2_sem_dias_ausencia": {
        "features_numericas": [
            "tempo_casa_meses",
            "idade_aproximada",
            "qtd_eventos_ausencia_ultimos_3m",
            "horas_ausencia_ultimos_3m",
            "qtd_faltas_injustificadas_ultimos_3m",
            "horas_extras_ultimos_3m",
            "horas_banco_ultimos_3m",
        ],
        "descricao": "Remove dias de ausência para reduzir redundância com horas de ausência.",
    },
    "modelo_3_sem_dias_e_horas_ausencia": {
        "features_numericas": [
            "tempo_casa_meses",
            "idade_aproximada",
            "qtd_eventos_ausencia_ultimos_3m",
            "qtd_faltas_injustificadas_ultimos_3m",
            "horas_extras_ultimos_3m",
            "horas_banco_ultimos_3m",
        ],
        "descricao": "Remove dias e horas de ausência, mantendo apenas frequência de eventos e demais sinais.",
    },
}


# =========================
# 2. FUNÇÕES AUXILIARES
# =========================

def criar_pipeline(features_numericas):
    preprocessador = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), features_numericas),
            ("cat", OneHotEncoder(handle_unknown="ignore"), FEATURES_CATEGORICAS),
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

    return pipeline


def avaliar_modelo(nome_modelo, descricao, pipeline, X_train, X_test, y_train, y_test):
    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)
    y_proba = pipeline.predict_proba(X_test)[:, 1]

    matriz = confusion_matrix(y_test, y_pred)

    tn, fp, fn, tp = matriz.ravel()

    resultado = {
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
        "negativos_teste": int((y_test == 0).sum()),
    }

    relatorio = classification_report(
        y_test,
        y_pred,
        digits=4,
        zero_division=0,
    )

    return resultado, matriz, relatorio


# =========================
# 3. LEITURA DOS DADOS
# =========================

df = pd.read_csv(CAMINHO_DATASET, encoding="utf-8-sig")

print("Dataset carregado com sucesso!")
print(f"Linhas: {len(df)}")
print(f"Colaboradores únicos: {df['id_colaborador'].nunique()}")
print(f"Targets positivos: {df[TARGET].sum()}")
print(f"Taxa de target positivo: {df[TARGET].mean():.4%}")


# =========================
# 4. TREINO E AVALIAÇÃO
# =========================

resultados = []

for nome_modelo, config in MODELOS.items():
    print("\n" + "=" * 80)
    print(f"Treinando: {nome_modelo}")
    print(config["descricao"])

    features_numericas = config["features_numericas"]
    features = features_numericas + FEATURES_CATEGORICAS

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

    pipeline = criar_pipeline(features_numericas)

    resultado, matriz, relatorio = avaliar_modelo(
        nome_modelo=nome_modelo,
        descricao=config["descricao"],
        pipeline=pipeline,
        X_train=X_train,
        X_test=X_test,
        y_train=y_train,
        y_test=y_test,
    )

    resultados.append(resultado)

    print("\nMatriz de confusão:")
    print(matriz)

    print("\nRelatório de classificação:")
    print(relatorio)

    print(f"ROC AUC: {resultado['roc_auc']:.4f}")
    print(f"Precision classe 1: {resultado['precision_classe_1']:.4f}")
    print(f"Recall classe 1: {resultado['recall_classe_1']:.4f}")
    print(f"F1 classe 1: {resultado['f1_classe_1']:.4f}")


# =========================
# 5. EXPORTAÇÃO DOS RESULTADOS
# =========================

df_resultados = pd.DataFrame(resultados)

df_resultados = df_resultados.sort_values(
    by=["roc_auc", "f1_classe_1", "recall_classe_1"],
    ascending=False,
)

caminho_saida = os.path.join(
    OUTPUTS_TABLES_DIR,
    "comparacao_modelos_logisticos.csv",
)

df_resultados.to_csv(caminho_saida, index=False, encoding="utf-8-sig")

print("\n" + "=" * 80)
print("Comparação final dos modelos:")
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


# =========================
# 6. GRÁFICO COMPARATIVO
# =========================

plt.figure(figsize=(10, 6))

plt.bar(
    df_resultados["modelo"],
    df_resultados["roc_auc"],
)

plt.xlabel("Modelo")
plt.ylabel("ROC AUC")
plt.title("Comparação de ROC AUC entre modelos logísticos")
plt.xticks(rotation=20, ha="right")
plt.ylim(0, 1)
plt.grid(axis="y", alpha=0.3)
plt.tight_layout()

caminho_grafico = os.path.join(
    OUTPUTS_CHARTS_DIR,
    "comparacao_roc_auc_modelos_logisticos.png",
)

plt.savefig(caminho_grafico, dpi=150)
plt.close()

print(f"Gráfico salvo em: {caminho_grafico}")
print("\nComparação de modelos finalizada com sucesso!")