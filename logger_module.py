"""
Módulo de logging — grava em arquivo com data/hora, ação e resultado.
Requisito do projeto: log em arquivo com data e hora, ação e resultado.
"""

import logging
import os
from datetime import datetime


def setup_logger(nome="telhado_solar", pasta_logs="logs"):
    """Configura e retorna o logger da aplicação."""
    os.makedirs(pasta_logs, exist_ok=True)

    arquivo = os.path.join(pasta_logs, f"{nome}_{datetime.now():%Y-%m-%d}.log")

    logger = logging.getLogger(nome)
    logger.setLevel(logging.INFO)

    # Evita duplicar handlers se chamar de novo
    if not logger.handlers:
        # Handler para arquivo
        fh = logging.FileHandler(arquivo, encoding="utf-8")
        fh.setLevel(logging.INFO)

        # Handler para console (útil em desenvolvimento)
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        # Formato: data/hora | nível | ação | resultado
        fmt = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        fh.setFormatter(fmt)
        ch.setFormatter(fmt)

        logger.addHandler(fh)
        logger.addHandler(ch)

    return logger


# Logger global da aplicação
log = setup_logger()


def log_acao(acao, resultado, nivel="info"):
    """Registra uma ação com seu resultado no log."""
    mensagem = f"AÇÃO: {acao} | RESULTADO: {resultado}"
    getattr(log, nivel, log.info)(mensagem)
