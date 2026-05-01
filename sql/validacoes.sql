-- SELECT TOP 10 * 
-- FROM dbo.vw_absenteismo_area_mes
-- ORDER BY mes_referencia, nome_area;

-- SELECT TOP 10 * 
-- FROM dbo.vw_horas_extras_area_mes
-- ORDER BY mes_referencia, nome_area;

-- SELECT TOP 10 * 
-- FROM dbo.vw_turnover_area_mes
-- ORDER BY mes_referencia, nome_area;

-- SELECT TOP 20 *
-- FROM dbo.vw_dataset_area_mes
-- ORDER BY mes_referencia, nome_area;

-- SELECT
--     COUNT(*) AS qtd_linhas
-- FROM dbo.vw_dataset_area_mes;

-- SELECT
--     MIN(mes_referencia) AS primeira_competencia,
--     MAX(mes_referencia) AS ultima_competencia,
--     COUNT(DISTINCT mes_referencia) AS qtd_meses,
--     COUNT(DISTINCT id_area) AS qtd_areas
-- FROM dbo.vw_dataset_area_mes;

SELECT
    nome_area,
    SUM(qtd_desligamentos) AS total_desligamentos,
    SUM(qtd_desligamentos_voluntarios) AS total_desligamentos_voluntarios,
    SUM(total_horas_ausencia) AS total_horas_ausencia,
    SUM(total_horas_extras) AS total_horas_extras,
    AVG(taxa_absenteismo) AS media_taxa_absenteismo,
    AVG(horas_extras_por_colaborador) AS media_horas_extras_por_colaborador,
    AVG(taxa_turnover_voluntario) AS media_taxa_turnover_voluntario
FROM dbo.vw_dataset_area_mes
GROUP BY nome_area
ORDER BY media_taxa_absenteismo DESC;