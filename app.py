import os
import pandas as pd
from flask import Flask, render_template, request, jsonify, send_file

# Configurações do Flask
app = Flask(__name__)

# Caminho do arquivo para persistência de dados
data_file = "dados_lojas.xlsx"

# Dados iniciais
initial_data = [
    {"Região": "ZONA DA MATA", "Loja": 97, "Nome": "Viçosa", "PDV": "não tem cx", "Operador": "Operador 1"},
    {"Região": "OURO PRETO", "Loja": 15, "Nome": "Ponte Nova", "PDV": "16", "Operador": "Operador 2"},
    {"Região": "CARATINGA", "Loja": 44, "Nome": "Inhapim", "PDV": "6", "Operador": "Operador 3"},
    # Adicione mais dados conforme necessário...
]

# Criar o arquivo com dados iniciais, se não existir
if not os.path.exists(data_file):
    df = pd.DataFrame(initial_data)
    df.to_excel(data_file, index=False, engine="openpyxl")

@app.route('/')
def index():
    # Carregar dados do arquivo
    df = pd.read_excel(data_file, engine="openpyxl")
    grouped_data = df.groupby("Região")
    return render_template("index.html", regionais=grouped_data)

@app.route('/adicionar', methods=['POST'])
def adicionar():
    try:
        data = request.get_json()
        novo_dado = pd.DataFrame([{  # Criar um DataFrame temporário para os novos dados
            "Região": data.get("regiao"),
            "Loja": data.get("loja"),
            "Nome": data.get("nome"),
            "PDV": data.get("pdv"),
            "Operador": data.get("operador", "")
        }])
        
        df = pd.read_excel(data_file, engine="openpyxl")
        df = pd.concat([df, novo_dado], ignore_index=True)  # Substituir append por concat
        df.to_excel(data_file, index=False, engine="openpyxl")
        return jsonify({"status": "success", "message": "Dados adicionados com sucesso."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/excluir', methods=['POST'])
def excluir():
    try:
        data = request.get_json()
        loja = data.get("loja")

        if loja is None:
            return jsonify({"status": "error", "message": "O campo 'loja' é obrigatório."}), 400

        # Carregar dados existentes
        df = pd.read_excel(data_file, engine="openpyxl")

        # Verificar se a loja existe
        if loja not in df["Loja"].values:
            return jsonify({"status": "error", "message": "Loja não encontrada."}), 404

        # Excluir a linha correspondente
        df = df[df["Loja"] != loja]
        df.to_excel(data_file, index=False, engine="openpyxl")

        return jsonify({"status": "success", "message": "Dados excluídos com sucesso."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/excluir_tudo', methods=['POST'])
def excluir_tudo():
    try:
        # Criar um DataFrame vazio com as mesmas colunas
        df = pd.DataFrame(columns=["Região", "Loja", "Nome", "PDV", "Operador"])
        df.to_excel(data_file, index=False, engine="openpyxl")

        return jsonify({"status": "success", "message": "Todos os dados foram excluídos."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/editar', methods=['POST'])
def editar():
    try:
        data = request.get_json()
        loja = data.get("loja")

        if loja is None:
            return jsonify({"status": "error", "message": "O campo 'loja' é obrigatório."}), 400

        # Atualizar os dados correspondentes à loja
        df = pd.read_excel(data_file, engine="openpyxl")
        if loja not in df["Loja"].values:
            return jsonify({"status": "error", "message": "Loja não encontrada."}), 404

        df.loc[df["Loja"] == loja, ["Região", "Nome", "PDV", "Operador"]] = [
            data.get("regiao"),
            data.get("nome"),
            data.get("pdv"),
            data.get("operador")
        ]
        df.to_excel(data_file, index=False, engine="openpyxl")
        return jsonify({"status": "success", "message": "Dados editados com sucesso."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/exportar', methods=['GET'])
def exportar():
    try:
        return send_file(data_file, as_attachment=True)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/importar', methods=['POST'])
def importar():
    try:
        if 'file' not in request.files:
            return jsonify({"status": "error", "message": "Nenhum arquivo foi enviado."}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({"status": "error", "message": "O nome do arquivo está vazio."}), 400

        new_data = pd.read_excel(file, engine="openpyxl")
        required_columns = {"Região", "Loja", "Nome", "PDV", "Operador"}
        if not required_columns.issubset(new_data.columns):
            return jsonify({"status": "error", "message": "O arquivo não contém todas as colunas necessárias."}), 400

        existing_data = pd.read_excel(data_file, engine="openpyxl")
        combined_data = pd.concat([existing_data, new_data], ignore_index=True)
        combined_data.to_excel(data_file, index=False, engine="openpyxl")

        return jsonify({"status": "success", "message": "Dados importados com sucesso."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
