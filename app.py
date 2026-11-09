"""
Telhado Solar Comunitario - API REST com Flask
Aplicacao principal com 4 endpoints CRUD + endpoint de calculo.

ODS 13 (Acao contra mudanca do clima), ODS 11 (Cidades sustentaveis), ODS 10 (Reducao das desigualdades)
"""

from flask import Flask, request, jsonify, render_template
from database import (
    init_db, criar_simulacao, listar_simulacoes,
    buscar_simulacao, atualizar_simulacao, deletar_simulacao,
)
from external_api import buscar_coordenadas, buscar_irradiacao_solar, buscar_dados_climaticos
from solar_calc import calcular_simulacao
from llm_module import gerar_relatorio
from logger_module import log_acao
from config import FLASK_HOST, FLASK_PORT, FLASK_DEBUG, TARIFAS_POR_ESTADO

app = Flask(__name__)


# ===================== PAGINA PRINCIPAL =====================

@app.route("/")
def index():
    """Serve a interface web."""
    return render_template("index.html")


# ===================== API REST - CRUD =====================

@app.route("/api/simulacoes", methods=["GET"])
def api_listar():
    """GET - Lista todas as simulacoes salvas."""
    try:
        simulacoes = listar_simulacoes()
        for s in simulacoes:
            for k, v in s.items():
                if hasattr(v, "as_integer_ratio"):
                    s[k] = float(v)
                elif hasattr(v, "isoformat"):
                    s[k] = v.isoformat()
        return jsonify({"status": "sucesso", "dados": simulacoes}), 200
    except Exception as e:
        log_acao("API_LISTAR", f"Erro: {e}", "error")
        return jsonify({"status": "erro", "mensagem": "Erro ao listar simulacoes"}), 500


@app.route("/api/simulacoes", methods=["POST"])
def api_criar():
    """POST - Cria uma nova simulacao com calculo automatico."""
    dados = request.get_json()
    if not dados:
        return jsonify({"status": "erro", "mensagem": "Corpo da requisicao vazio"}), 400

    cidade = dados.get("cidade", "").strip()
    estado = dados.get("estado", "").strip().upper()
    valor_conta = dados.get("valor_conta")
    num_moradores = dados.get("num_moradores", 1)

    erros = []
    if not cidade:
        erros.append("Campo 'cidade' e obrigatorio")
    if not estado or len(estado) != 2:
        erros.append("Campo 'estado' deve ter 2 letras (ex: SP)")
    if valor_conta is None:
        erros.append("Campo 'valor_conta' e obrigatorio")
    else:
        try:
            valor_conta = float(valor_conta)
            if valor_conta <= 0:
                erros.append("'valor_conta' deve ser maior que zero")
            if valor_conta > 50000:
                erros.append("'valor_conta' parece acima do esperado")
        except (ValueError, TypeError):
            erros.append("'valor_conta' deve ser um numero")

    try:
        num_moradores = int(num_moradores)
        if num_moradores < 1:
            num_moradores = 1
        if num_moradores > 500:
            erros.append("'num_moradores' maximo e 500")
    except (ValueError, TypeError):
        num_moradores = 1

    if erros:
        return jsonify({"status": "erro", "mensagem": "; ".join(erros)}), 400

    try:
        coords = buscar_coordenadas(cidade, estado)
        latitude = coords["latitude"] if coords else None
        longitude = coords["longitude"] if coords else None

        irradiacao = None
        if latitude and longitude:
            irradiacao = buscar_irradiacao_solar(latitude, longitude)

        calc = calcular_simulacao(valor_conta, estado, irradiacao, num_moradores)

        registro = {
            "cidade": cidade,
            "estado": estado,
            "latitude": latitude,
            "longitude": longitude,
            "valor_conta": valor_conta,
            "num_moradores": num_moradores,
            **calc,
        }

        registro["relatorio_llm"] = gerar_relatorio(registro)

        novo_id = criar_simulacao(registro)
        registro["id"] = novo_id

        return jsonify({"status": "sucesso", "dados": registro}), 201

    except Exception as e:
        log_acao("API_CRIAR", f"Erro: {e}", "error")
        return jsonify({"status": "erro", "mensagem": "Erro interno ao processar simulacao"}), 500


