from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
import os

app = Flask(__name__)

# Caminho para o arquivo Excel
EXCEL_FILE = "dados_lojas.xlsx"

# Inicializar o DataFrame
if not os.path.exists(EXCEL_FILE):
    df = pd.DataFrame(columns=["Região", "Loja", "Nome", "PDV", "Operador"])
    df.to_excel(EXCEL_FILE, index=False)
else:
    df = pd.read_excel(EXCEL_FILE)


# Página principal
@app.route("/")
def index():
    regionais = df.groupby("Região")
    return render_template("index.html", regionais=regionais)


# Adicionar nova loja
@app.route("/adicionar", methods=["POST"])
def adicionar():
    global df
    data = request.get_json()

    # Validação de campos
    if not all(key in data for key in ["regiao", "loja", "nome", "pdv", "operador"]):
        return jsonify({"message": "Todos os campos são obrigatórios."}), 400

    nova_linha = {
        "Região": data["regiao"],
        "Loja": data["loja"],
        "Nome": data["nome"],
        "PDV": data["pdv"],
        "Operador": data["operador"],
    }
    nova_linha_df = pd.DataFrame([nova_linha])
    df = pd.concat([df, nova_linha_df], ignore_index=True)
    df.to_excel(EXCEL_FILE, index=False)
    return jsonify({"message": "Loja adicionada com sucesso!"})


# Editar loja
@app.route("/editar", methods=["POST"])
def editar():
    global df
    data = request.get_json()

    # Validação de campos
    if not all(key in data for key in ["regiao", "loja", "nome", "pdv", "operador"]):
        return jsonify({"message": "Todos os campos são obrigatórios."}), 400

    loja = data["loja"]

    # Encontrar a linha com a loja correspondente
    linha = df[df["Loja"] == loja]
    if linha.empty:
        return jsonify({"message": "Loja não encontrada."}), 404

    # Atualizar os valores
    df.loc[df["Loja"] == loja, "Região"] = data["regiao"]
    df.loc[df["Loja"] == loja, "Nome"] = data["nome"]
    df.loc[df["Loja"] == loja, "PDV"] = data["pdv"]
    df.loc[df["Loja"] == loja, "Operador"] = data["operador"]

    # Salvar no arquivo
    df.to_excel(EXCEL_FILE, index=False)
    return jsonify({"message": "Loja editada com sucesso!"})


# Excluir loja
@app.route("/excluir", methods=["POST"])
def excluir():
    global df
    data = request.get_json()
    loja = data.get("loja")

    if not loja:
        return jsonify({"message": "O campo 'loja' é obrigatório."}), 400

    df = df[df["Loja"] != loja]
    df.to_excel(EXCEL_FILE, index=False)
    return jsonify({"message": "Loja excluída com sucesso!"})


# Excluir todos os dados
@app.route("/excluir_tudo", methods=["POST"])
def excluir_tudo():
    global df
    df = pd.DataFrame(columns=["Região", "Loja", "Nome", "PDV", "Operador"])
    df.to_excel(EXCEL_FILE, index=False)
    return jsonify({"message": "Todos os dados foram excluídos!"})


# Exportar Excel
@app.route("/exportar", methods=["GET"])
def exportar():
    return send_file(EXCEL_FILE, as_attachment=True)


# Importar dados
@app.route("/importar", methods=["POST"])
def importar():
    global df
    file = request.files.get("file")

    if file and file.filename.endswith(".xlsx"):
        try:
            new_df = pd.read_excel(file)
            if set(new_df.columns) == {"Região", "Loja", "Nome", "PDV", "Operador"}:
                df = new_df
                df.to_excel(EXCEL_FILE, index=False)
                return jsonify({"message": "Dados importados com sucesso!"})
            else:
                return jsonify({"message": "O arquivo possui colunas inválidas."}), 400
        except Exception as e:
            return jsonify({"message": f"Erro ao processar o arquivo: {str(e)}"}), 400

    return jsonify({"message": "Envie um arquivo Excel válido (.xlsx)."}), 400


if __name__ == "__main__":
    app.run(debug=True)
