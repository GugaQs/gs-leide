# Setup na Faculdade - Passo a Passo

## 1. Clonar o projeto (30 segundos)

```bash
git clone https://github.com/GugaQs/gs-leide.git
cd gs-leide
```

## 2. Instalar dependencias Python (30 segundos)

```bash
pip install -r requirements.txt
```

Se der erro de permissao:
```bash
pip install --user -r requirements.txt
```

## 3. Configurar MySQL (2 minutos)

### Se tiver XAMPP:
1. Abra o painel do XAMPP
2. Clique em "Start" no MySQL
3. Clique em "Shell" e rode:
```bash
mysql -u root < schema.sql
```

### Se tiver MySQL direto:
```bash
mysql -u root -p < schema.sql
```
(digita a senha do MySQL quando pedir)

### O que esse comando faz:
- Cria o banco `telhado_solar`
- Cria a tabela `simulacoes` com todos os campos

## 4. Criar o arquivo .env (1 minuto)

Copie o exemplo:
```bash
copy .env.example .env
```

Edite o `.env` e ajuste a senha do MySQL da maquina:
```
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=COLOQUE_A_SENHA_DO_MYSQL_AQUI
DB_NAME=telhado_solar

FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=True

LLM_API_KEY=sua_chave_aqui
LLM_API_URL=https://api.groq.com/openai/v1/chat/completions
LLM_MODEL=llama-3.3-70b-versatile
```

**XAMPP geralmente nao tem senha** — nesse caso deixe:
```
DB_PASSWORD=
```

## 5. Rodar o projeto (10 segundos)

```bash
python app.py
```

Abra no navegador: **http://localhost:5000**

## 6. Gravar o video

Com o sistema rodando:
1. Preencha cidade, estado e valor da conta
2. Ajuste o numero de moradores
3. Clique em "Calcular Economia"
4. Mostre os resultados: dados da regiao, economia, investimento, tabela de prazos, projecao 25 anos
5. Salve a simulacao e mostre o relatorio completo
6. Faca outra simulacao de outra cidade e compare no historico

## Troubleshooting

### "ModuleNotFoundError: No module named 'flask'"
```bash
pip install -r requirements.txt
```

### "Access denied for user 'root'"
Verifique a senha do MySQL no `.env`

### "Can't connect to MySQL server"
Verifique se o MySQL esta rodando (XAMPP > Start MySQL)

### "Database 'telhado_solar' doesn't exist"
Rode o schema novamente:
```bash
mysql -u root -p < schema.sql
```

### Porta 5000 ocupada
Mude no `.env`:
```
FLASK_PORT=5001
```
E acesse http://localhost:5001

## Estrutura do Projeto

```
gs-leide/
├── app.py              # Servidor Flask (rotas da API)
├── config.py           # Configuracoes e tarifas por estado
├── database.py         # CRUD MySQL (queries parametrizadas)
├── external_api.py     # Integracao Open-Meteo (irradiacao solar)
├── solar_calc.py       # Logica de calculo solar e financiamento
├── llm_module.py       # Geracao de relatorio (Groq LLM ou template)
├── logger_module.py    # Sistema de logs
├── gerar_relatorio.py  # Geracao do PDF (reportlab)
├── schema.sql          # Script para criar o banco MySQL
├── requirements.txt    # Dependencias Python
├── .env.example        # Modelo do arquivo de configuracao
├── .gitignore          # Arquivos ignorados pelo git
├── templates/
│   └── index.html      # Pagina principal
└── static/
    ├── css/style.css   # Estilos
    └── js/app.js       # Frontend (SVG, calculos, historico)
```
