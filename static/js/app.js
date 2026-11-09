/**
 * Telhado Solar Comunitário — Frontend Interativo
 * Casinha SVG com placas solares que aparecem conforme o slider muda.
 */

// ===================== ESTADO =====================
let dadosAtuais = null; // último cálculo recebido da API
let irradiacaoCache = {}; // cache de irradiação por cidade+estado

// ===================== INICIALIZAÇÃO =====================
document.addEventListener("DOMContentLoaded", () => {
    // Sliders
    const sliderValor = document.getElementById("valorConta");
    const sliderMoradores = document.getElementById("numMoradores");

    sliderValor.addEventListener("input", () => {
        document.getElementById("valorContaDisplay").textContent = sliderValor.value;
        atualizarCasaLocal();
    });

    sliderMoradores.addEventListener("input", () => {
        document.getElementById("numMoradoresDisplay").textContent = sliderMoradores.value;
        atualizarCasaLocal();
    });

    // Desenha a casa inicial com os valores atuais do slider
    atualizarCasaLocal();

    // Carrega histórico
    carregarHistorico();
});


// ===================== VISTA AÉREA — COMUNIDADE SOLAR =====================

const PLACAS_POR_TELHADO = 6;
const CORES_CASAS = [
    { parede: "#F5E6D3", telhado: "#9CA3AF", telhado2: "#6B7280" },
    { parede: "#E8D5C4", telhado: "#A1887F", telhado2: "#8D6E63" },
    { parede: "#DBEAFE", telhado: "#78909C", telhado2: "#607D8B" },
    { parede: "#FDE68A", telhado: "#A1887F", telhado2: "#795548" },
    { parede: "#D1FAE5", telhado: "#90A4AE", telhado2: "#78909C" },
    { parede: "#FCE7F3", telhado: "#B0BEC5", telhado2: "#90A4AE" },
];

