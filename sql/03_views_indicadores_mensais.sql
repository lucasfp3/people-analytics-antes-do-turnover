USE PeopleAnalyticsBeforeTurnover;
GO

DROP VIEW IF EXISTS dbo.vw_absenteismo_area_mes;
GO

CREATE VIEW dbo.vw_absenteismo_area_mes AS
SELECT
    a.id_area,
    a.nome_area,
    a.diretoria,
    DATEFROMPARTS(YEAR(fa.data_absencia), MONTH(fa.data_absencia), 1) AS mes_referencia,
    COUNT(*) AS qtd_eventos_ausencia,
    COUNT(DISTINCT fa.id_colaborador) AS qtd_colaboradores_com_ausencia,
    SUM(fa.dias_ausencia) AS total_dias_ausencia,
    SUM(fa.horas_ausencia) AS total_horas_ausencia,
    SUM(CASE WHEN fa.justificada = 0 THEN fa.dias_ausencia ELSE 0 END) AS total_dias_falta_injustificada,
    SUM(CASE WHEN fa.justificada = 0 THEN fa.horas_ausencia ELSE 0 END) AS total_horas_falta_injustificada
FROM dbo.fato_absenteismo fa
INNER JOIN dbo.dim_colaborador c
    ON fa.id_colaborador = c.id_colaborador
INNER JOIN dbo.dim_area a
    ON c.id_area = a.id_area
GROUP BY
    a.id_area,
    a.nome_area,
    a.diretoria,
    DATEFROMPARTS(YEAR(fa.data_absencia), MONTH(fa.data_absencia), 1);
GO


DROP VIEW IF EXISTS dbo.vw_horas_extras_area_mes;
GO

CREATE VIEW dbo.vw_horas_extras_area_mes AS
SELECT
    a.id_area,
    a.nome_area,
    a.diretoria,
    DATEFROMPARTS(YEAR(fhe.data_hora_extra), MONTH(fhe.data_hora_extra), 1) AS mes_referencia,
    COUNT(*) AS qtd_lancamentos_horas_extras,
    COUNT(DISTINCT fhe.id_colaborador) AS qtd_colaboradores_com_hora_extra,
    SUM(fhe.horas_extras) AS total_horas_extras,
    SUM(fhe.horas_banco) AS total_horas_banco,
    AVG(fhe.horas_extras) AS media_horas_extras_por_lancamento
FROM dbo.fato_horas_extras fhe
INNER JOIN dbo.dim_colaborador c
    ON fhe.id_colaborador = c.id_colaborador
INNER JOIN dbo.dim_area a
    ON c.id_area = a.id_area
GROUP BY
    a.id_area,
    a.nome_area,
    a.diretoria,
    DATEFROMPARTS(YEAR(fhe.data_hora_extra), MONTH(fhe.data_hora_extra), 1);
GO


DROP VIEW IF EXISTS dbo.vw_turnover_area_mes;
GO

CREATE VIEW dbo.vw_turnover_area_mes AS
SELECT
    a.id_area,
    a.nome_area,
    a.diretoria,
    DATEFROMPARTS(YEAR(c.data_desligamento), MONTH(c.data_desligamento), 1) AS mes_referencia,
    COUNT(DISTINCT c.id_colaborador) AS qtd_desligamentos,
    COUNT(DISTINCT CASE 
        WHEN c.tipo_desligamento = 'Voluntário' THEN c.id_colaborador 
    END) AS qtd_desligamentos_voluntarios,
    COUNT(DISTINCT CASE 
        WHEN c.tipo_desligamento = 'Involuntário' THEN c.id_colaborador 
    END) AS qtd_desligamentos_involuntarios
FROM dbo.dim_colaborador c
INNER JOIN dbo.dim_area a
    ON c.id_area = a.id_area
WHERE c.data_desligamento IS NOT NULL
GROUP BY
    a.id_area,
    a.nome_area,
    a.diretoria,
    DATEFROMPARTS(YEAR(c.data_desligamento), MONTH(c.data_desligamento), 1);
GO