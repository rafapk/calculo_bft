from flask import Flask, request, jsonify, send_file
import math
import matplotlib.pyplot as plt
import os
import time 
import fitz  # PyMuPDF
import re
import pdfplumber
import PyPDF2


app = Flask(__name__)

# Função para calcular o percentual de gordura corporal (BFP) para masculino
def calcular_bfp_masculino(cintura, pescoço, altura):
    return 495 / (1.0324 - 0.19077 * math.log10(cintura - pescoço) + 0.15456 * math.log10(altura)) - 450

# Função para calcular o percentual de gordura corporal (BFP) para feminino
def calcular_bfp_feminino(cintura, quadril, pescoço, altura):
    return 495 / (1.29579 - 0.35004 * math.log10(cintura + quadril - pescoço) + 0.22100 * math.log10(altura)) - 450

# Função para determinar o percentual de gordura ideal
def determinar_gordura_ideal(idade, sexo):
    tabela_ideal = {
        "masculino": {20: 8.5, 25: 10.5, 30: 12.7, 35: 13.7, 40: 15.3, 45: 16.4, 50: 18.9, 55: 20.9},
        "feminino": {20: 17.7, 25: 18.4, 30: 19.3, 35: 21.5, 40: 22.2, 45: 22.9, 50: 25.2, 55: 26.3},
    }
    if sexo not in tabela_ideal:
        return None
    faixa_etaria = min(tabela_ideal[sexo].keys(), key=lambda x: abs(x - idade))
    return tabela_ideal[sexo][faixa_etaria]

# Função para plotar o gráfico do percentual de gordura corporal
def plotar_grafico_bfp(bfp, gordura_ideal, sexo):
    # Categorias e limites baseados na tabela fornecida

    if not os.path.exists('static'):
        os.makedirs('static')

    if sexo == "masculino":
        categorias = ["Essential fat", "Athletes", "Fitness", "Average", "Obese"]
        limites = [2, 6, 14, 18, 25, 40]
        cores = ["#8B0000", "#00FF00", "#32CD32", "#FFD700", "#B22222"]
    elif sexo == "feminino":
        categorias = ["Essential fat", "Athletes", "Fitness", "Average", "Obese"]
        limites = [10, 14, 21, 25, 32, 50]
        cores = ["#8B0000", "#00FF00", "#32CD32", "#FFD700", "#B22222"]
    else:
        return None

    fig, ax = plt.subplots(figsize=(12, 6))

    # Adicionar barras para categorias
    for i in range(len(categorias)):
        largura = limites[i + 1] - limites[i] if i + 1 < len(limites) else 5
        ax.barh(0, largura, color=cores[i], edgecolor="black", left=limites[i], height=1)

        # Adicionar rótulos de categoria no eixo X
        ax.text(
            (limites[i] + (limites[i + 1] if i + 1 < len(limites) else limites[i] + 5)) / 2,
            0.2,
            categorias[i],
            ha="center",
            va="center",
            fontsize=11,
            fontweight="bold"
        )

    # Adicionar linhas indicadoras para BFP e BFP Ideal
    ax.plot([bfp, bfp], [-0.5, 0.5], color="blue", linewidth=2, linestyle="--", label=f"Seu BFP: {bfp:.1f}%")
    if gordura_ideal is not None:
        ax.plot([gordura_ideal, gordura_ideal], [-0.5, 0.5], color="green", linewidth=2, linestyle="-.", label=f"BFP Ideal: {gordura_ideal:.1f}%")

    # Configurar eixos
    ax.set_xlim(0, limites[-1])
    ax.set_ylim(-1, 1)
    ax.set_xlabel("Percentual de Gordura Corporal (%)", fontsize=12)
    ax.set_yticks([])
    ax.set_xticks(limites + [limites[-1]])
    ax.legend(loc="upper left", fontsize=10)
    ax.grid(axis="x", linestyle="--", alpha=0.7)

    # Salvar gráfico
    timestamp = int(time.time())
    graph_path = os.path.join('static', f'grafico_bfp_{timestamp}.png')
        # Salvar gráfico
    if not os.path.exists('static'):
        os.makedirs('static')
    timestamp = int(time.time())
    graph_path = os.path.join('static', f'grafico_bfp_{timestamp}.png')
    plt.savefig(graph_path, bbox_inches="tight")
    plt.savefig(graph_path, bbox_inches="tight")
    plt.close()
    return graph_path

