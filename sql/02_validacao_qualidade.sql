USE PeopleAnalyticsBeforeTurnover;
GO

-- 1. Contagem de registros por tabela
SELECT 'dim_area' AS tabela, COUNT(*) AS qtd_registros FROM dbo.dim_area
UNION ALL
SELECT 'dim_cargo', COUNT(*) FROM dbo.dim_cargo
UNION ALL
SELECT 'dim_colaborador', COUNT(*) FROM dbo.dim_colaborador
UNION ALL
SELECT 'fato_absenteismo', COUNT(*) FROM dbo.fato_absenteismo
UNION ALL
SELECT 'fato_horas_extras', COUNT(*) FROM dbo.fato_horas_extras;
GO

-- 2. Colaboradores sem área válida
SELECT 
    COUNT(*) AS qtd_colaboradores_sem_area_valida
FROM dbo.dim_colaborador c
LEFT JOIN dbo.dim_area a
    ON c.id_area = a.id_area
WHERE a.id_area IS NULL;
GO

-- 3. Colaboradores sem cargo válido
SELECT 
    COUNT(*) AS qtd_colaboradores_sem_cargo_valido
FROM dbo.dim_colaborador c
LEFT JOIN dbo.dim_cargo cg
    ON c.id_cargo = cg.id_cargo
WHERE cg.id_cargo IS NULL;
GO

-- 4. Registros de absenteísmo sem colaborador correspondente
SELECT 
    COUNT(*) AS qtd_absenteismo_sem_colaborador
FROM dbo.fato_absenteismo fa
LEFT JOIN dbo.dim_colaborador c
    ON fa.id_colaborador = c.id_colaborador
WHERE c.id_colaborador IS NULL;
GO

-- 5. Registros de horas extras sem colaborador correspondente
SELECT 
    COUNT(*) AS qtd_horas_extras_sem_colaborador
FROM dbo.fato_horas_extras fhe
LEFT JOIN dbo.dim_colaborador c
    ON fhe.id_colaborador = c.id_colaborador
WHERE c.id_colaborador IS NULL;
GO

-- 6. Desligamento antes da admissão
SELECT 
    COUNT(*) AS qtd_desligamento_antes_admissao
FROM dbo.dim_colaborador
WHERE data_desligamento IS NOT NULL
  AND data_desligamento < data_admissao;
GO

-- 7. Horas extras negativas
SELECT 
    COUNT(*) AS qtd_horas_extras_negativas
FROM dbo.fato_horas_extras
WHERE horas_extras < 0
   OR horas_banco < 0;
GO

-- 8. Ausências negativas
SELECT 
    COUNT(*) AS qtd_ausencias_negativas
FROM dbo.fato_absenteismo
WHERE dias_ausencia < 0
   OR horas_ausencia < 0;
GO