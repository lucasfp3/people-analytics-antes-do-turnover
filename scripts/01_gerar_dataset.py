import os
import random
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from faker import Faker


fake = Faker("pt_BR")
Faker.seed(42)
np.random.seed(42)
random.seed(42)


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")

os.makedirs(RAW_DIR, exist_ok=True)


def random_date(start_date, end_date):
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    return start_date + timedelta(days=random_days)


# =========================
# 1. ÁREAS
# =========================

areas = pd.DataFrame([
    {"id_area": 1, "nome_area": "Atendimento", "diretoria": "Operações"},
    {"id_area": 2, "nome_area": "Enfermagem", "diretoria": "Operações Assistenciais"},
    {"id_area": 3, "nome_area": "Comercial", "diretoria": "Receita"},
    {"id_area": 4, "nome_area": "Financeiro", "diretoria": "Administrativo"},
    {"id_area": 5, "nome_area": "Tecnologia", "diretoria": "Corporativo"},
    {"id_area": 6, "nome_area": "Recursos Humanos", "diretoria": "Corporativo"},
    {"id_area": 7, "nome_area": "Logística", "diretoria": "Operações"},
    {"id_area": 8, "nome_area": "Faturamento", "diretoria": "Administrativo"},
])

areas.to_csv(os.path.join(RAW_DIR, "areas.csv"), index=False, encoding="utf-8-sig")


# =========================
# 2. CARGOS
# =========================

cargos = pd.DataFrame([
    {"id_cargo": 1, "nome_cargo": "Auxiliar", "nivel_cargo": "Operacional"},
    {"id_cargo": 2, "nome_cargo": "Assistente", "nivel_cargo": "Operacional"},
    {"id_cargo": 3, "nome_cargo": "Analista Júnior", "nivel_cargo": "Técnico"},
    {"id_cargo": 4, "nome_cargo": "Analista Pleno", "nivel_cargo": "Técnico"},
    {"id_cargo": 5, "nome_cargo": "Analista Sênior", "nivel_cargo": "Técnico"},
    {"id_cargo": 6, "nome_cargo": "Especialista", "nivel_cargo": "Especialista"},
    {"id_cargo": 7, "nome_cargo": "Coordenador", "nivel_cargo": "Liderança"},
    {"id_cargo": 8, "nome_cargo": "Gerente", "nivel_cargo": "Liderança"},
])

cargos.to_csv(os.path.join(RAW_DIR, "cargos.csv"), index=False, encoding="utf-8-sig")


# =========================
# 3. COLABORADORES
# =========================

n_colaboradores = 1200

data_inicio_empresa = datetime(2018, 1, 1)
data_fim_base = datetime(2025, 12, 31)

pesos_area = {
    1: 0.22,  # Atendimento
    2: 0.18,  # Enfermagem
    3: 0.14,  # Comercial
    4: 0.10,  # Financeiro
    5: 0.12,  # Tecnologia
    6: 0.08,  # RH
    7: 0.10,  # Logística
    8: 0.06,  # Faturamento
}

ids_area = list(pesos_area.keys())
probs_area = list(pesos_area.values())

colaboradores = []

for i in range(1, n_colaboradores + 1):
    id_area = np.random.choice(ids_area, p=probs_area)

    if id_area in [1, 2, 7]:
        id_cargo = np.random.choice([1, 2, 3, 4], p=[0.25, 0.35, 0.25, 0.15])
    elif id_area in [5]:
        id_cargo = np.random.choice([3, 4, 5, 6, 7], p=[0.15, 0.25, 0.30, 0.20, 0.10])
    else:
        id_cargo = np.random.choice([2, 3, 4, 5, 6, 7, 8], p=[0.20, 0.20, 0.25, 0.15, 0.10, 0.07, 0.03])

    data_admissao = random_date(data_inicio_empresa, datetime(2025, 6, 30))

    idade = random.randint(20, 58)
    data_nascimento = datetime(2025 - idade, random.randint(1, 12), random.randint(1, 28))

    base_prob_desligamento = {
        1: 0.24,  # Atendimento
        2: 0.22,  # Enfermagem
        3: 0.18,  # Comercial
        4: 0.10,  # Financeiro
        5: 0.15,  # Tecnologia
        6: 0.09,  # RH
        7: 0.20,  # Logística
        8: 0.12,  # Faturamento
    }[id_area]

    desligado = np.random.rand() < base_prob_desligamento

    data_desligamento = None
    tipo_desligamento = None
    status_colaborador = "Ativo"

    if desligado:
        data_min_desligamento = data_admissao + timedelta(days=90)
        if data_min_desligamento < data_fim_base:
            data_desligamento = random_date(data_min_desligamento, data_fim_base)
            status_colaborador = "Desligado"
            tipo_desligamento = np.random.choice(
                ["Voluntário", "Involuntário"],
                p=[0.65, 0.35]
            )

    colaboradores.append({
        "id_colaborador": i,
        "matricula": f"MAT{i:05d}",
        "nome_colaborador": fake.name(),
        "sexo": np.random.choice(["Feminino", "Masculino"], p=[0.58, 0.42]),
        "data_nascimento": data_nascimento.date(),
        "data_admissao": data_admissao.date(),
        "data_desligamento": data_desligamento.date() if data_desligamento else None,
        "status_colaborador": status_colaborador,
        "tipo_desligamento": tipo_desligamento,
        "id_area": id_area,
        "id_cargo": id_cargo,
        "id_gestor": random.randint(1, 80),
        "id_unidade": random.randint(1, 15),
    })

