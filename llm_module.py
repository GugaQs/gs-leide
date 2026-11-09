"""
Módulo de integração com LLM (Large Language Model).
Usa API compatível com OpenAI (Groq é gratuito e rápido).
Gera relatórios explicativos em linguagem simples para o morador.

Se a chave não estiver configurada, gera um relatório template sem LLM.
"""

import requests
from config import LLM_API_KEY, LLM_API_URL, LLM_MODEL
from logger_module import log_acao

TIMEOUT = 30


def gerar_relatorio(dados_simulacao):
    """
    Gera um relatório explicativo sobre a simulação solar.
    Se LLM estiver configurado, usa IA. Senão, usa template.
    """
    if LLM_API_KEY and LLM_API_KEY != "sua_chave_aqui":
        return _gerar_com_llm(dados_simulacao)
    else:
        return _gerar_template(dados_simulacao)


def _gerar_com_llm(dados):
    """Gera relatório usando LLM via API."""
    moradores = dados.get('num_moradores', 1)
    economia = dados.get('economia_mensal', 0)
    parcela = dados.get('parcela_mensal', 0)
    saldo = economia - parcela
    custo_pessoa = dados.get('custo_por_pessoa', 0)
    economia_25 = dados.get('economia_25_anos', economia * 300)
    lucro_vista = dados.get('lucro_liquido_vista', economia_25 - custo_pessoa)

    prompt = f"""Você é um consultor de energia solar comunitária.
Gere um relatório CURTO e em linguagem SIMPLES para um morador de baixa renda.
Use no máximo 300 palavras. Sem jargão técnico. Seja direto e amigável.

Dados da simulação:
- Cidade/Estado: {dados.get('cidade', 'N/A')}/{dados.get('estado', 'N/A')}
- Valor atual da conta de luz: R${dados.get('valor_conta', 0):.2f}/mês
- Tarifa da região: R${dados.get('tarifa_kwh', 0):.2f}/kWh
- Consumo estimado: {dados.get('consumo_kwh', 0):.0f} kWh/mês
- Irradiação solar média: {dados.get('irradiacao_media', 0):.1f} kWh/m²/dia
- Produção solar por casa: {dados.get('producao_kwh_mes', 0):.0f} kWh/mês
- Placas necessárias: {dados.get('num_placas', 0)} ({dados.get('placas_por_casa', 0)} por telhado)
- Custo estimado do sistema: R${dados.get('custo_estimado', 0):,.2f}
- Economia mensal estimada: R${economia:.2f} ({dados.get('percentual_economia', 0)}% da conta)
- Tempo de retorno (à vista): {dados.get('tempo_retorno_meses', 0)} meses
- Moradores na cooperativa: {moradores}
- Investimento por casa (à vista): R${custo_pessoa:,.2f}
- Parcela mensal (60x, juros 1,2%/mês): R${parcela:.2f}
- Saldo mensal (economia - parcela): R${saldo:.2f}
- Economia total em 25 anos: R${economia_25:,.2f}
- Lucro líquido em 25 anos (à vista): R${lucro_vista:,.2f}

Estruture assim:
1. Resumo (2 frases)
2. Dados da Região (tarifa, irradiação, consumo)
3. Economia (quanto vai economizar por mês e percentual da conta)
4. Investimento por Casa (valor à vista, parcela mensal, saldo mensal e se vale a pena financiar)
5. Visão de Longo Prazo (economia em 25 anos, lucro líquido)
6. Próximos passos (o que fazer agora)"""

    headers = {
        "Authorization": f"Bearer {LLM_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": LLM_MODEL,
        "messages": [
            {"role": "system", "content": "Você é um consultor de energia solar que explica de forma simples."},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": 500,
        "temperature": 0.7,
    }

    try:
        resp = requests.post(LLM_API_URL, json=payload, headers=headers, timeout=TIMEOUT)
        resp.raise_for_status()
        resultado = resp.json()

        texto = resultado["choices"][0]["message"]["content"]
        log_acao("LLM_RELATORIO", f"Relatório gerado com sucesso ({len(texto)} chars)")
        return texto

    except requests.exceptions.RequestException as e:
        log_acao("LLM_RELATORIO", f"Erro na API LLM: {e}", "error")
        return _gerar_template(dados)
    except (KeyError, IndexError) as e:
        log_acao("LLM_RELATORIO", f"Resposta inesperada da API: {e}", "error")
        return _gerar_template(dados)


def _gerar_template(dados):
    """Gera relatório usando template (fallback sem LLM)."""
    log_acao("LLM_RELATORIO", "Usando template (LLM não configurado)")

    economia = dados.get("economia_mensal", 0)
    economia_anual = economia * 12
    tempo = dados.get("tempo_retorno_meses", 0)
    tempo_anos = tempo / 12
    moradores = dados.get("num_moradores", 1)
    parcela = dados.get("parcela_mensal", 0)
    saldo = economia - parcela
    custo_pessoa = dados.get("custo_por_pessoa", 0)
    percentual = dados.get("percentual_economia", 0)
    economia_25 = dados.get("economia_25_anos", economia * 300)
    lucro_vista = dados.get("lucro_liquido_vista", economia_25 - custo_pessoa)
    lucro_fin = dados.get("lucro_liquido_financiado", economia_25 - (parcela * 60))

    texto = f"""📊 RELATÓRIO DA SUA SIMULAÇÃO SOLAR

🏠 Resumo
Com base na sua conta de luz de R${dados.get('valor_conta', 0):.2f} por mês e na quantidade de sol que a sua região recebe, estimamos que você precisa de {dados.get('num_placas', 0)} placas solares.

📍 Dados da Região
• Tarifa de energia: R${dados.get('tarifa_kwh', 0):.2f}/kWh
• Irradiação solar: {dados.get('irradiacao_media', 0):.1f} kWh/m²/dia
• Seu consumo estimado: {dados.get('consumo_kwh', 0):.0f} kWh/mês
• Produção solar por casa: {dados.get('producao_kwh_mes', 0):.0f} kWh/mês

💰 Economia
Você pode economizar R${economia:.2f} por mês — isso cobre {percentual}% da sua conta de luz. Em um ano, são R${economia_anual:,.2f} no seu bolso.

☀️ Sistema Solar
• {dados.get('num_placas', 0)} placas no total ({dados.get('placas_por_casa', 0)} por telhado)
• Custo total do sistema: R${dados.get('custo_estimado', 0):,.2f}"""

    if moradores > 1:
        texto += f"""
• Com {moradores} casas na cooperativa, cada uma paga R${custo_pessoa:,.2f}"""

    texto += f"""

🏠 Investimento por Casa
• À vista: R${custo_pessoa:,.2f}
• Financiado em 60x (juros 1,2%/mês): R${parcela:.2f}/mês"""

    if saldo >= 0:
        texto += f"""
• Saldo mensal: +R${saldo:.2f} (economia R${economia:.2f} - parcela R${parcela:.2f})
✅ Vale a pena financiar! Você já economiza desde o primeiro mês."""
    else:
        texto += f"""
• Saldo mensal: -R${abs(saldo):.2f} (economia R${economia:.2f} - parcela R${parcela:.2f})
⚠️ A parcela é maior que a economia. Considere pagar à vista ou juntar mais vizinhos."""

    texto += f"""

🔮 Visão de Longo Prazo (25 anos)
As placas solares duram mais de 25 anos. Nesse período:
• Economia total: R${economia_25:,.2f}
• Lucro líquido (à vista): R${lucro_vista:,.2f}
• Lucro líquido (financiado 60x): R${lucro_fin:,.2f}
O investimento se paga em {tempo} meses ({tempo_anos:.1f} anos). Depois disso, a economia de R${economia:.2f}/mês é lucro puro.

✅ Próximos passos
1. Converse com seus vizinhos sobre montar uma cooperativa solar
2. Procure empresas de energia solar na sua região para orçamentos
3. Verifique se há linhas de crédito disponíveis (BNDES, Banco do Nordeste)
4. Consulte a distribuidora de energia sobre as regras de geração distribuída"""

    return texto
