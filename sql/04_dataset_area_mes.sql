USE PeopleAnalyticsBeforeTurnover;
GO

DROP VIEW IF EXISTS dbo.vw_dataset_area_mes;
GO

CREATE VIEW dbo.vw_dataset_area_mes AS

WITH numeros AS (
    SELECT TOP (96)
        ROW_NUMBER() OVER (ORDER BY object_id) - 1 AS n
    FROM sys.all_objects
),

calendario_mes AS (
    SELECT
        DATEADD(MONTH, n, CAST('2018-01-01' AS DATE)) AS mes_referencia
    FROM numeros
),

area_mes AS (
    SELECT
        a.id_area,
        a.nome_area,
        a.diretoria,
        c.mes_referencia,
        EOMONTH(c.mes_referencia) AS fim_mes
    FROM dbo.dim_area a
    CROSS JOIN calendario_mes c
),

headcount AS (
    SELECT
        am.id_area,
        am.mes_referencia,

        SUM(
            CASE 
                WHEN col.data_admissao <= am.mes_referencia
                 AND (
                        col.data_desligamento IS NULL 
                        OR col.data_desligamento >= am.mes_referencia
                     )
                THEN 1 
                ELSE 0 
            END
        ) AS headcount_inicio_mes,

        SUM(
            CASE 
                WHEN col.data_admissao <= am.fim_mes
                 AND (
                        col.data_desligamento IS NULL 
                        OR col.data_desligamento > am.fim_mes
                     )
                THEN 1 
                ELSE 0 
            END
        ) AS headcount_fim_mes

    FROM area_mes am
    LEFT JOIN dbo.dim_colaborador col
        ON am.id_area = col.id_area
    GROUP BY
        am.id_area,
        am.mes_referencia
)

SELECT
    am.id_area,
    am.nome_area,
    am.diretoria,
    am.mes_referencia,

    ISNULL(h.headcount_inicio_mes, 0) AS headcount_inicio_mes,
    ISNULL(h.headcount_fim_mes, 0) AS headcount_fim_mes,

    CAST(
        (ISNULL(h.headcount_inicio_mes, 0) + ISNULL(h.headcount_fim_mes, 0)) / 2.0
        AS DECIMAL(10,2)
    ) AS headcount_medio,

    ISNULL(abs.qtd_eventos_ausencia, 0) AS qtd_eventos_ausencia,
    ISNULL(abs.qtd_colaboradores_com_ausencia, 0) AS qtd_colaboradores_com_ausencia,
    ISNULL(abs.total_dias_ausencia, 0) AS total_dias_ausencia,
    ISNULL(abs.total_horas_ausencia, 0) AS total_horas_ausencia,
    ISNULL(abs.total_dias_falta_injustificada, 0) AS total_dias_falta_injustificada,
    ISNULL(abs.total_horas_falta_injustificada, 0) AS total_horas_falta_injustificada,

    ISNULL(he.qtd_lancamentos_horas_extras, 0) AS qtd_lancamentos_horas_extras,
    ISNULL(he.qtd_colaboradores_com_hora_extra, 0) AS qtd_colaboradores_com_hora_extra,
    ISNULL(he.total_horas_extras, 0) AS total_horas_extras,
    ISNULL(he.total_horas_banco, 0) AS total_horas_banco,
    ISNULL(he.media_horas_extras_por_lancamento, 0) AS media_horas_extras_por_lancamento,

    ISNULL(t.qtd_desligamentos, 0) AS qtd_desligamentos,
    ISNULL(t.qtd_desligamentos_voluntarios, 0) AS qtd_desligamentos_voluntarios,
    ISNULL(t.qtd_desligamentos_involuntarios, 0) AS qtd_desligamentos_involuntarios,

    CAST(
        CASE 
            WHEN ((ISNULL(h.headcount_inicio_mes, 0) + ISNULL(h.headcount_fim_mes, 0)) / 2.0) = 0
            THEN 0
            ELSE ISNULL(abs.total_horas_ausencia, 0) / 
                 (((ISNULL(h.headcount_inicio_mes, 0) + ISNULL(h.headcount_fim_mes, 0)) / 2.0) * 176)
        END
        AS DECIMAL(10,4)
    ) AS taxa_absenteismo,

    CAST(
        CASE 
            WHEN ((ISNULL(h.headcount_inicio_mes, 0) + ISNULL(h.headcount_fim_mes, 0)) / 2.0) = 0
            THEN 0
            ELSE ISNULL(abs.total_horas_falta_injustificada, 0) / 
                 (((ISNULL(h.headcount_inicio_mes, 0) + ISNULL(h.headcount_fim_mes, 0)) / 2.0) * 176)
        END
        AS DECIMAL(10,4)
    ) AS taxa_falta_injustificada,

    CAST(
        CASE 
            WHEN ((ISNULL(h.headcount_inicio_mes, 0) + ISNULL(h.headcount_fim_mes, 0)) / 2.0) = 0
            THEN 0
            ELSE ISNULL(he.total_horas_extras, 0) / 
                 ((ISNULL(h.headcount_inicio_mes, 0) + ISNULL(h.headcount_fim_mes, 0)) / 2.0)
        END
        AS DECIMAL(10,2)
    ) AS horas_extras_por_colaborador,

    CAST(
        CASE 
            WHEN ((ISNULL(h.headcount_inicio_mes, 0) + ISNULL(h.headcount_fim_mes, 0)) / 2.0) = 0
            THEN 0
            ELSE ISNULL(t.qtd_desligamentos, 0) / 
                 ((ISNULL(h.headcount_inicio_mes, 0) + ISNULL(h.headcount_fim_mes, 0)) / 2.0)
        END
        AS DECIMAL(10,4)
    ) AS taxa_turnover,

    CAST(
        CASE 
            WHEN ((ISNULL(h.headcount_inicio_mes, 0) + ISNULL(h.headcount_fim_mes, 0)) / 2.0) = 0
            THEN 0
            ELSE ISNULL(t.qtd_desligamentos_voluntarios, 0) / 
                 ((ISNULL(h.headcount_inicio_mes, 0) + ISNULL(h.headcount_fim_mes, 0)) / 2.0)
        END
        AS DECIMAL(10,4)
    ) AS taxa_turnover_voluntario

FROM area_mes am
LEFT JOIN headcount h
    ON am.id_area = h.id_area
   AND am.mes_referencia = h.mes_referencia

LEFT JOIN dbo.vw_absenteismo_area_mes abs
    ON am.id_area = abs.id_area
   AND am.mes_referencia = abs.mes_referencia

LEFT JOIN dbo.vw_horas_extras_area_mes he
    ON am.id_area = he.id_area
   AND am.mes_referencia = he.mes_referencia

LEFT JOIN dbo.vw_turnover_area_mes t
    ON am.id_area = t.id_area
   AND am.mes_referencia = t.mes_referencia;
GO