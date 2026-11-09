"""
Gera o relatorio PDF de ate 3 paginas para entrega da Global Solution.
Secoes: problema, cidadao, ODS, arquitetura, modelo de dados,
seguranca (3 ameacas + mitigacao), validacao e limitacoes.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
import os

# Cores
VERDE_ESCURO = HexColor("#065F46")
VERDE = HexColor("#059669")
VERDE_CLARO = HexColor("#ECFDF5")
VERDE_BORDA = HexColor("#A7F3D0")
CINZA = HexColor("#4B5563")
CINZA_CLARO = HexColor("#9CA3AF")
PRETO = HexColor("#1F2937")


def criar_estilos():
    """Cria estilos customizados para o PDF."""
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        "TituloPrincipal", parent=styles["Title"],
        fontSize=18, textColor=VERDE_ESCURO, alignment=TA_CENTER,
        spaceAfter=2*mm, fontName="Helvetica-Bold",
    ))
    styles.add(ParagraphStyle(
        "Subtitulo", parent=styles["Normal"],
        fontSize=10, textColor=CINZA_CLARO, alignment=TA_CENTER,
        spaceAfter=4*mm,
    ))
    styles.add(ParagraphStyle(
        "TituloSecao", parent=styles["Heading2"],
        fontSize=12, textColor=VERDE_ESCURO, fontName="Helvetica-Bold",
        spaceBefore=5*mm, spaceAfter=2*mm,
        borderWidth=0, leftIndent=0,
    ))
    styles.add(ParagraphStyle(
        "SubtituloSecao", parent=styles["Heading3"],
        fontSize=10, textColor=PRETO, fontName="Helvetica-Bold",
        spaceBefore=3*mm, spaceAfter=1*mm,
    ))
    styles.add(ParagraphStyle(
        "Corpo", parent=styles["Normal"],
        fontSize=9, textColor=CINZA, alignment=TA_JUSTIFY,
        leading=13, spaceAfter=2*mm,
    ))
    styles.add(ParagraphStyle(
        "Item", parent=styles["Normal"],
        fontSize=9, textColor=CINZA, alignment=TA_LEFT,
        leading=13, leftIndent=8*mm, bulletIndent=3*mm,
        spaceAfter=1*mm,
    ))
    styles.add(ParagraphStyle(
        "DestaqueTitulo", parent=styles["Normal"],
        fontSize=9, textColor=VERDE_ESCURO, fontName="Helvetica-Bold",
        leading=12, spaceAfter=0.5*mm,
    ))
    styles.add(ParagraphStyle(
        "DestaqueCorpo", parent=styles["Normal"],
        fontSize=8.5, textColor=CINZA, alignment=TA_JUSTIFY,
        leading=12,
    ))
    styles.add(ParagraphStyle(
        "Rodape", parent=styles["Normal"],
        fontSize=8, textColor=CINZA_CLARO, alignment=TA_CENTER,
    ))
    return styles


def destaque_box(titulo, texto, styles, elements):
    """Cria uma caixa destacada com fundo verde claro."""
    conteudo = [[
        Paragraph(f"<b>{titulo}</b>", styles["DestaqueTitulo"]),
    ], [
        Paragraph(texto, styles["DestaqueCorpo"]),
    ]]
    t = Table(conteudo, colWidths=[170*mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), VERDE_CLARO),
        ("BOX", (0, 0), (-1, -1), 0.5, VERDE_BORDA),
        ("TOPPADDING", (0, 0), (-1, 0), 3*mm),
        ("BOTTOMPADDING", (0, -1), (-1, -1), 3*mm),
        ("LEFTPADDING", (0, 0), (-1, -1), 3*mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3*mm),
    ]))
    elements.append(KeepTogether([t, Spacer(1, 2*mm)]))


def gerar():
    caminho = os.path.join(os.path.dirname(os.path.abspath(__file__)), "relatorio_global_solution.pdf")

    doc = SimpleDocTemplate(
        caminho, pagesize=A4,
        topMargin=18*mm, bottomMargin=15*mm,
        leftMargin=15*mm, rightMargin=15*mm,
    )

    styles = criar_estilos()
    elements = []

    def linha_verde():
        elements.append(HRFlowable(
            width="40%", thickness=1, color=VERDE,
            spaceAfter=2*mm, spaceBefore=0,
        ))

    def secao(titulo):
        elements.append(Paragraph(titulo, styles["TituloSecao"]))
        linha_verde()

    def subsecao(titulo):
        elements.append(Paragraph(titulo, styles["SubtituloSecao"]))

    def corpo(texto):
        elements.append(Paragraph(texto, styles["Corpo"]))

    def item(texto):
        elements.append(Paragraph(f"• {texto}", styles["Item"]))

    # ============================
    # TITULO
    # ============================
    elements.append(Paragraph("Telhado Solar Comunitário", styles["TituloPrincipal"]))
    elements.append(Paragraph(
        "Calculadora interativa de energia solar para comunidades de baixa renda",
        styles["Subtitulo"]
    ))
    elements.append(Paragraph(
        "Disciplina: Coding for Security | FIAP 2026 | Global Solution — CitizenTech",
        styles["Subtitulo"]
    ))
    elements.append(HRFlowable(width="100%", thickness=1, color=VERDE, spaceAfter=4*mm))

    # ============================
    # 1. PROBLEMA
    # ============================
    secao("1. Problema")
    corpo(
        "Moradores de baixa renda no Brasil pagam proporcionalmente mais pela energia elétrica "
        "do que a classe média e alta. A tarifa social atinge apenas parte da população elegível, "
        "e muitos não conhecem alternativas como a energia solar fotovoltaica, que se tornou "
        "economicamente viável nos últimos anos."
    )
    corpo(
        "A principal barreira não é tecnológica, mas informacional: o cidadão não sabe quanto "
        "custa um sistema solar, quanto economizaria por mês, em quanto tempo o investimento "
        "se paga, nem que é possível formar cooperativas solares para reduzir o custo por pessoa. "
        "Segundo a ANEEL, o Brasil atingiu 2 milhões de sistemas de geração distribuída em 2024, "
        "mas a concentração está em classes A e B."
    )

    # ============================
    # 2. CIDADAO
    # ============================
    secao("2. Cidadão Beneficiado")
    corpo(
        "O cidadão-alvo é o morador de comunidade, bairro periférico ou zona rural que paga "
        "conta de luz alta (R$150 a R$500/mês) e não tem acesso a informações sobre energia solar. "
        "Também atende líderes comunitários que podem organizar cooperativas solares em seus bairros."
    )
    corpo(
        "Perfil: renda familiar de 1 a 3 salários mínimos, ensino médio completo ou incompleto, "
        "acesso a internet por celular. A interface foi projetada para ser simples, "
        "visual e autoexplicativa, com linguagem acessível e sem jargão técnico."
    )

    # ============================
    # 3. ODS
    # ============================
    secao("3. ODS Relacionados")
    destaque_box(
        "ODS 13 — Ação contra a mudança global do clima",
        "A energia solar reduz a emissão de CO2 ao substituir fontes fósseis. "
        "O sistema incentiva a adoção de energia limpa em comunidades que normalmente "
        "não teriam acesso a essa informação.",
        styles, elements
    )
    destaque_box(
        "ODS 11 — Cidades e comunidades sustentáveis",
        "Cooperativas solares tornam bairros mais sustentáveis e autossuficientes "
        "energeticamente, reduzindo a dependência da rede e a vulnerabilidade a aumentos tarifários.",
        styles, elements
    )
    destaque_box(
        "ODS 10 — Redução das desigualdades",
        "Democratiza o acesso à energia solar — hoje restrita às classes A e B — por "
        "meio de informação clara e do modelo cooperativo que divide custos.",
        styles, elements
    )

    # ============================
    # 4. ARQUITETURA
    # ============================
    secao("4. Arquitetura e Modelo de Dados")

    subsecao("Arquitetura")
    corpo(
        "Aplicação web monolítica com separação em módulos Python:"
    )
    item("app.py: servidor Flask com 6 rotas (4 CRUD + cálculo + tarifas)")
    item("database.py: conexão MySQL com CRUD via queries parametrizadas (sem ORM)")
    item("external_api.py: integração com Open-Meteo (geocoding + irradiação solar)")
    item("solar_calc.py: lógica de dimensionamento e economia")
    item("llm_module.py: geração de relatório com LLM (Groq) ou template fallback")
    item("logger_module.py: logging em arquivo com data/hora/ação/resultado")
    item("Frontend: HTML5 + CSS3 + JavaScript puro com SVG interativo")

    subsecao("Modelo de Dados — Tabela simulacoes")
    corpo(
        "Campos: id (PK auto_increment), cidade (VARCHAR 100), estado (CHAR 2), "
        "latitude/longitude (DECIMAL 10,6), valor_conta (DECIMAL 10,2), "
        "tarifa_kwh (DECIMAL 10,4), consumo_kwh (DECIMAL 10,2), "
        "irradiacao_media (DECIMAL 10,4), num_placas (INT), custo_estimado (DECIMAL 12,2), "
        "economia_mensal (DECIMAL 10,2), tempo_retorno_meses (INT), "
        "num_moradores (INT default 1), custo_por_pessoa (DECIMAL 12,2), "
        "relatorio_llm (TEXT), created_at/updated_at (TIMESTAMP)."
    )

    subsecao("API Externa — Open-Meteo (gratuita, sem chave)")
    item("Geocoding: converte nome da cidade em latitude/longitude")
    item("Forecast: irradiação solar (shortwave_radiation_sum) dos últimos 30 dias, convertida de MJ/m² para kWh/m²/dia (fator 0.2778)")
    item("Current Weather: temperatura, umidade e cobertura de nuvens (dados complementares)")

    subsecao("Fluxo de Cálculo")
    item("Usuário informa cidade, estado e valor da conta de luz")
    item("Sistema busca coordenadas e irradiação solar via Open-Meteo")
    item("consumo_kWh = valor_conta / tarifa_estado (dados ANEEL)")
    item("energia_placa_mês = potência(0.55kW) × horas_sol × 30 × eficiência(0.80)")
    item("num_placas = consumo / energia_placa_mês (arredondado para cima)")
    item("Custo total = num_placas × R$1.800 | Economia = 90% da conta | Retorno = custo/economia")

    # ============================
    # 5. SEGURANCA
    # ============================
    secao("5. Segurança e Privacidade")

    subsecao("Medidas Implementadas")
    item("Credenciais (senha MySQL, chave LLM) em .env, fora do versionamento (.gitignore)")
    item("Todas as queries SQL usam parâmetros (%s), prevenindo SQL Injection")
    item("Validação de toda entrada: tipo, tamanho, intervalo (valor_conta > 0 e < 50000)")
    item("Mensagens de erro genéricas — erros internos logados mas não expostos")
    item("Coleta mínima: apenas cidade, estado e valor da conta (sem CPF, nome ou endereço) — LGPD")

    elements.append(Spacer(1, 2*mm))
    subsecao("Três Ameaças e Mitigações")

    destaque_box(
        "Ameaça 1: SQL Injection",
        "Risco: atacante insere comandos SQL nos campos (ex: cidade = \"'; DROP TABLE simulacoes;\"). "
        "Mitigação: queries parametrizadas com %s do mysql-connector-python. "
        "Valores são dados, nunca parte do comando SQL. Campo estado validado para 2 caracteres.",
        styles, elements
    )
    destaque_box(
        "Ameaça 2: Exposição de credenciais no código-fonte",
        "Risco: credenciais hardcoded dariam acesso ao banco a qualquer pessoa com o repositório. "
        "Mitigação: credenciais no .env (no .gitignore). Repositório contém apenas .env.example com placeholders.",
        styles, elements
    )
    destaque_box(
        "Ameaça 3: Abuso da API (rate limiting / DDoS)",
        "Risco: milhares de requisições ao /api/calcular sobrecarregam servidor e Open-Meteo. "
        "Mitigação: validação rejeita requests malformados. Em produção: flask-limiter (10 req/min/IP) e CORS restrito.",
        styles, elements
    )

    # ============================
    # 6. VALIDACAO
    # ============================
    secao("6. Validação e Limitações")
    corpo(
        "A solução foi validada com dados reais da API Open-Meteo para São Paulo/SP. "
        "A irradiação retornada (4.8 kWh/m²/dia) é consistente com o Atlas "
        "Solarimétrico do INPE para o Sudeste (4.5 a 5.5 kWh/m²/dia). "
        "Teste: conta de R$300/mês em SP resulta em 6 placas de 550W, "
        "economia de R$270/mês e retorno em 40 meses (3.3 anos)."
    )
    subsecao("Limitações")
    item("Tarifas são médias estaduais (ANEEL), não a tarifa exata da distribuidora")
    item("Cálculo não considera sombreamento, orientação do telhado ou manutenção")
    item("Custo por placa (R$1.800) é média e varia por região")
    item("Em produção: necessária autenticação e rate limiting")
    item("Módulo LLM depende de API externa (Groq); sem chave, usa template local")

    # ============================
    # 7. USO DE IA
    # ============================
    secao("7. Uso de IA Generativa")
    corpo(
        "Este projeto utilizou IA generativa (Claude, Anthropic) como ferramenta de apoio "
        "para: estruturação do código e boas práticas de segurança, depuração de erros, "
        "e geração de ideias para a interface visual interativa (SVG da casinha com placas solares). "
        "Todo o código foi revisado, compreendido e pode ser explicado na arguição."
    )
    corpo(
        "O módulo LLM integrado (llm_module.py) utiliza a API do Groq "
        "(modelo Llama 3.3 70B) para gerar relatórios explicativos em linguagem simples. "
        "Na ausência da chave de API, o sistema gera um relatório template funcional."
    )

    # ============================
    # GERAR
    # ============================
    doc.build(elements)
    print(f"Relatorio gerado: {caminho}")
    return caminho


if __name__ == "__main__":
    gerar()
