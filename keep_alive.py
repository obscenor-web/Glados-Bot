from flask import Flask
from threading import Thread

# Cria o servidor Flask
app = Flask('')

# Rota principal
@app.route('/')
def home():
    return "Bot is alive!"  # O UptimeRobot vai acessar essa URL

# Função que roda o servidor
def run():
    app.run(host='0.0.0.0', port=5000)

# Função que mantém o servidor rodando em paralelo
def keep_alive():
    t = Thread(target=run)
    t.start()
