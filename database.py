"""
Módulo de banco de dados — MySQL sem ORM, com consultas parametrizadas.
Segurança: todas as queries usam %s para evitar SQL injection.
"""

import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG
from logger_module import log_acao


def get_connection():
    """Cria e retorna uma conexão com o MySQL."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        log_acao("CONEXAO_DB", f"Falha: {e}", "error")
        raise


def init_db():
    """Cria o banco e a tabela se não existirem."""
    try:
        # Conecta sem selecionar banco para poder criá-lo
        cfg = {k: v for k, v in DB_CONFIG.items() if k != "database"}
        conn = mysql.connector.connect(**cfg)
        cursor = conn.cursor()

        cursor.execute(
            f"CREATE DATABASE IF NOT EXISTS `{DB_CONFIG['database']}` "
            "DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        )
        cursor.execute(f"USE `{DB_CONFIG['database']}`")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS simulacoes (
                id              INT AUTO_INCREMENT PRIMARY KEY,
                cidade          VARCHAR(100)   NOT NULL,
                estado          CHAR(2)        NOT NULL,
                latitude        DECIMAL(10,6),
                longitude       DECIMAL(10,6),
                valor_conta     DECIMAL(10,2)  NOT NULL,
                tarifa_kwh      DECIMAL(10,4),
                consumo_kwh     DECIMAL(10,2),
                irradiacao_media DECIMAL(10,4),
                num_placas      INT,
                custo_estimado  DECIMAL(12,2),
                economia_mensal DECIMAL(10,2),
                tempo_retorno_meses INT,
                num_moradores   INT            DEFAULT 1,
                custo_por_pessoa DECIMAL(12,2),
                relatorio_llm  TEXT,
                created_at      TIMESTAMP      DEFAULT CURRENT_TIMESTAMP,
                updated_at      TIMESTAMP      DEFAULT CURRENT_TIMESTAMP
                                               ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

        conn.commit()
        cursor.close()
        conn.close()
        log_acao("INIT_DB", "Banco e tabela criados/verificados com sucesso")
    except Error as e:
        log_acao("INIT_DB", f"Erro: {e}", "error")
        raise


# ===================== CRUD =====================


def criar_simulacao(dados):
    """INSERT — cria uma nova simulação e retorna o ID."""
    sql = """
        INSERT INTO simulacoes
            (cidade, estado, latitude, longitude, valor_conta, tarifa_kwh,
             consumo_kwh, irradiacao_media, num_placas, custo_estimado,
             economia_mensal, tempo_retorno_meses, num_moradores,
             custo_por_pessoa, relatorio_llm)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    valores = (
        dados["cidade"], dados["estado"],
        dados.get("latitude"), dados.get("longitude"),
        dados["valor_conta"], dados.get("tarifa_kwh"),
        dados.get("consumo_kwh"), dados.get("irradiacao_media"),
        dados.get("num_placas"), dados.get("custo_estimado"),
        dados.get("economia_mensal"), dados.get("tempo_retorno_meses"),
        dados.get("num_moradores", 1), dados.get("custo_por_pessoa"),
        dados.get("relatorio_llm"),
    )
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(sql, valores)
        conn.commit()
        novo_id = cursor.lastrowid
        cursor.close()
        conn.close()
        log_acao("CRIAR_SIMULACAO", f"ID {novo_id} criado para {dados['cidade']}/{dados['estado']}")
        return novo_id
    except Error as e:
        log_acao("CRIAR_SIMULACAO", f"Erro: {e}", "error")
        raise


def listar_simulacoes():
    """SELECT — retorna todas as simulações."""
    sql = "SELECT * FROM simulacoes ORDER BY created_at DESC"
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql)
        resultados = cursor.fetchall()
        cursor.close()
        conn.close()
        log_acao("LISTAR_SIMULACOES", f"{len(resultados)} registros retornados")
        return resultados
    except Error as e:
        log_acao("LISTAR_SIMULACOES", f"Erro: {e}", "error")
        raise


def buscar_simulacao(sim_id):
    """SELECT — retorna uma simulação pelo ID."""
    sql = "SELECT * FROM simulacoes WHERE id = %s"
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, (sim_id,))
        resultado = cursor.fetchone()
        cursor.close()
        conn.close()
        if resultado:
            log_acao("BUSCAR_SIMULACAO", f"ID {sim_id} encontrado")
        else:
            log_acao("BUSCAR_SIMULACAO", f"ID {sim_id} não encontrado")
        return resultado
    except Error as e:
        log_acao("BUSCAR_SIMULACAO", f"Erro: {e}", "error")
        raise


def atualizar_simulacao(sim_id, dados):
    """UPDATE — atualiza os campos de uma simulação existente."""
    campos_permitidos = [
        "cidade", "estado", "latitude", "longitude", "valor_conta",
        "tarifa_kwh", "consumo_kwh", "irradiacao_media", "num_placas",
        "custo_estimado", "economia_mensal", "tempo_retorno_meses",
        "num_moradores", "custo_por_pessoa", "relatorio_llm",
    ]
    # Filtra apenas campos válidos
    campos = {k: v for k, v in dados.items() if k in campos_permitidos}
    if not campos:
        log_acao("ATUALIZAR_SIMULACAO", "Nenhum campo válido para atualizar")
        return False

    set_clause = ", ".join(f"{k} = %s" for k in campos)
    sql = f"UPDATE simulacoes SET {set_clause} WHERE id = %s"
    valores = list(campos.values()) + [sim_id]

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(sql, valores)
        conn.commit()
        alterados = cursor.rowcount
        cursor.close()
        conn.close()
        log_acao("ATUALIZAR_SIMULACAO", f"ID {sim_id} — {alterados} linha(s) alterada(s)")
        return alterados > 0
    except Error as e:
        log_acao("ATUALIZAR_SIMULACAO", f"Erro: {e}", "error")
        raise


def deletar_simulacao(sim_id):
    """DELETE — remove uma simulação pelo ID."""
    sql = "DELETE FROM simulacoes WHERE id = %s"
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(sql, (sim_id,))
        conn.commit()
        removidos = cursor.rowcount
        cursor.close()
        conn.close()
        log_acao("DELETAR_SIMULACAO", f"ID {sim_id} — {removidos} linha(s) removida(s)")
        return removidos > 0
    except Error as e:
        log_acao("DELETAR_SIMULACAO", f"Erro: {e}", "error")
        raise