def calcular_categoria_gordura(sexo, bfp):
    categorias = {
        "masculino": [2, 6, 14, 18, 25, 40],
        "feminino": [10, 14, 21, 25, 32, 50]
    }
    nomes = ["Essential fat", "Athletes", "Fitness", "Average", "Obese"]
    limites = categorias.get(sexo)
    if limites:
        for i in range(len(limites) - 1):
            if limites[i] <= bfp < limites[i + 1]:
                return nomes[i]
        return nomes[-1]
    return None

def calcular_massa_gorda(bfp, peso):
    return (bfp / 100) * peso

def calcular_massa_magra(peso, massa_gorda):
    return peso - massa_gorda

def determinar_gordura_ideal(idade, sexo):
    tabela_ideal = {
        "masculino": {20: 8.5, 25: 10.5, 30: 12.7, 35: 13.7, 40: 15.3, 45: 16.4, 50: 18.9, 55: 20.9},
        "feminino": {20: 17.7, 25: 18.4, 30: 19.3, 35: 21.5, 40: 22.2, 45: 22.9, 50: 25.2, 55: 26.3},
    }
    if sexo not in tabela_ideal:
        return None
    faixa_etaria = min(tabela_ideal[sexo].keys(), key=lambda x: abs(x - idade))
    return tabela_ideal[sexo][faixa_etaria]

def gordura_a_perder(bfp, gordura_ideal, peso):
    return (bfp - gordura_ideal) * peso / 100 if bfp > gordura_ideal else 0

def calcular_bfp_imc(imc, idade, sexo):
    if sexo == "masculino":
        return 1.20 * imc + 0.23 * idade - 16.2
    elif sexo == "feminino":
        return 1.20 * imc + 0.23 * idade - 5.4
    return None

# Função para ler o PDF e extrair os dados
def extrair_dados_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    
    nome = ""
    peso = None
    altura = None
    pescoco = None
    cintura = None
    quadril = None
    
    # Loop para extrair o texto das páginas do PDF
    for page in doc:
        text = page.get_text("text")
        
        # Extrair o nome do paciente
        nome_match = re.search(r'Nome:\s*(\w+)', text)
        if nome_match:
            nome = nome_match.group(1)
        
        # Procurar os dados na tabela
        for line in text.split("\n"):
            if "Peso atual (Kg)" in line:
                peso_match = re.search(r'(\d+[\.,]?\d*)\s*$', line)
                if peso_match:
                    peso = peso_match.group(1).replace(',', '.')
            if "Altura atual (cm)" in line:
                altura_match = re.search(r'(\d+[\.,]?\d*)\s*$', line)
                if altura_match:
                    altura = altura_match.group(1).replace(',', '.')
            if "Circunferência do Pescoço (cm)" in line:
                pescoco_match = re.search(r'(\d+[\.,]?\d*)\s*$', line)
                if pescoco_match:
                    pescoco = pescoco_match.group(1).replace(',', '.')
            if "Circunferência da Cintura (cm)" in line:
                cintura_match = re.search(r'(\d+[\.,]?\d*)\s*$', line)
                if cintura_match:
                    cintura = cintura_match.group(1).replace(',', '.')
            if "Circunferência do Quadril (cm)" in line:
                quadril_match = re.search(r'(\d+[\.,]?\d*)\s*$', line)
                if quadril_match:
                    quadril = quadril_match.group(1).replace(',', '.')
    
    return {
        "nome": nome,
        "peso": peso,
        "altura": altura,
        "pescoco": pescoco,
        "cintura": cintura,
        "quadril": quadril
    }
