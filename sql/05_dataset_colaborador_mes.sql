USE PeopleAnalyticsBeforeTurnover;
GO

DROP TABLE IF EXISTS dbo.dataset_colaborador_mes;
GO

WITH numeros AS (
    SELECT TOP (96)
        ROW_NUMBER() OVER (ORDER BY object_id) - 1 AS n
    FROM sys.all_objects
),

calendario_mes AS (
    SELECT
        DATEADD(MONTH, n, CAST('2018-01-01' AS DATE)) AS mes_referencia,
        EOMONTH(DATEADD(MONTH, n, CAST('2018-01-01' AS DATE))) AS fim_mes
    FROM numeros
),

colaborador_mes AS (
    SELECT
        c.id_colaborador,
        c.matricula,
        c.sexo,
        c.data_nascimento,
        c.data_admissao,
        c.data_desligamento,
        c.status_colaborador,
        c.tipo_desligamento,
        c.id_area,
        a.nome_area,
        a.diretoria,
        c.id_cargo,
        cg.nome_cargo,
        cg.nivel_cargo,
        cm.mes_referencia,
        cm.fim_mes
    FROM dbo.dim_colaborador c
    INNER JOIN dbo.dim_area a
        ON c.id_area = a.id_area
    INNER JOIN dbo.dim_cargo cg
        ON c.id_cargo = cg.id_cargo
    CROSS JOIN calendario_mes cm
    WHERE c.data_admissao <= cm.fim_mes
      AND (
            c.data_desligamento IS NULL
            OR c.data_desligamento > cm.fim_mes
          )
),

features AS (
    SELECT
        cm.*,

        DATEDIFF(MONTH, cm.data_admissao, cm.fim_mes) AS tempo_casa_meses,

        DATEDIFF(YEAR, cm.data_nascimento, cm.fim_mes) AS idade_aproximada,

        ISNULL((
            SELECT COUNT(*)
            FROM dbo.fato_absenteismo fa
            WHERE fa.id_colaborador = cm.id_colaborador
              AND fa.data_absencia >= DATEADD(MONTH, -3, cm.mes_referencia)
              AND fa.data_absencia <= cm.fim_mes
        ), 0) AS qtd_eventos_ausencia_ultimos_3m,

        ISNULL((
            SELECT SUM(fa.dias_ausencia)
            FROM dbo.fato_absenteismo fa
            WHERE fa.id_colaborador = cm.id_colaborador
              AND fa.data_absencia >= DATEADD(MONTH, -3, cm.mes_referencia)
              AND fa.data_absencia <= cm.fim_mes
        ), 0) AS dias_ausencia_ultimos_3m,

        ISNULL((
            SELECT SUM(fa.horas_ausencia)
            FROM dbo.fato_absenteismo fa
            WHERE fa.id_colaborador = cm.id_colaborador
              AND fa.data_absencia >= DATEADD(MONTH, -3, cm.mes_referencia)
              AND fa.data_absencia <= cm.fim_mes
        ), 0) AS horas_ausencia_ultimos_3m,

        ISNULL((
            SELECT SUM(CASE WHEN fa.justificada = 0 THEN 1 ELSE 0 END)
            FROM dbo.fato_absenteismo fa
            WHERE fa.id_colaborador = cm.id_colaborador
              AND fa.data_absencia >= DATEADD(MONTH, -3, cm.mes_referencia)
              AND fa.data_absencia <= cm.fim_mes
        ), 0) AS qtd_faltas_injustificadas_ultimos_3m,

        ISNULL((
            SELECT SUM(fhe.horas_extras)
            FROM dbo.fato_horas_extras fhe
            WHERE fhe.id_colaborador = cm.id_colaborador
              AND fhe.data_hora_extra >= DATEADD(MONTH, -3, cm.mes_referencia)
              AND fhe.data_hora_extra <= cm.fim_mes
        ), 0) AS horas_extras_ultimos_3m,

        ISNULL((
            SELECT SUM(fhe.horas_banco)
            FROM dbo.fato_horas_extras fhe
            WHERE fhe.id_colaborador = cm.id_colaborador
              AND fhe.data_hora_extra >= DATEADD(MONTH, -3, cm.mes_referencia)
              AND fhe.data_hora_extra <= cm.fim_mes
        ), 0) AS horas_banco_ultimos_3m,

        CASE
            WHEN cm.tipo_desligamento = 'Voluntário'
             AND cm.data_desligamento > cm.fim_mes
             AND cm.data_desligamento <= EOMONTH(DATEADD(MONTH, 3, cm.fim_mes))
            THEN 1
            ELSE 0
        END AS target_turnover_voluntario_3m

    FROM colaborador_mes cm
)

SELECT *
INTO dbo.dataset_colaborador_mes
FROM features
WHERE tempo_casa_meses >= 1;
GO

CREATE INDEX IX_dataset_colaborador_mes_colab_mes
ON dbo.dataset_colaborador_mes (id_colaborador, mes_referencia);
GO

SELECT
    COUNT(*) AS qtd_linhas,
    COUNT(DISTINCT id_colaborador) AS qtd_colaboradores,
    SUM(target_turnover_voluntario_3m) AS qtd_targets_positivos
FROM dbo.dataset_colaborador_mes;
GO

SELECT TOP 20 *
FROM dbo.dataset_colaborador_mes
ORDER BY id_colaborador, mes_referencia;
GO