from flask import Flask, request, jsonify, render_template
import pandas as pd
import os

app = Flask(__name__)

# Caminho do arquivo Excel (dados locais)
data_file = "dados_lojas.xlsx"

# Função para carregar ou inicializar o Excel
def carregar_dados():
    if os.path.exists(data_file):
        return pd.read_excel(data_file, engine="openpyxl")
    else:
        df = pd.DataFrame(columns=["Região", "Loja", "Nome", "PDV", "Operador"])
        df.to_excel(data_file, index=False, engine="openpyxl")
        return df

# Página inicial - Carrega os dados e renderiza o HTML
@app.route("/")
def index():
    df = carregar_dados()
    return render_template("index.html", data=df.to_dict(orient="records"))

# Rota para adicionar nova loja
@app.route("/adicionar", methods=["POST"])
def adicionar():
    try:
        data = request.get_json()
        df = carregar_dados()
        
        # Nova linha para o DataFrame
        nova_loja = {
            "Região": data.get("regiao"),
            "Loja": str(data.get("loja")).strip(),
            "Nome": data.get("nome"),
            "PDV": data.get("pdv"),
            "Operador": data.get("operador")
        }
        
        # Adiciona ao DataFrame e salva
        df = pd.concat([df, pd.DataFrame([nova_loja])], ignore_index=True)
        df.to_excel(data_file, index=False, engine="openpyxl")
        
        return jsonify({"status": "success", "message": "Loja adicionada com sucesso."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Rota para editar loja existente
@app.route("/editar", methods=["POST"])
def editar():
    try:
        data = request.get_json()
        loja_id = str(data.get("loja")).strip()  # Padroniza como string
        
        if not loja_id:
            return jsonify({"status": "error", "message": "O campo 'loja' é obrigatório."}), 400

        df = carregar_dados()
        df["Loja"] = df["Loja"].astype(str).str.strip()

        # Verifica se a loja existe
        if loja_id not in df["Loja"].values:
            return jsonify({"status": "error", "message": "Loja não encontrada."}), 404

        # Atualiza os dados da loja
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

# Rota para excluir loja
@app.route("/excluir", methods=["POST"])
def excluir():
    try:
        data = request.get_json()
        loja_id = str(data.get("loja")).strip()
        
        df = carregar_dados()
        df["Loja"] = df["Loja"].astype(str).str.strip()

        if loja_id in df["Loja"].values:
            df = df[df["Loja"] != loja_id]
            df.to_excel(data_file, index=False, engine="openpyxl")
            return jsonify({"status": "success", "message": "Loja excluída com sucesso."})
        else:
            return jsonify({"status": "error", "message": "Loja não encontrada."}), 404

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Rota para importar dados de um arquivo Excel
@app.route("/importar", methods=["POST"])
def importar():
    try:
        file = request.files["file"]
        if not file:
            return jsonify({"status": "error", "message": "Nenhum arquivo enviado."}), 400

        # Lê o arquivo enviado
        df_novo = pd.read_excel(file, engine="openpyxl")
        
        # Carrega os dados existentes e concatena
        df_existente = carregar_dados()
        df_concatenado = pd.concat([df_existente, df_novo], ignore_index=True)

        # Remove duplicatas e salva
        df_concatenado.drop_duplicates(subset=["Loja"], keep="last", inplace=True)
        df_concatenado.to_excel(data_file, index=False, engine="openpyxl")

        return jsonify({"status": "success", "message": "Dados importados com sucesso."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
