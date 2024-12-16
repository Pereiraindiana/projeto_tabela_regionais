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
]

# Criar o arquivo com dados iniciais, se não existir
if not os.path.exists(data_file):
    df = pd.DataFrame(initial_data)
    df.to_excel(data_file, index=False, engine="openpyxl")

@app.route('/')
def index():
    df = pd.read_excel(data_file, engine="openpyxl")
    grouped_data = df.groupby("Região")
    return render_template("index.html", regionais=grouped_data)

@app.route('/adicionar', methods=['POST'])
def adicionar():
    try:
        data = request.get_json()
        novo_dado = pd.DataFrame([{
            "Região": data.get("regiao"),
            "Loja": data.get("loja"),
            "Nome": data.get("nome"),
            "PDV": data.get("pdv"),
            "Operador": data.get("operador", "")
        }])
        
        df = pd.read_excel(data_file, engine="openpyxl")
        df = pd.concat([df, novo_dado], ignore_index=True)
        df.to_excel(data_file, index=False, engine="openpyxl")
        return jsonify({"status": "success", "message": "Loja adicionada com sucesso."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/editar', methods=['POST'])
def editar():
    try:
        data = request.get_json()
        loja_id = data.get("loja")

        if loja_id is None:
            return jsonify({"status": "error", "message": "O campo 'loja' é obrigatório."}), 400

        # Carregar dados
        df = pd.read_excel(data_file, engine="openpyxl")

        # Verificar existência da loja
        if loja_id not in df["Loja"].values:
            return jsonify({"status": "error", "message": "Loja não encontrada."}), 404

        # Atualizar os dados
        df.loc[df["Loja"] == loja_id, ["Região", "Nome", "PDV", "Operador"]] = [
            data.get("regiao"),
            data.get("nome"),
            data.get("pdv"),
            data.get("operador")
        ]
        df.to_excel(data_file, index=False, engine="openpyxl")
        return jsonify({"status": "success", "message": "Loja editada com sucesso."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/excluir', methods=['POST'])
def excluir():
    try:
        data = request.get_json()
        loja_id = data.get("loja")

        if loja_id is None:
            return jsonify({"status": "error", "message": "O campo 'loja' é obrigatório."}), 400

        df = pd.read_excel(data_file, engine="openpyxl")

        # Verificar se a loja existe
        if loja_id not in df["Loja"].values:
            return jsonify({"status": "error", "message": "Loja não encontrada."}), 404

        # Excluir a linha correspondente
        df = df[df["Loja"] != loja_id]
        df.to_excel(data_file, index=False, engine="openpyxl")
        return jsonify({"status": "success", "message": "Loja excluída com sucesso."})
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
