# ☀️ Telhado Solar Comunitário

**Global Solution — CitizenTech | FIAP 2026**
**Disciplina:** Coding for Security

> Descubra quanto você pode economizar com energia solar e como sua comunidade pode se unir para tornar isso realidade.

## 🎯 O Problema

Moradores de baixa renda pagam contas de luz altas, mas não sabem que a energia solar já é acessível — especialmente quando vizinhos se juntam numa cooperativa solar. Falta informação clara, em linguagem simples, sobre custos, economia e como começar.

## 👤 O Cidadão

Morador de comunidade ou bairro periférico com conta de luz alta e pouco acesso a informação sobre alternativas energéticas. Também atende líderes comunitários que querem organizar cooperativas solares.

## 🌍 ODS Relacionados

- **ODS 13** — Ação contra a mudança global do clima
- **ODS 11** — Cidades e comunidades sustentáveis
- **ODS 10** — Redução das desigualdades

## 🛠️ Tecnologias

| Componente | Tecnologia |
|---|---|
| Backend | Python + Flask |
| Banco de dados | MySQL (sem ORM, queries parametrizadas) |
| API externa | [Open-Meteo](https://open-meteo.com/) (irradiação solar, sem chave) |
| Módulo extra | Integração com LLM via API (Groq, gratuito) |
| Frontend | HTML5 + CSS3 + JavaScript puro |
| Visualização | SVG interativo (casinha com placas solares) |

## 📁 Estrutura do Projeto

```
telhado-solar/
├── app.py               # Aplicação Flask (4 endpoints CRUD + auxiliares)
├── config.py            # Configurações e constantes
├── database.py          # Conexão MySQL e operações CRUD
├── external_api.py      # Integração com Open-Meteo
├── solar_calc.py        # Lógica de cálculo solar
├── llm_module.py        # Geração de relatório com LLM
├── logger_module.py     # Sistema de logging
├── schema.sql           # Script de criação do banco
├── requirements.txt     # Dependências Python
├── .env.example         # Exemplo de variáveis de ambiente
├── templates/
│   └── index.html       # Interface web
├── static/
│   ├── css/style.css    # Estilos
│   └── js/app.js        # JavaScript (casinha SVG interativa)
└── logs/                # Logs da aplicação
```

## 🚀 Como Executar

### Pré-requisitos

- Python 3.10+
- MySQL 8.0+
- Git

### Passo a passo

1. **Clone o repositório**
```bash
git clone https://github.com/seu-usuario/telhado-solar.git
cd telhado-solar
```

2. **Crie o ambiente virtual**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. **Instale as dependências**
```bash
pip install -r requirements.txt
```

4. **Configure o .env**
```bash
cp .env.example .env
# Edite o .env com suas credenciais do MySQL
```

5. **Inicie o MySQL** e verifique que está rodando na porta 3306

6. **Execute a aplicação**
```bash
python app.py
```

7. **Acesse no navegador:** http://localhost:5000

> O banco de dados e a tabela são criados automaticamente na primeira execução.

### LLM (opcional)

Para ter o relatório gerado por IA:
1. Crie uma conta gratuita no [Groq](https://console.groq.com/)
2. Gere uma API key
3. Coloque no `.env`: `LLM_API_KEY=sua_chave`

Sem a chave, o sistema gera um relatório template (funciona normalmente).

## 📡 API REST — Endpoints

| Método | Rota | Descrição | Status |
|---|---|---|---|
| `GET` | `/api/simulacoes` | Lista todas as simulações | 200 |
| `POST` | `/api/simulacoes` | Cria nova simulação (com cálculo) | 201 |
| `PUT` | `/api/simulacoes/<id>` | Atualiza uma simulação | 200 |
| `DELETE` | `/api/simulacoes/<id>` | Remove uma simulação | 200 |
| `POST` | `/api/calcular` | Cálculo rápido (não salva) | 200 |
| `GET` | `/api/tarifas` | Lista tarifas por estado | 200 |

### Exemplo de requisição POST

```json
{
    "cidade": "São Paulo",
    "estado": "SP",
    "valor_conta": 300,
    "num_moradores": 10
}
```

## 🔒 Segurança

- **Credenciais em .env** — nunca versionadas (`.gitignore`)
- **Consultas parametrizadas** — todas as queries usam `%s`, sem concatenação
- **Validação de entrada** — todos os campos são validados antes de processar
- **Mensagens de erro genéricas** — erros internos não são expostos ao usuário
- **Coleta mínima de dados** — apenas cidade, estado e valor da conta (LGPD)
- **Dados fictícios/abertos** — usa apenas APIs públicas e dados abertos (ANEEL, Open-Meteo)

## 📝 Uso de IA Generativa

Este projeto utilizou IA generativa (Claude, Anthropic) como ferramenta de apoio para:
- Auxílio na estruturação do código e boas práticas
- Depuração de erros
- Geração de ideias para a interface visual

Todo o código foi revisado, compreendido e pode ser explicado na arguição. O módulo LLM integrado usa a API do Groq (Llama 3.3) para gerar relatórios explicativos em linguagem simples.

## 📄 Licença

Projeto acadêmico — FIAP 2026.
