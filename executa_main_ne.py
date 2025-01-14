
import os
import subprocess
import webbrowser

# Instalar dependências
subprocess.run(["pip", "install", "-r", "requirements.txt"])

# Rodar o backend
os.chdir(os.path.dirname(__file__))
subprocess.Popen(["python", "app.py"])

# Abrir o navegador
webbrowser.open("http://127.0.0.1:5000")
