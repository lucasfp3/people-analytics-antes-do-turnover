USE PeopleAnalyticsBeforeTurnover;
GO

DROP TABLE IF EXISTS dbo.fato_horas_extras;
DROP TABLE IF EXISTS dbo.fato_absenteismo;
DROP TABLE IF EXISTS dbo.dim_colaborador;
DROP TABLE IF EXISTS dbo.dim_cargo;
DROP TABLE IF EXISTS dbo.dim_area;
GO

CREATE TABLE dbo.dim_area (
    id_area INT NOT NULL PRIMARY KEY,
    nome_area NVARCHAR(100) NOT NULL,
    diretoria NVARCHAR(100) NOT NULL
);
GO

CREATE TABLE dbo.dim_cargo (
    id_cargo INT NOT NULL PRIMARY KEY,
    nome_cargo NVARCHAR(100) NOT NULL,
    nivel_cargo NVARCHAR(100) NOT NULL
);
GO

CREATE TABLE dbo.dim_colaborador (
    id_colaborador INT NOT NULL PRIMARY KEY,
    matricula NVARCHAR(20) NOT NULL,
    nome_colaborador NVARCHAR(150) NOT NULL,
    sexo NVARCHAR(20) NULL,
    data_nascimento DATE NULL,
    data_admissao DATE NOT NULL,
    data_desligamento DATE NULL,
    status_colaborador NVARCHAR(50) NOT NULL,
    tipo_desligamento NVARCHAR(50) NULL,
    id_area INT NOT NULL,
    id_cargo INT NOT NULL,
    id_gestor INT NULL,
    id_unidade INT NULL,

    CONSTRAINT FK_dim_colaborador_area
        FOREIGN KEY (id_area) REFERENCES dbo.dim_area(id_area),

    CONSTRAINT FK_dim_colaborador_cargo
        FOREIGN KEY (id_cargo) REFERENCES dbo.dim_cargo(id_cargo)
);
GO

CREATE TABLE dbo.fato_absenteismo (
    id_absencia INT NOT NULL PRIMARY KEY,
    id_colaborador INT NOT NULL,
    data_absencia DATE NOT NULL,
    tipo_absencia NVARCHAR(100) NOT NULL,
    justificada BIT NOT NULL,
    dias_ausencia INT NOT NULL,
    horas_ausencia DECIMAL(10,2) NOT NULL,

    CONSTRAINT FK_fato_absenteismo_colaborador
        FOREIGN KEY (id_colaborador) REFERENCES dbo.dim_colaborador(id_colaborador)
);
GO

CREATE TABLE dbo.fato_horas_extras (
    id_hora_extra INT NOT NULL PRIMARY KEY,
    id_colaborador INT NOT NULL,
    data_hora_extra DATE NOT NULL,
    horas_extras DECIMAL(10,2) NOT NULL,
    horas_banco DECIMAL(10,2) NOT NULL,
    tipo_lancamento NVARCHAR(100) NOT NULL,

    CONSTRAINT FK_fato_horas_extras_colaborador
        FOREIGN KEY (id_colaborador) REFERENCES dbo.dim_colaborador(id_colaborador)
);
GO