'''
@app.route('/importar_pdf', methods=['POST'])
def importar_pdf():
    # Supondo que o arquivo PDF seja enviado via multipart/form-data
    file = request.files['pdf']
    
    # Abre o PDF com pdfplumber
    with pdfplumber.open(file) as pdf:
        page = pdf.pages[0]  # Assume-se que o conteúdo relevante está na primeira página

        # Extração do texto completo
        text = page.extract_text()

        # Processar o texto e extrair as informações
        nome = None
        peso = None
        altura = None
        pescoco = None
        cintura = None
        quadril = None

        # Buscar o nome (considerando que está após 'Nome:')
        for line in text.split("\n"):
            if line.startswith("Nome:"):
                nome = line.split("Nome:")[1].strip()

        # Buscar os dados na tabela (peso, altura, circunferências)
        for line in text.split("\n"):
            if "Peso atual (Kg)" in line:
                peso = line.split("Peso atual (Kg)")[1].strip().split()[0]
            if "Altura atual (cm)" in line:
                altura = line.split("Altura atual (cm)")[1].strip().split()[0]
            if "Circunferência do Pescoço (cm)" in line:
                pescoco = line.split("Circunferência do Pescoço (cm)")[1].strip().split()[0]
            if "Circunferência da Cintura (cm)" in line:
                cintura = line.split("Circunferência da Cintura (cm)")[1].strip().split()[0]
            if "Circunferência do Quadril (cm)" in line:
                quadril = line.split("Circunferência do Quadril (cm)")[1].strip().split()[0]

        # Retorna os dados extraídos para o frontend
        return jsonify({
            'nome': nome,
            'peso': peso,
            'altura': altura,
            'pescoco': pescoco,
            'cintura': cintura,
            'quadril': quadril
        })
'''

@app.route('/')
def index():
    return send_file('index.html')

# Diretório para salvar o PDF
upload_folder = 'uploads'

'''
@app.route('/importar_pdf', methods=['POST'])
def importar_pdf():
    # Verificar se o arquivo foi enviado
    file = request.files.get('pdf')
    if file:
        # Verificar e criar o diretório de uploads, se necessário
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)

        # Salvar o arquivo PDF temporariamente no diretório de uploads
        pdf_path = os.path.join(upload_folder, file.filename)
        file.save(pdf_path)

        # Extrair dados do PDF
        dados = extrair_dados_pdf(pdf_path)

        return jsonify(dados), 200

    return jsonify({"error": "Arquivo não enviado"}), 400

'''

@app.route('/importar_pdf', methods=['POST'])
def importar_pdf():
    # Verificar se o arquivo foi enviado
    file = request.files.get('pdf')
    if file:
        # Extrair dados do PDF diretamente do arquivo enviado
        dados = extrair_dados_pdf(file)

        return jsonify(dados), 200

    return jsonify({"error": "Arquivo não enviado"}), 400


def pegar_ultimo_valido(valores):
    """Retorna o último valor válido não vazio, `null`, `-` ou `N/A`."""
    for valor in reversed(valores):
        if valor and valor not in ['', 'null', '-', 'N/A']:
            return valor.strip()
    return None

def extrair_valor_circunferencia(linha):
    """Extrai o valor numérico de uma linha que contém uma circunferência."""
    valores = re.findall(r"(\d+[,\.]?\d*)", linha)
    if valores:
        return valores[0]
    return None