function desenharCasa(numPlacas) {
    const totalPlacas = Math.max(0, numPlacas);
    const numCasas = totalPlacas === 0 ? 1 : Math.ceil(totalPlacas / PLACAS_POR_TELHADO);
    const casasVisiveis = Math.min(numCasas, 12);

    // Layout: calcular grid de casas
    let cols, rows;
    if (casasVisiveis <= 1) { cols = 1; rows = 1; }
    else if (casasVisiveis <= 2) { cols = 2; rows = 1; }
    else if (casasVisiveis <= 4) { cols = 2; rows = 2; }
    else if (casasVisiveis <= 6) { cols = 3; rows = 2; }
    else if (casasVisiveis <= 9) { cols = 3; rows = 3; }
    else { cols = 4; rows = 3; }

    // Dimensões dinâmicas
    const casaW = casasVisiveis <= 2 ? 130 : (casasVisiveis <= 6 ? 100 : 80);
    const casaH = casasVisiveis <= 2 ? 100 : (casasVisiveis <= 6 ? 80 : 65);
    const gap = casasVisiveis <= 2 ? 30 : (casasVisiveis <= 6 ? 20 : 15);
    const ruaH = 22;

    const gridW = cols * casaW + (cols - 1) * gap;
    const gridH = rows * (casaH + ruaH + 10);
    const w = Math.max(460, gridW + 60);
    const h = Math.max(300, gridH + 80);

    let svg = `<svg viewBox="0 0 ${w} ${h}" xmlns="http://www.w3.org/2000/svg" style="max-width:480px;">`;

    // Defs
    svg += `<defs>
        <linearGradient id="grama" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="#86EFAC"/>
            <stop offset="100%" stop-color="#4ADE80"/>
        </linearGradient>
        <linearGradient id="placa" x1="0" y1="0" x2="0.3" y2="1">
            <stop offset="0%" stop-color="#1E3A5F"/>
            <stop offset="50%" stop-color="#1E40AF"/>
            <stop offset="100%" stop-color="#1E3A5F"/>
        </linearGradient>
        <filter id="sombra">
            <feDropShadow dx="1.5" dy="2" stdDeviation="2" flood-opacity="0.12"/>
        </filter>
        <filter id="sombraPlaca">
            <feDropShadow dx="0.5" dy="0.5" stdDeviation="0.5" flood-opacity="0.15"/>
        </filter>
    </defs>`;

    // Fundo gramado
    svg += `<rect x="0" y="0" width="${w}" height="${h}" fill="url(#grama)" rx="8"/>`;
    for (let i = 0; i < Math.ceil(h / 30); i++) {
        svg += `<line x1="0" y1="${15 + i*30}" x2="${w}" y2="${15 + i*30}" stroke="#6EE7A0" stroke-width="0.4" opacity="0.35"/>`;
    }

    // Árvores nos cantos
    svg += desenharArvore(25, 25, 14);
    svg += desenharArvore(w - 25, 30, 12);
    if (h > 350) svg += desenharArvore(20, h - 40, 11);

    // Offset para centralizar o grid
    const offX = (w - gridW) / 2;
    const offY = 30;

    let placasColocadas = 0;

    for (let r = 0; r < rows; r++) {
        // Rua horizontal antes de cada fileira
        const ruaY = offY + r * (casaH + ruaH + 10);
        svg += `<rect x="10" y="${ruaY}" width="${w - 20}" height="${ruaH}" fill="#94A3B8" rx="3" opacity="0.5"/>`;
        svg += `<line x1="15" y1="${ruaY + ruaH/2}" x2="${w-15}" y2="${ruaY + ruaH/2}" stroke="#CBD5E1" stroke-width="1.5" stroke-dasharray="8,6" opacity="0.6"/>`;

        for (let c = 0; c < cols; c++) {
            const idx = r * cols + c;
            if (idx >= casasVisiveis) break;

            const cx = offX + c * (casaW + gap);
            const cy = ruaY + ruaH + 5;
            const cor = CORES_CASAS[idx % CORES_CASAS.length];

            const placasNestaCasa = Math.min(
                PLACAS_POR_TELHADO,
                Math.max(0, totalPlacas - placasColocadas)
            );

            svg += desenharCasaUnit(cx, cy, casaW, casaH, cor, placasNestaCasa, placasColocadas * 0.04, casasVisiveis);
            placasColocadas += placasNestaCasa;
        }
    }

    // Indicador: casas extras não visíveis
    if (numCasas > casasVisiveis) {
        const extras = numCasas - casasVisiveis;
        svg += `<text x="${w/2}" y="${h - 28}" text-anchor="middle" font-size="11" font-family="Inter,sans-serif" font-weight="600" fill="#065F46" opacity="0.8">+ ${extras} casa${extras > 1 ? 's' : ''} na comunidade</text>`;
    }

    // Legenda
    if (totalPlacas > 0) {
        const casasUsadas = Math.min(numCasas, casasVisiveis);
        let legenda = `${totalPlacas} placas · ${numCasas} telhado${numCasas > 1 ? 's' : ''}`;
        if (numCasas > 1) legenda += ` · ${PLACAS_POR_TELHADO}/telhado`;
        svg += `<text x="${w/2}" y="${h - 10}" text-anchor="middle" font-size="10" font-family="Inter,sans-serif" font-weight="600" fill="#065F46" opacity="0.7">${legenda}</text>`;
    }

    svg += `</svg>`;
    document.getElementById("houseContainer").innerHTML = svg;
}


