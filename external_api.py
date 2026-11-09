"""
Módulo de integração com APIs externas.
- Open-Meteo: irradiação solar e clima (gratuita, sem chave).
- Open-Meteo Geocoding: converte nome da cidade em coordenadas.
"""

import requests
from logger_module import log_acao

# Timeout padrão para requisições (segundos)
TIMEOUT = 10


def buscar_coordenadas(cidade, estado=""):
    """
    Busca latitude e longitude de uma cidade brasileira.
    Usa a API de geocoding do Open-Meteo (gratuita, sem chave).
    Retorna dict com name, latitude, longitude ou None.
    """
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {
        "name": cidade,
        "count": 5,
        "language": "pt",
        "country": "BR",
    }
    try:
        resp = requests.get(url, params=params, timeout=TIMEOUT)
        resp.raise_for_status()
        dados = resp.json()

        resultados = dados.get("results", [])
        if not resultados:
            log_acao("GEOCODING", f"Cidade '{cidade}' nao encontrada")
            return None

        # Se passou estado, tenta filtrar
        if estado:
            for r in resultados:
                admin = r.get("admin1", "").upper()
                if estado.upper() in admin:
                    log_acao("GEOCODING", f"'{cidade}/{estado}' -> lat={r['latitude']}, lon={r['longitude']}")
                    return {
                        "name": r.get("name", cidade),
                        "latitude": r["latitude"],
                        "longitude": r["longitude"],
                    }

        # Fallback: primeiro resultado
        r = resultados[0]
        log_acao("GEOCODING", f"'{cidade}' -> lat={r['latitude']}, lon={r['longitude']}")
        return {
            "name": r.get("name", cidade),
            "latitude": r["latitude"],
            "longitude": r["longitude"],
        }

    except requests.exceptions.RequestException as e:
        log_acao("GEOCODING", f"Erro na requisicao: {e}", "error")
        return None


def buscar_irradiacao_solar(latitude, longitude):
    """
    Busca dados de irradiação solar via Open-Meteo.
    Retorna a média diária de horas de sol equivalente (kWh/m2/dia).
    Usa dados dos últimos 30 dias para ter uma média realista.
    """
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": "shortwave_radiation_sum",
        "past_days": 30,
        "forecast_days": 1,
        "timezone": "America/Sao_Paulo",
    }
    try:
        resp = requests.get(url, params=params, timeout=TIMEOUT)
        resp.raise_for_status()
        dados = resp.json()

        radiacao_diaria = dados.get("daily", {}).get("shortwave_radiation_sum", [])
        # Filtra valores None
        valores = [v for v in radiacao_diaria if v is not None]

        if not valores:
            log_acao("IRRADIACAO", "Nenhum dado de radiacao retornado", "warning")
            return None

        # Open-Meteo retorna em MJ/m2 - converter para kWh/m2
        # 1 MJ = 0.2778 kWh
        media_mj = sum(valores) / len(valores)
        media_kwh = media_mj * 0.2778

        log_acao(
            "IRRADIACAO",
            f"lat={latitude}, lon={longitude} -> media={media_kwh:.2f} kWh/m2/dia ({len(valores)} dias)"
        )
        return round(media_kwh, 4)

    except requests.exceptions.RequestException as e:
        log_acao("IRRADIACAO", f"Erro na requisicao: {e}", "error")
        return None


def buscar_dados_climaticos(latitude, longitude):
    """
    Busca dados climáticos complementares (temperatura, umidade).
    Útil para o relatório gerado pelo LLM.
    """
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,relative_humidity_2m,cloud_cover",
        "timezone": "America/Sao_Paulo",
    }
    try:
        resp = requests.get(url, params=params, timeout=TIMEOUT)
        resp.raise_for_status()
        dados = resp.json()

        current = dados.get("current", {})
        resultado = {
            "temperatura": current.get("temperature_2m"),
            "umidade": current.get("relative_humidity_2m"),
            "cobertura_nuvens": current.get("cloud_cover"),
        }
        log_acao("CLIMA", f"lat={latitude}, lon={longitude} -> temp={resultado['temperatura']}C")
        return resultado

    except requests.exceptions.RequestException as e:
        log_acao("CLIMA", f"Erro: {e}", "error")
        return None
