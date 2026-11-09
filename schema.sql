-- =============================================
-- Telhado Solar Comunitário — Schema do Banco
-- Execute este script para criar o banco manualmente
-- (o app.py também cria automaticamente ao iniciar)
-- =============================================

CREATE DATABASE IF NOT EXISTS telhado_solar
    DEFAULT CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE telhado_solar;

CREATE TABLE IF NOT EXISTS simulacoes (
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    cidade              VARCHAR(100)    NOT NULL,
    estado              CHAR(2)         NOT NULL,
    latitude            DECIMAL(10,6),
    longitude           DECIMAL(10,6),
    valor_conta         DECIMAL(10,2)   NOT NULL,
    tarifa_kwh          DECIMAL(10,4),
    consumo_kwh         DECIMAL(10,2),
    irradiacao_media    DECIMAL(10,4),
    num_placas          INT,
    custo_estimado      DECIMAL(12,2),
    economia_mensal     DECIMAL(10,2),
    tempo_retorno_meses INT,
    num_moradores       INT             DEFAULT 1,
    custo_por_pessoa    DECIMAL(12,2),
    relatorio_llm       TEXT,
    created_at          TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP       DEFAULT CURRENT_TIMESTAMP
                                        ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