def extrair_dados_pdf(pdf_path):
    # Inicializar o dicionário para armazenar os dados extraídos
    dados = {}

    # Abrir o arquivo PDF com pdfplumber
    with pdfplumber.open(pdf_path) as pdf:
        # Iterar por todas as páginas do PDF
        for page in pdf.pages:
            text = page.extract_text()

            # Extração do Nome do Paciente (considerando todas as páginas)
            nome_match = re.search(r"Nome:\s*(.*)", text)
            if nome_match and 'nome' not in dados:
                dados['nome'] = nome_match.group(1).strip()

            # Extração de todas as tabelas da página
            tabelas = page.extract_tables()

            # Verificar o número de tabelas extraídas
            print(f"Total de tabelas extraídas na página {pdf.pages.index(page) + 1}: {len(tabelas)}")
            
            # Processar todas as tabelas
            for i, tabela in enumerate(tabelas):
                print(f"\nTabela {i + 1} (Página {pdf.pages.index(page) + 1}):")
                for linha in tabela:
                    print(linha)

                # A primeira tabela contém Peso e Altura
                if len(tabela) > 0:
                    for linha in tabela:
                        campo = linha[0].strip() if linha[0] else ""
                        valores = linha[1:]

                        if "Peso atual (Kg)" in campo:
                            dados['peso'] = pegar_ultimo_valido(valores)
                        elif "Altura atual (cm)" in campo:
                            dados['altura'] = pegar_ultimo_valido(valores)

            # Agora, buscaremos as circunferências diretamente pelas palavras-chave
            circunferencias = [
                "Circunferência do Pescoço",
                "Circunferência da Cintura",
                "Circunferência do Quadril",
                "Circunferência do Abdomen",
                "Circunf. do Braço Relaxado",
                "Circunf. do Braço Contraído",
                "Circunf. Medial da Coxa",
                "Circunf. da Panturrilha"
            ]

            for linha in text.split('\n'):
                for circunferencia in circunferencias:
                    if circunferencia in linha:
                        valor = extrair_valor_circunferencia(linha)
                        if valor:
                            dados[circunferencia] = valor

    # Remover valores vazios, null, '-', N/A
    dados = {chave: valor for chave, valor in dados.items() if valor and valor not in ['', 'null', '-', 'N/A']}

    # Imprimir os dados extraídos no terminal
    print("Dados extraídos:")
    for chave, valor in dados.items():
        print(f"{chave}: {valor}")

    # Retornar os dados extraídos
    return dados

@app.route('/calcular', methods=['POST'])
def calcular_bfp():
    data = request.json
    try:
        nome = data.get('nome')
        sexo = data.get('sexo')
        idade = float(data.get('idade', 0))
        altura = float(data.get('altura', 0)) / 100  # Convert cm to meters
        peso = float(data.get('peso', 0))
        pescoco = float(data.get('pescoco', 0))
        cintura = float(data.get('cintura', 0))
        quadril = float(data.get('quadril', 0)) if sexo == 'feminino' else None

        if altura <= 0 or pescoco <= 0 or cintura <= 0 or (quadril is not None and quadril <= 0):
            return jsonify({"error": "Todos os valores devem ser maiores que zero."}), 400

        imc = peso / (altura ** 2)

        if sexo == "masculino":
            bfp = calcular_bfp_masculino(cintura, pescoco, altura * 100)
        elif sexo == "feminino":
            bfp = calcular_bfp_feminino(cintura, quadril, pescoco, altura * 100)
        else:
            return jsonify({"error": "Sexo inválido"}), 400

        categoria = calcular_categoria_gordura(sexo, bfp)
        gordura_ideal = determinar_gordura_ideal(idade, sexo)
        massa_gorda = calcular_massa_gorda(bfp, peso)
        massa_magra = calcular_massa_magra(peso, massa_gorda)
        gordura_perder = gordura_a_perder(bfp, gordura_ideal, peso)
        bfp_imc = calcular_bfp_imc(imc, idade, sexo)

        graph_path = plotar_grafico_bfp(bfp, gordura_ideal, sexo)

        return jsonify({
            "nome": nome,
            "bfp": round(bfp, 2),
            "categoria": categoria,
            "massa_gorda": round(massa_gorda, 2),
            "massa_magra": round(massa_magra, 2),
            "gordura_ideal": round(gordura_ideal, 2) if gordura_ideal else None,
            "gordura_perder": round(gordura_perder, 2),
            "bfp_imc": round(bfp_imc, 2),
            "grafico": f"/static/{os.path.basename(graph_path)}"
        }), 200

    except Exception as e:
        return jsonify({"error": f"Erro: {str(e)}"}), 500

    

    
@app.route('/static/<path:path>')
def serve_static(path):
    return send_file(os.path.join('static', path))

if __name__ == '__main__':
    app.run(debug=True)