@app.route("/api/simulacoes/<int:sim_id>", methods=["PUT"])
def api_atualizar(sim_id):
    """PUT - Atualiza uma simulacao existente (recalcula se necessario)."""
    dados = request.get_json()
    if not dados:
        return jsonify({"status": "erro", "mensagem": "Corpo da requisicao vazio"}), 400

    try:
        existente = buscar_simulacao(sim_id)
        if not existente:
            return jsonify({"status": "erro", "mensagem": "Simulacao nao encontrada"}), 404

        valor_conta = dados.get("valor_conta", existente.get("valor_conta"))
        estado = dados.get("estado", existente.get("estado", "SP"))
        num_moradores = dados.get("num_moradores", existente.get("num_moradores", 1))

        try:
            valor_conta = float(valor_conta)
            num_moradores = int(num_moradores)
        except (ValueError, TypeError):
            return jsonify({"status": "erro", "mensagem": "Valores invalidos"}), 400

        if valor_conta <= 0:
            return jsonify({"status": "erro", "mensagem": "'valor_conta' deve ser maior que zero"}), 400

        irradiacao = float(existente.get("irradiacao_media") or 0)
        calc = calcular_simulacao(valor_conta, estado, irradiacao, num_moradores)

        dados_update = {**dados, **calc, "valor_conta": valor_conta, "num_moradores": num_moradores}

        atualizado = atualizar_simulacao(sim_id, dados_update)
        if atualizado:
            return jsonify({"status": "sucesso", "mensagem": "Simulacao atualizada", "dados": dados_update}), 200
        else:
            return jsonify({"status": "erro", "mensagem": "Nenhuma alteracao realizada"}), 400

    except Exception as e:
        log_acao("API_ATUALIZAR", f"Erro: {e}", "error")
        return jsonify({"status": "erro", "mensagem": "Erro interno ao atualizar"}), 500


@app.route("/api/simulacoes/<int:sim_id>", methods=["DELETE"])
def api_deletar(sim_id):
    """DELETE - Remove uma simulacao pelo ID."""
    try:
        removido = deletar_simulacao(sim_id)
        if removido:
            return jsonify({"status": "sucesso", "mensagem": f"Simulacao {sim_id} removida"}), 200
        else:
            return jsonify({"status": "erro", "mensagem": "Simulacao nao encontrada"}), 404
    except Exception as e:
        log_acao("API_DELETAR", f"Erro: {e}", "error")
        return jsonify({"status": "erro", "mensagem": "Erro interno ao deletar"}), 500


# ===================== ENDPOINTS AUXILIARES =====================

@app.route("/api/calcular", methods=["POST"])
def api_calcular():
    """Endpoint rapido de calculo (nao salva no banco). Para o slider interativo."""
    dados = request.get_json()
    if not dados:
        return jsonify({"status": "erro", "mensagem": "Corpo vazio"}), 400

    cidade = dados.get("cidade", "").strip()
    estado = dados.get("estado", "SP").strip().upper()
    valor_conta = dados.get("valor_conta")
    num_moradores = dados.get("num_moradores", 1)

    if not valor_conta:
        return jsonify({"status": "erro", "mensagem": "'valor_conta' obrigatorio"}), 400

    try:
        valor_conta = float(valor_conta)
        num_moradores = int(num_moradores)
    except (ValueError, TypeError):
        return jsonify({"status": "erro", "mensagem": "Valores invalidos"}), 400

    if valor_conta <= 0:
        return jsonify({"status": "erro", "mensagem": "'valor_conta' deve ser positivo"}), 400

    try:
        irradiacao = None
        latitude = None
        longitude = None

        if cidade:
            coords = buscar_coordenadas(cidade, estado)
            if coords:
                latitude = coords["latitude"]
                longitude = coords["longitude"]
                irradiacao = buscar_irradiacao_solar(latitude, longitude)

        calc = calcular_simulacao(valor_conta, estado, irradiacao, num_moradores)
        calc["cidade"] = cidade
        calc["estado"] = estado
        calc["latitude"] = latitude
        calc["longitude"] = longitude
        calc["valor_conta"] = valor_conta

        return jsonify({"status": "sucesso", "dados": calc}), 200

    except Exception as e:
        log_acao("API_CALCULAR", f"Erro: {e}", "error")
        return jsonify({"status": "erro", "mensagem": "Erro ao calcular"}), 500


@app.route("/api/tarifas", methods=["GET"])
def api_tarifas():
    """GET - Retorna as tarifas por estado (dados ANEEL)."""
    return jsonify({"status": "sucesso", "dados": TARIFAS_POR_ESTADO}), 200


# ===================== INICIALIZACAO =====================

if __name__ == "__main__":
    log_acao("SERVIDOR", "Inicializando banco de dados...")
    init_db()
    log_acao("SERVIDOR", f"Iniciando Flask em {FLASK_HOST}:{FLASK_PORT}")
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG)
