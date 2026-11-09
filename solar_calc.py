"""
Módulo de cálculo solar - toda a lógica de dimensionamento e economia.
Transforma os dados brutos em informações úteis para o morador.
"""

import math
from config import (
    TARIFAS_POR_ESTADO,
    POTENCIA_PLACA_W,
    EFICIENCIA_SISTEMA,
    CUSTO_PLACA_INSTALADA,
    DIAS_MES,
    HORAS_SOL_PADRAO,
)
from logger_module import log_acao


def obter_tarifa(estado):
    """Retorna a tarifa média do estado em R$/kWh."""
    estado = estado.upper().strip()
    tarifa = TARIFAS_POR_ESTADO.get(estado, 0.80)  # fallback nacional
    log_acao("TARIFA", f"Estado {estado} -> R${tarifa}/kWh")
    return tarifa


def calcular_consumo_kwh(valor_conta, tarifa_kwh):
    """Estima o consumo mensal em kWh a partir do valor da conta."""
    if tarifa_kwh <= 0:
        tarifa_kwh = 0.80
    consumo = valor_conta / tarifa_kwh
    return round(consumo, 2)


def calcular_num_placas(consumo_kwh, irradiacao_diaria):
    """
    Calcula quantas placas solares são necessárias.

    Fórmula:
        energia_placa_mes = potencia_placa(kW) x horas_sol_dia x 30 x eficiência
        num_placas = consumo_mensal / energia_placa_mes
    """
    if irradiacao_diaria is None or irradiacao_diaria <= 0:
        irradiacao_diaria = HORAS_SOL_PADRAO

    # Horas de sol pico = irradiação em kWh/m2/dia (já é equivalente)
    horas_sol = irradiacao_diaria

    potencia_kw = POTENCIA_PLACA_W / 1000  # 0.55 kW
    energia_placa_mes = potencia_kw * horas_sol * DIAS_MES * EFICIENCIA_SISTEMA

    if energia_placa_mes <= 0:
        return 1

    num = math.ceil(consumo_kwh / energia_placa_mes)
    return max(num, 1)


def calcular_simulacao(valor_conta, estado, irradiacao_diaria=None, num_moradores=1):
    """
    Cálculo completo da simulação solar para cooperativa.

    valor_conta = média da conta de luz por casa
    num_moradores = quantas casas participam da cooperativa
    """
    tarifa = obter_tarifa(estado)
    consumo_por_casa = calcular_consumo_kwh(valor_conta, tarifa)

    if irradiacao_diaria is None or irradiacao_diaria <= 0:
        irradiacao_diaria = HORAS_SOL_PADRAO

    if num_moradores < 1:
        num_moradores = 1

    # Consumo total da cooperativa
    consumo_total = consumo_por_casa * num_moradores

    # Placas para toda a cooperativa
    placas_total = calcular_num_placas(consumo_total, irradiacao_diaria)
    placas_por_casa = math.ceil(placas_total / num_moradores)

    # Produção real das placas (kWh/mês)
    horas_sol = irradiacao_diaria
    potencia_kw = POTENCIA_PLACA_W / 1000
    energia_placa_mes = potencia_kw * horas_sol * DIAS_MES * EFICIENCIA_SISTEMA
    producao_total = placas_total * energia_placa_mes
    producao_por_casa = producao_total / num_moradores

    # Economia baseada na produção real (não fixa em 90%)
    economia_por_casa = min(producao_por_casa * tarifa, valor_conta)
    economia_total = economia_por_casa * num_moradores
    percentual_economia = round((economia_por_casa / valor_conta) * 100, 1) if valor_conta > 0 else 0

    # Custos
    custo_total = placas_total * CUSTO_PLACA_INSTALADA
    custo_por_pessoa = round(custo_total / num_moradores, 2)

    # Financiamento em múltiplos prazos (taxa 1.2% a.m.)
    taxa_mensal = 0.012
    prazos = [24, 36, 48, 60]
    opcoes_financiamento = []
    for n_parcelas in prazos:
        parcela = custo_por_pessoa * (taxa_mensal * (1 + taxa_mensal)**n_parcelas) / ((1 + taxa_mensal)**n_parcelas - 1)
        parcela = round(parcela, 2)
        total_pago = round(parcela * n_parcelas, 2)
        juros_total = round(total_pago - custo_por_pessoa, 2)
        saldo_mensal = round(economia_por_casa - parcela, 2)
        opcoes_financiamento.append({
            "meses": n_parcelas,
            "parcela": parcela,
            "total_pago": total_pago,
            "juros_total": juros_total,
            "saldo_mensal": saldo_mensal,
        })

    parcela_60 = opcoes_financiamento[-1]["parcela"]

    # Tempo de retorno (à vista)
    if economia_por_casa > 0:
        tempo_retorno = math.ceil(custo_por_pessoa / economia_por_casa)
    else:
        tempo_retorno = 0

    # Projeção 25 anos (vida útil das placas)
    meses_vida_util = 25 * 12
    economia_25_anos = round(economia_por_casa * meses_vida_util, 2)
    lucro_liquido_vista = round(economia_25_anos - custo_por_pessoa, 2)
    lucro_liquido_financiado = round(economia_25_anos - opcoes_financiamento[-1]["total_pago"], 2)

    resultado = {
        "tarifa_kwh": tarifa,
        "consumo_kwh": round(consumo_por_casa, 2),
        "consumo_total_kwh": round(consumo_total, 2),
        "irradiacao_media": irradiacao_diaria,
        "num_placas": placas_total,
        "placas_por_casa": placas_por_casa,
        "producao_kwh_mes": round(producao_por_casa, 2),
        "custo_estimado": round(custo_total, 2),
        "custo_por_pessoa": custo_por_pessoa,
        "parcela_mensal": parcela_60,
        "economia_mensal": round(economia_por_casa, 2),
        "economia_total": round(economia_total, 2),
        "percentual_economia": percentual_economia,
        "tempo_retorno_meses": tempo_retorno,
        "num_moradores": num_moradores,
        "opcoes_financiamento": opcoes_financiamento,
        "economia_25_anos": economia_25_anos,
        "lucro_liquido_vista": lucro_liquido_vista,
        "lucro_liquido_financiado": lucro_liquido_financiado,
    }

    log_acao(
        "CALCULO_SOLAR",
        f"Conta R${valor_conta} | {estado} | {num_moradores} casas | "
        f"{placas_total} placas | Economia R${economia_por_casa:.0f}/casa/mes | "
        f"Retorno {tempo_retorno} meses"
    )
    return resultado
