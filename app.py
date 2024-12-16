from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
import os

app = Flask(__name__)

# Caminho do arquivo para armazenar os dados
data_file = "dados_lojas.xlsx"

# Dados iniciais padrão
initial_data = [
    {"Região": "ZONA DA MATA", "Loja": 97, "Nome": "Viçosa", "PDV": "não tem cx", "Operador": "Operador 1"},
    {"Região": "OURO PRETO", "Loja": 15, "Nome": "Ponte Nova", "PDV": "16", "Operador": "Operador 2"},
    {"Região": "CARATINGA", "Loja": 44, "Nome": "Inhapim", "PDV": "6", "Operador": "Operador 3"},
]

# Cria o arquivo com dados iniciais caso ele não exista
if not os.path.exists(data_file):
    df = pd.DataFrame(initial_data)
    df.to_excel(data_file, index=False, engine="openpyxl")

@app.route("/")
def index():
    # Carrega os dados do arquivo Excel
    df = pd.read_excel(data_file, engine="openpyxl")
    grouped_data = df.groupby("Região")
    return render_template("index.html", regionais=grouped_data)

@app.route("/adicionar", methods=["POST"])
def adicionar():
    try:
        # Recebe os dados da requisição
        data = request.get_json()
        new_data = pd.DataFrame([{
            "Região": data.get("regiao").strip(),
            "Loja": data.get("loja"),
            "Nome": data.get("nome").strip(),
            "PDV": data.get("pdv").strip(),
            "Operador": data.get("operador", "").strip()
        }])

        # Adiciona os novos dados ao arquivo existente
        df = pd.read_excel(data_file, engine="openpyxl")
        df = pd.concat([df, new_data], ignore_index=True)
        df.to_excel(data_file, index=False, engine="openpyxl")
        return jsonify({"status": "success", "message": "Loja adicionada com sucesso!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/editar", methods=["POST"])
def editar():
    try:
        # Recebe os dados da requisição
        data = request.get_json()
        loja_id = data.get("loja")
        
        # Carrega os dados existentes
        df = pd.read_excel(data_file, engine="openpyxl")
        
        # Verifica se a loja existe
        if loja_id not in df["Loja"].values:
            return jsonify({"status": "error", "message": "Loja não encontrada."}), 404

        # Atualiza os dados da loja
        df.loc[df["Loja"] == loja_id, ["Região", "Nome", "PDV", "Operador"]] = [
            data.get("regiao").strip(),
            data.get("nome").strip(),
            data.get("pdv").strip(),
            data.get("operador", "").strip(),
        ]
        df.to_excel(data_file, index=False, engine="openpyxl")
        return jsonify({"status": "success", "message": "Dados editados com sucesso!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/excluir", methods=["POST"])
def excluir():
    try:
        # Recebe o ID da loja para exclusão
        data = request.get_json()
        loja_id = data.get("loja")

        # Carrega os dados existentes
        df = pd.read_excel(data_file, engine="openpyxl")

        # Verifica se a loja existe
        if loja_id not in df["Loja"].values:
            return jsonify({"status": "error", "message": "Loja não encontrada."}), 404

        # Remove a loja
        df = df[df["Loja"] != loja_id]
        df.to_excel(data_file, index=False, engine="openpyxl")
        return jsonify({"status": "success", "message": "Loja excluída com sucesso!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/excluir_tudo", methods=["POST"])
def excluir_tudo():
    try:
        # Exclui todos os dados
        df = pd.DataFrame(columns=["Região", "Loja", "Nome", "PDV", "Operador"])
        df.to_excel(data_file, index=False, engine="openpyxl")
        return jsonify({"status": "success", "message": "Todos os dados foram excluídos!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/exportar", methods=["GET"])
def exportar():
    try:
        # Envia o arquivo Excel para download
        return send_file(data_file, as_attachment=True)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