function desenharCasaUnit(x, y, w, h, cor, numPlacas, delayBase, totalCasas) {
    let s = "";
    const escala = totalCasas <= 2 ? 1 : (totalCasas <= 6 ? 0.85 : 0.7);

    // Sombra 3D (paredes visíveis)
    const d3 = Math.round(4 * escala);
    s += `<g filter="url(#sombra)">`;
    s += `<path d="M ${x+w},${y+d3} L ${x+w+d3},${y+d3*2} L ${x+w+d3},${y+h+d3*2} L ${x+w},${y+h+d3}" fill="#D1D5DB" stroke="#D1D5DB" stroke-width="0.3"/>`;
    s += `<path d="M ${x},${y+h+d3} L ${x+d3},${y+h+d3*2} L ${x+w+d3},${y+h+d3*2} L ${x+w},${y+h+d3}" fill="#E5E7EB" stroke="#D1D5DB" stroke-width="0.3"/>`;

    // Telhado
    s += `<rect x="${x}" y="${y}" width="${w}" height="${h}" fill="${cor.telhado}" stroke="${cor.telhado2}" stroke-width="1" rx="2"/>`;
    // Cumeeira
    s += `<line x1="${x}" y1="${y+h/2}" x2="${x+w}" y2="${y+h/2}" stroke="${cor.telhado2}" stroke-width="0.8" stroke-dasharray="3,2" opacity="0.5"/>`;
    s += `</g>`;

    // Porta (retângulo na base)
    const portaW = Math.max(8, Math.round(w * 0.15));
    const portaH = Math.max(4, Math.round(h * 0.08));
    s += `<rect x="${x + w*0.6}" y="${y+h - portaH/2}" width="${portaW}" height="${portaH + 2}" fill="#92400E" rx="1" stroke="#78350F" stroke-width="0.5"/>`;

    // Janela
    const janW = Math.max(6, Math.round(w * 0.1));
    const janH = Math.max(5, Math.round(h * 0.08));
    s += `<rect x="${x + w*0.2}" y="${y + h*0.65}" width="${janW}" height="${janH}" fill="#BFDBFE" stroke="white" stroke-width="1" rx="0.5"/>`;

    // Jardim pequeno (retângulo verde claro na frente)
    s += `<rect x="${x + w*0.35}" y="${y+h+d3}" width="${w*0.2}" height="${d3}" fill="#4ADE80" rx="1" opacity="0.6"/>`;

    // Placas solares no telhado
    if (numPlacas > 0) {
        const slots = gerarSlotsPlacas(x, y, w, h, numPlacas);
        for (let i = 0; i < slots.length; i++) {
            s += desenharPlaca(slots[i].x, slots[i].y, slots[i].w, slots[i].h, delayBase + i * 0.05);
        }
    }

    return s;
}


function desenharPlaca(px, py, pw, ph, delay) {
    return `<g filter="url(#sombraPlaca)">
        <rect x="${px}" y="${py}" width="${pw}" height="${ph}" fill="url(#placa)" stroke="#1E3A8A" stroke-width="0.6" rx="1" opacity="0">
            <animate attributeName="opacity" from="0" to="1" dur="0.3s" begin="${delay}s" fill="freeze"/>
        </rect>
        <line x1="${px + pw*0.5}" y1="${py}" x2="${px + pw*0.5}" y2="${py+ph}" stroke="#2563EB" stroke-width="0.3" opacity="0.3"/>
        <line x1="${px}" y1="${py + ph*0.5}" x2="${px+pw}" y2="${py + ph*0.5}" stroke="#2563EB" stroke-width="0.3" opacity="0.3"/>
    </g>`;
}


function desenharArvore(cx, cy, r) {
    return `<g>
        <circle cx="${cx}" cy="${cy}" r="${r}" fill="#16A34A" opacity="0.65"/>
        <circle cx="${cx - r*0.4}" cy="${cy - r*0.25}" r="${r*0.65}" fill="#22C55E" opacity="0.55"/>
        <circle cx="${cx + r*0.35}" cy="${cy - r*0.15}" r="${r*0.55}" fill="#15803D" opacity="0.55"/>
    </g>`;
}


function gerarSlotsPlacas(x, y, w, h, count) {
    // Grid 3x2 no telhado (metade superior, antes da cumeeira)
    const slots = [];
    const cols = 3, rows = 2;
    const margin = Math.max(3, w * 0.06);
    const areaW = w - margin * 2;
    const areaH = h / 2 - margin * 1.5;
    const pw = (areaW - (cols - 1) * 2) / cols;
    const ph = (areaH - (rows - 1) * 2) / rows;

    for (let r = 0; r < rows && slots.length < count; r++) {
        for (let c = 0; c < cols && slots.length < count; c++) {
            slots.push({
                x: x + margin + c * (pw + 2),
                y: y + margin + r * (ph + 2),
                w: pw,
                h: ph,
            });
        }
    }
    return slots;
}


// ===================== CÁLCULO LOCAL (slider) =====================

function atualizarCasaLocal() {
    const valor = parseFloat(document.getElementById("valorConta").value);
    const moradores = parseInt(document.getElementById("numMoradores").value);

    const placasPorPessoa = Math.max(1, Math.ceil(valor / 60));
    const placasTotal = placasPorPessoa * moradores;
    const telhados = Math.ceil(placasTotal / PLACAS_POR_TELHADO);

    desenharCasa(placasTotal);

    const info = document.getElementById("placasInfo");
    if (moradores > 1) {
        info.textContent = `≈ ${placasTotal} placas em ${telhados} telhado${telhados > 1 ? 's' : ''} · ${moradores} moradores na cooperativa`;
    } else {
        info.textContent = `≈ ${placasTotal} placa${placasTotal > 1 ? 's' : ''} para R$${valor}/mês`;
    }
}


