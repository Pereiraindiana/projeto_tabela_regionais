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
    nova_linha = {
        "Região": data["regiao"].strip(),
        "Loja": data["loja"].strip(),
        "Nome": data["nome"].strip(),
        "PDV": data["pdv"].strip(),
        "Operador": data["operador"].strip(),
    }
    df = pd.concat([df, pd.DataFrame([nova_linha])], ignore_index=True)
    df.to_excel(EXCEL_FILE, index=False)
    return jsonify({"message": "Loja adicionada com sucesso!"})


# Excluir loja
@app.route("/excluir", methods=["POST"])
def excluir():
    global df
    data = request.get_json()
    loja = data["loja"].strip().lower()  # Ignorar espaços e diferenças de maiúsculas/minúsculas
    
    # Filtrar e manter apenas as lojas que não são iguais ao valor informado
    original_len = len(df)
    df = df[~df["Loja"].str.strip().str.lower().eq(loja)]

    if len(df) < original_len:
        df.to_excel(EXCEL_FILE, index=False)
        return jsonify({"message": "Loja excluída com sucesso!"})
    else:
        return jsonify({"message": "Erro: Loja não encontrada."}), 404


# Editar loja
@app.route("/editar", methods=["POST"])
def editar():
    global df
    data = request.get_json()
    loja = data["loja"].strip().lower()  # Normalizar a busca

    # Encontrar a linha com a loja correspondente
    mask = df["Loja"].str.strip().str.lower() == loja

    if not mask.any():
        return jsonify({"message": "Erro: Loja não encontrada."}), 404

    # Atualizar os valores
    df.loc[mask, "Região"] = data["regiao"].strip()
    df.loc[mask, "Nome"] = data["nome"].strip()
    df.loc[mask, "PDV"] = data["pdv"].strip()
    df.loc[mask, "Operador"] = data["operador"].strip()

    # Salvar no arquivo
    df.to_excel(EXCEL_FILE, index=False)
    return jsonify({"message": "Loja editada com sucesso!"})


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
    file = request.files["file"]
    if file:
        df = pd.read_excel(file)
        df.to_excel(EXCEL_FILE, index=False)
        return jsonify({"message": "Dados importados com sucesso!"})
    return jsonify({"message": "Erro ao importar o arquivo"}), 400


if __name__ == "__main__":
    app.run(debug=True)
