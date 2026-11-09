"""
Configurações do projeto Telhado Solar Comunitário.
Carrega variáveis do .env para manter credenciais fora do código.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# --- Banco de Dados ---
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 3306)),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "telhado_solar"),
}

# --- Flask ---
FLASK_HOST = os.getenv("FLASK_HOST", "0.0.0.0")
FLASK_PORT = int(os.getenv("FLASK_PORT", 5000))
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "False").lower() in ("true", "1")

# --- LLM ---
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_API_URL = os.getenv("LLM_API_URL", "https://api.groq.com/openai/v1/chat/completions")
LLM_MODEL = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")

# --- Tarifas médias por estado (R$/kWh) - dados ANEEL 2024 ---
# Fonte: https://www.aneel.gov.br/ranking-das-tarifas
TARIFAS_POR_ESTADO = {
    "AC": 0.91, "AL": 0.85, "AM": 0.92, "AP": 0.72, "BA": 0.83,
    "CE": 0.79, "DF": 0.78, "ES": 0.80, "GO": 0.82, "MA": 0.81,
    "MG": 0.87, "MS": 0.82, "MT": 0.83, "PA": 0.88, "PB": 0.82,
    "PE": 0.80, "PI": 0.78, "PR": 0.76, "RJ": 0.93, "RN": 0.82,
    "RO": 0.85, "RR": 0.78, "RS": 0.84, "SC": 0.74, "SE": 0.81,
    "SP": 0.80, "TO": 0.80,
}

# --- Constantes de cálculo solar ---
POTENCIA_PLACA_W = 550          # Watts por placa (padrão atual)
AREA_PLACA_M2 = 2.2             # m² por placa
EFICIENCIA_SISTEMA = 0.80       # perdas (inversor, fiação, sujeira)
CUSTO_PLACA_INSTALADA = 1800.0  # R$ por placa instalada (média Brasil 2024)
DIAS_MES = 30
HORAS_SOL_PADRAO = 5.0          # fallback se API falhar