// ===================== CÁLCULO VIA API =====================

async function calcular() {
    const cidade = document.getElementById("cidade").value.trim();
    const estado = document.getElementById("estado").value;
    const valorConta = parseFloat(document.getElementById("valorConta").value);
    const numMoradores = parseInt(document.getElementById("numMoradores").value);

    // Validação
    if (!cidade) {
        alert("Por favor, informe sua cidade.");
        document.getElementById("cidade").focus();
        return;
    }
    if (!estado) {
        alert("Por favor, selecione seu estado.");
        document.getElementById("estado").focus();
        return;
    }

    // UI: loading
    const btn = document.getElementById("btnCalcular");
    btn.disabled = true;
    btn.textContent = "⏳ Calculando...";
    document.getElementById("loading").classList.add("ativo");
    document.getElementById("resultados").classList.remove("ativo");

    try {
        const resp = await fetch("/api/calcular", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                cidade: cidade,
                estado: estado,
                valor_conta: valorConta,
                num_moradores: numMoradores,
            }),
        });

        const json = await resp.json();

        if (json.status === "sucesso") {
            dadosAtuais = json.dados;
            mostrarResultados(json.dados);
            desenharCasa(json.dados.num_placas || 0);
        } else {
            alert("Erro: " + (json.mensagem || "Tente novamente."));
        }
    } catch (err) {
        alert("Erro de conexão. Verifique se o servidor está rodando.");
        console.error(err);
    } finally {
        btn.disabled = false;
        btn.textContent = "⚡ Calcular Economia";
        document.getElementById("loading").classList.remove("ativo");
    }
}