colaboradores = pd.DataFrame(colaboradores)
colaboradores.to_csv(os.path.join(RAW_DIR, "colaboradores.csv"), index=False, encoding="utf-8-sig")


# =========================
# 4. ABSENTEÍSMO
# =========================

absenteismo_registros = []
id_absencia = 1

taxa_abs_area = {
    1: 0.18,
    2: 0.20,
    3: 0.12,
    4: 0.07,
    5: 0.08,
    6: 0.06,
    7: 0.16,
    8: 0.09,
}

tipos_absencia = ["Atestado", "Falta injustificada", "Atraso", "Licença curta"]
prob_tipos = [0.55, 0.20, 0.15, 0.10]

for _, colab in colaboradores.iterrows():
    id_area = colab["id_area"]
    data_admissao = pd.to_datetime(colab["data_admissao"])
    data_limite = pd.to_datetime(colab["data_desligamento"]) if pd.notna(colab["data_desligamento"]) else data_fim_base

    meses_ativo = max(1, ((data_limite.year - data_admissao.year) * 12 + data_limite.month - data_admissao.month))

    media_eventos = meses_ativo * taxa_abs_area[id_area]
    qtd_eventos = np.random.poisson(media_eventos)

for _, colab in colaboradores.iterrows():
    id_area = colab["id_area"]

    data_admissao = pd.to_datetime(colab["data_admissao"]).to_pydatetime()

    if pd.notna(colab["data_desligamento"]):
        data_limite = pd.to_datetime(colab["data_desligamento"]).to_pydatetime()
    else:
        data_limite = data_fim_base

    meses_ativo = max(
        1,
        ((data_limite.year - data_admissao.year) * 12 + data_limite.month - data_admissao.month)
    )

    media_eventos = meses_ativo * taxa_abs_area[id_area]
    qtd_eventos = np.random.poisson(media_eventos)

    for _ in range(qtd_eventos):
        data_abs = random_date(data_admissao, data_limite)

        tipo = np.random.choice(tipos_absencia, p=prob_tipos)

        if tipo == "Atraso":
            dias = 0
            horas = np.random.choice([1, 2, 3, 4], p=[0.45, 0.30, 0.15, 0.10])
        elif tipo == "Licença curta":
            dias = random.randint(2, 5)
            horas = dias * 8
        else:
            dias = random.randint(1, 3)
            horas = dias * 8

        justificada = 0 if tipo == "Falta injustificada" else 1

        absenteismo_registros.append({
            "id_absencia": id_absencia,
            "id_colaborador": colab["id_colaborador"],
            "data_absencia": data_abs.date(),
            "tipo_absencia": tipo,
            "justificada": justificada,
            "dias_ausencia": dias,
            "horas_ausencia": horas,
        })

        id_absencia += 1

absenteismo = pd.DataFrame(absenteismo_registros)
absenteismo.to_csv(os.path.join(RAW_DIR, "absenteismo.csv"), index=False, encoding="utf-8-sig")


# =========================
# 5. HORAS EXTRAS
# =========================

horas_extras_registros = []
id_hora_extra = 1

taxa_he_area = {
    1: 0.22,
    2: 0.24,
    3: 0.13,
    4: 0.06,
    5: 0.10,
    6: 0.05,
    7: 0.18,
    8: 0.08,
}

for _, colab in colaboradores.iterrows():
    id_area = colab["id_area"]

    data_admissao = pd.to_datetime(colab["data_admissao"]).to_pydatetime()

    if pd.notna(colab["data_desligamento"]):
        data_limite = pd.to_datetime(colab["data_desligamento"]).to_pydatetime()
    else:
        data_limite = data_fim_base

    meses_ativo = max(
        1,
        ((data_limite.year - data_admissao.year) * 12 + data_limite.month - data_admissao.month)
    )

    media_eventos = meses_ativo * taxa_he_area[id_area]
    qtd_eventos = np.random.poisson(media_eventos)

    for _ in range(qtd_eventos):
        data_he = random_date(data_admissao, data_limite)

        horas = round(np.random.gamma(shape=2.0, scale=2.0), 2)
        horas = min(horas, 12)

        tipo_lancamento = np.random.choice(
            ["Hora extra paga", "Banco de horas positivo", "Compensação"],
            p=[0.55, 0.35, 0.10]
        )

        horas_banco = horas if tipo_lancamento == "Banco de horas positivo" else 0

        horas_extras_registros.append({
            "id_hora_extra": id_hora_extra,
            "id_colaborador": colab["id_colaborador"],
            "data_hora_extra": data_he.date(),
            "horas_extras": horas,
            "horas_banco": horas_banco,
            "tipo_lancamento": tipo_lancamento,
        })

        id_hora_extra += 1

horas_extras = pd.DataFrame(horas_extras_registros)
horas_extras.to_csv(os.path.join(RAW_DIR, "horas_extras.csv"), index=False, encoding="utf-8-sig")


print("Datasets gerados com sucesso!")
print(f"Colaboradores: {len(colaboradores)}")
print(f"Absenteísmo: {len(absenteismo)}")
print(f"Horas extras: {len(horas_extras)}")
print(f"Arquivos salvos em: {RAW_DIR}")