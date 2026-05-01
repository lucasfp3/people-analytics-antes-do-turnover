USE PeopleAnalyticsBeforeTurnover;
GO

-- 1. Visão geral da base colaborador/mês
SELECT
    COUNT(*) AS qtd_linhas,
    COUNT(DISTINCT id_colaborador) AS qtd_colaboradores,
    SUM(target_turnover_voluntario_3m) AS qtd_targets_positivos,
    CAST(AVG(CAST(target_turnover_voluntario_3m AS FLOAT)) AS DECIMAL(10,4)) AS taxa_target_positivo
FROM dbo.dataset_colaborador_mes;
GO


-- 2. Colaboradores únicos com target positivo
SELECT
    COUNT(DISTINCT id_colaborador) AS qtd_colaboradores_com_target_positivo
FROM dbo.dataset_colaborador_mes
WHERE target_turnover_voluntario_3m = 1;
GO


-- 3. Distribuição do target
SELECT
    target_turnover_voluntario_3m,
    COUNT(*) AS qtd_linhas,
    CAST(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER () AS DECIMAL(10,2)) AS percentual
FROM dbo.dataset_colaborador_mes
GROUP BY target_turnover_voluntario_3m
ORDER BY target_turnover_voluntario_3m;
GO


-- 4. Target positivo por área
SELECT
    nome_area,
    diretoria,
    COUNT(*) AS qtd_linhas,
    SUM(target_turnover_voluntario_3m) AS qtd_targets_positivos,
    COUNT(DISTINCT CASE 
        WHEN target_turnover_voluntario_3m = 1 
        THEN id_colaborador 
    END) AS colaboradores_unicos_com_target,
    CAST(AVG(CAST(target_turnover_voluntario_3m AS FLOAT)) AS DECIMAL(10,4)) AS taxa_target_positivo
FROM dbo.dataset_colaborador_mes
GROUP BY
    nome_area,
    diretoria
ORDER BY
    taxa_target_positivo DESC;
GO


-- 5. Médias das features por classe do target
SELECT
    target_turnover_voluntario_3m,
    COUNT(*) AS qtd_linhas,
    AVG(CAST(tempo_casa_meses AS FLOAT)) AS media_tempo_casa_meses,
    AVG(CAST(idade_aproximada AS FLOAT)) AS media_idade_aproximada,
    AVG(CAST(qtd_eventos_ausencia_ultimos_3m AS FLOAT)) AS media_eventos_ausencia_3m,
    AVG(CAST(dias_ausencia_ultimos_3m AS FLOAT)) AS media_dias_ausencia_3m,
    AVG(CAST(horas_ausencia_ultimos_3m AS FLOAT)) AS media_horas_ausencia_3m,
    AVG(CAST(qtd_faltas_injustificadas_ultimos_3m AS FLOAT)) AS media_faltas_injustificadas_3m,
    AVG(CAST(horas_extras_ultimos_3m AS FLOAT)) AS media_horas_extras_3m,
    AVG(CAST(horas_banco_ultimos_3m AS FLOAT)) AS media_horas_banco_3m
FROM dbo.dataset_colaborador_mes
GROUP BY target_turnover_voluntario_3m
ORDER BY target_turnover_voluntario_3m;
GO


-- 6. Checagem de valores negativos
SELECT
    SUM(CASE WHEN tempo_casa_meses < 0 THEN 1 ELSE 0 END) AS tempo_casa_negativo,
    SUM(CASE WHEN idade_aproximada < 0 THEN 1 ELSE 0 END) AS idade_negativa,
    SUM(CASE WHEN qtd_eventos_ausencia_ultimos_3m < 0 THEN 1 ELSE 0 END) AS eventos_ausencia_negativos,
    SUM(CASE WHEN dias_ausencia_ultimos_3m < 0 THEN 1 ELSE 0 END) AS dias_ausencia_negativos,
    SUM(CASE WHEN horas_ausencia_ultimos_3m < 0 THEN 1 ELSE 0 END) AS horas_ausencia_negativas,
    SUM(CASE WHEN qtd_faltas_injustificadas_ultimos_3m < 0 THEN 1 ELSE 0 END) AS faltas_injustificadas_negativas,
    SUM(CASE WHEN horas_extras_ultimos_3m < 0 THEN 1 ELSE 0 END) AS horas_extras_negativas,
    SUM(CASE WHEN horas_banco_ultimos_3m < 0 THEN 1 ELSE 0 END) AS horas_banco_negativas
FROM dbo.dataset_colaborador_mes;
GO