function mostrarResultados(dados) {
    const secao = document.getElementById("resultados");
    secao.classList.add("ativo");

    const fmt = (v) => v.toLocaleString("pt-BR", {minimumFractionDigits: 2, maximumFractionDigits: 2});

    // Dados da região
    document.getElementById("resTarifa").textContent = `R$ ${dados.tarifa_kwh.toFixed(2)}/kWh`;
    document.getElementById("resIrradiacao").textContent = `${(dados.irradiacao_media || 0).toFixed(1)} kWh/m²/dia`;
    document.getElementById("resConsumo").textContent = `${dados.consumo_kwh.toFixed(0)} kWh/mês`;
    document.getElementById("resProducao").textContent = `${(dados.producao_kwh_mes || 0).toFixed(0)} kWh/mês`;

    // Economia por casa
    document.getElementById("resEconomia").textContent = `R$ ${fmt(dados.economia_mensal)}`;
    document.getElementById("resPercentual").textContent = `${dados.percentual_economia || 0}%`;

    // Sistema solar
    document.getElementById("resPlacas").textContent = `${dados.num_placas} placas`;
    document.getElementById("resPlacasCasa").textContent = `${dados.placas_por_casa || Math.ceil(dados.num_placas / dados.num_moradores)}`;
    document.getElementById("resCusto").textContent = `R$ ${fmt(dados.custo_estimado)}`;
    document.getElementById("resMoradores").textContent = `${dados.num_moradores} casa${dados.num_moradores > 1 ? 's' : ''}`;

    // Investimento por casa
    document.getElementById("resCustoPessoa").textContent = `R$ ${fmt(dados.custo_por_pessoa)}`;
    document.getElementById("resParcela").textContent = `R$ ${fmt(dados.parcela_mensal || 0)}`;
    document.getElementById("resRetorno").textContent = `${dados.tempo_retorno_meses} meses`;

    // Saldo detalhado (usa parcela de 60x como referência)
    const parcela = dados.parcela_mensal || 0;
    const saldo = dados.economia_mensal - parcela;
    document.getElementById("saldoEconomia").textContent = `+ R$ ${fmt(dados.economia_mensal)}`;
    document.getElementById("saldoParcela").textContent = `- R$ ${fmt(parcela)}`;
    const saldoFinalEl = document.getElementById("saldoFinal");
    saldoFinalEl.textContent = `R$ ${fmt(saldo)}`;
    saldoFinalEl.className = `saldo-valor ${saldo >= 0 ? 'positivo' : 'negativo'}`;

    const veredicto = document.getElementById("saldoVeredicto");
    if (saldo > 0) {
        veredicto.className = "saldo-veredicto positivo";
        veredicto.textContent = `Vale a pena! Mesmo pagando a parcela, você economiza R$ ${fmt(saldo)}/mês desde o primeiro dia.`;
    } else if (saldo === 0) {
        veredicto.className = "saldo-veredicto positivo";
        veredicto.textContent = "A parcela se paga sozinha com a economia! Depois de 60 meses, a economia é toda sua.";
    } else {
        veredicto.className = "saldo-veredicto negativo";
        veredicto.textContent = `A parcela é R$ ${fmt(Math.abs(saldo))}/mês a mais que a economia. Considere pagar à vista ou juntar mais vizinhos.`;
    }

    // Tabela comparativa de prazos
    if (dados.opcoes_financiamento) {
        let melhorIdx = -1;
        dados.opcoes_financiamento.forEach((op, i) => {
            if (op.saldo_mensal >= 0 && (melhorIdx === -1 || op.meses < dados.opcoes_financiamento[melhorIdx].meses)) {
                melhorIdx = i;
            }
        });
        if (melhorIdx === -1) melhorIdx = dados.opcoes_financiamento.length - 1;

        let tabHtml = `<table>
            <thead><tr>
                <th>Prazo</th>
                <th>Parcela/mês</th>
                <th>Total pago</th>
                <th>Juros pagos</th>
                <th>Saldo mensal</th>
            </tr></thead><tbody>`;

        dados.opcoes_financiamento.forEach((op, i) => {
            const classe = i === melhorIdx ? ' class="melhor-opcao"' : '';
            const saldoClass = op.saldo_mensal >= 0 ? 'saldo-positivo' : 'saldo-negativo';
            const saldoSinal = op.saldo_mensal >= 0 ? '+' : '';
            const tag = i === melhorIdx ? ' <span class="tag-recomendado">MELHOR</span>' : '';
            tabHtml += `<tr${classe}>
                <td>${op.meses}x${tag}</td>
                <td>R$ ${fmt(op.parcela)}</td>
                <td>R$ ${fmt(op.total_pago)}</td>
                <td>R$ ${fmt(op.juros_total)}</td>
                <td class="${saldoClass}">${saldoSinal}R$ ${fmt(op.saldo_mensal)}</td>
            </tr>`;
        });

        tabHtml += `</tbody></table>`;
        document.getElementById("tabelaFinanciamento").innerHTML = tabHtml;
    }

    // Projeção 25 anos
    if (dados.economia_25_anos) {
        document.getElementById("resEconomia25").textContent = `R$ ${fmt(dados.economia_25_anos)}`;
        document.getElementById("resLucroVista").textContent = `R$ ${fmt(dados.lucro_liquido_vista)}`;
        document.getElementById("resLucroFinanciado").textContent = `R$ ${fmt(dados.lucro_liquido_financiado)}`;

        const nota = document.getElementById("projecaoNota");
        const anosRetorno = (dados.tempo_retorno_meses / 12).toFixed(1);
        nota.textContent = `As placas solares têm vida útil de mais de 25 anos. Seu investimento se paga em ${anosRetorno} anos e, depois disso, a economia de R$ ${fmt(dados.economia_mensal)}/mês é lucro puro por mais de ${(25 - parseFloat(anosRetorno)).toFixed(0)} anos.`;
    }

    // Atualiza SVG
    desenharCasa(dados.num_placas);
    document.getElementById("placasInfo").textContent =
        `${dados.num_placas} placas de 550W | ${dados.num_moradores} casa${dados.num_moradores > 1 ? 's' : ''} | Irradiação: ${(dados.irradiacao_media || 0).toFixed(1)} kWh/m²/dia`;

    secao.scrollIntoView({ behavior: "smooth", block: "start" });
}


// ===================== SALVAR SIMULAÇÃO =====================

async function salvar() {
    if (!dadosAtuais) {
        alert("Faça uma simulação primeiro.");
        return;
    }

    const cidade = document.getElementById("cidade").value.trim();
    const estado = document.getElementById("estado").value;
    const valorConta = parseFloat(document.getElementById("valorConta").value);
    const numMoradores = parseInt(document.getElementById("numMoradores").value);

    try {
        const resp = await fetch("/api/simulacoes", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                cidade: cidade,
                estado: estado,
                valor_conta: valorConta,
                num_moradores: numMoradores,
            }),
        });

        const json = await resp.json();

        if (json.status === "sucesso") {
            // Mostra relatório LLM se existir
            if (json.dados.relatorio_llm) {
                document.getElementById("relatorioContainer").style.display = "block";
                document.getElementById("relatorioTexto").textContent = json.dados.relatorio_llm;
            }
            alert("Simulação salva com sucesso! ID: " + json.dados.id);
            carregarHistorico();
        } else {
            alert("Erro ao salvar: " + (json.mensagem || "Tente novamente."));
        }
    } catch (err) {
        alert("Erro de conexão ao salvar.");
        console.error(err);
    }
}


// ===================== HISTÓRICO =====================

async function carregarHistorico() {
    try {
        const resp = await fetch("/api/simulacoes");
        const json = await resp.json();

        if (json.status === "sucesso" && json.dados.length > 0) {
            renderizarHistorico(json.dados);
        }
    } catch (err) {
        // Sem servidor, ignora
        console.log("Servidor não disponível para carregar histórico.");
    }
}


function renderizarHistorico(simulacoes) {
    const container = document.getElementById("historicoContainer");
    const fmt = (v) => parseFloat(v).toLocaleString("pt-BR", {minimumFractionDigits: 2, maximumFractionDigits: 2});

    let html = `<div class="historico-cards">`;

    simulacoes.forEach(s => {
        const moradores = s.num_moradores || 1;
        const custoPessoa = s.custo_por_pessoa || (s.custo_estimado / moradores);
        const tarifa = s.tarifa_kwh || 0;

        html += `<div class="historico-card">
            <div class="historico-header">
                <strong>${s.cidade}/${s.estado}</strong>
                <button class="btn-delete" onclick="deletar(${s.id})" title="Remover">🗑️</button>
            </div>
            <div class="historico-dados">
                <div class="historico-dado">
                    <span class="historico-label">Conta média</span>
                    <span class="historico-value">R$ ${fmt(s.valor_conta)}</span>
                </div>
                <div class="historico-dado">
                    <span class="historico-label">Casas na cooperativa</span>
                    <span class="historico-value">${moradores}</span>
                </div>
                <div class="historico-dado">
                    <span class="historico-label">Tarifa</span>
                    <span class="historico-value">R$ ${tarifa.toFixed(2)}/kWh</span>
                </div>
                <div class="historico-dado">
                    <span class="historico-label">Placas totais</span>
                    <span class="historico-value">${s.num_placas}</span>
                </div>
                <div class="historico-dado destaque">
                    <span class="historico-label">Economia/casa/mês</span>
                    <span class="historico-value">R$ ${fmt(s.economia_mensal)}</span>
                </div>
                <div class="historico-dado destaque">
                    <span class="historico-label">Investimento/casa</span>
                    <span class="historico-value">R$ ${fmt(custoPessoa)}</span>
                </div>
                <div class="historico-dado">
                    <span class="historico-label">Retorno</span>
                    <span class="historico-value">${s.tempo_retorno_meses} meses</span>
                </div>
            </div>
            ${s.relatorio_llm ? `<button class="btn-relatorio" onclick="toggleRelatorio(${s.id})">📝 Ver Relatório</button>
            <div class="historico-relatorio" id="relatorio-${s.id}" style="display:none;">
                <div class="relatorio-box">${s.relatorio_llm}</div>
            </div>` : ''}
        </div>`;
    });

    html += `</div>`;
    container.innerHTML = html;
}

function toggleRelatorio(id) {
    const el = document.getElementById(`relatorio-${id}`);
    if (el) {
        el.style.display = el.style.display === "none" ? "block" : "none";
    }
}


async function deletar(id) {
    if (!confirm("Deseja remover esta simulação?")) return;

    try {
        const resp = await fetch(`/api/simulacoes/${id}`, { method: "DELETE" });
        const json = await resp.json();

        if (json.status === "sucesso") {
            carregarHistorico();
        } else {
            alert("Erro ao remover: " + (json.mensagem || "Tente novamente."));
        }
    } catch (err) {
        alert("Erro de conexão ao remover.");
    }
}
