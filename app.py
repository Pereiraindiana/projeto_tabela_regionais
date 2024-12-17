from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
import os

app = Flask(__name__)

# Caminho para o arquivo Excel
EXCEL_FILE = "dados_lojas.xlsx"

# Função para carregar os dados
def load_data():
    if not os.path.exists(EXCEL_FILE):
        df = pd.DataFrame(columns=["Região", "Loja", "Nome", "PDV", "Operador"])
        df.to_excel(EXCEL_FILE, index=False)
    else:
        df = pd.read_excel(EXCEL_FILE)
    return df

# Carregar o DataFrame
df = load_data()

# Página principal
@app.route("/")
def index():
    global df
    regionais = df.groupby("Região")
    return render_template("index.html", regionais=regionais)

# Adicionar nova loja
@app.route("/adicionar", methods=["POST"])
def adicionar():
    global df
    data = request.get_json()
    nova_linha = {
        "Região": data["regiao"].strip(),
        "Loja": str(data["loja"]).strip(),
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
    loja = str(data["loja"]).strip()
    
    if loja not in df["Loja"].astype(str).values:
        return jsonify({"message": "Erro: Loja não encontrada."}), 404
    
    df = df[df["Loja"].astype(str) != loja]
    df.to_excel(EXCEL_FILE, index=False)
    return jsonify({"message": "Loja excluída com sucesso!"})

# Editar loja
@app.route("/editar", methods=["POST"])
def editar():
    global df
    data = request.get_json()
    loja = str(data["loja"]).strip()
    
    if loja not in df["Loja"].astype(str).values:
        return jsonify({"message": "Erro: Loja não encontrada."}), 404

    # Editar os valores
    mask = df["Loja"].astype(str) == loja
    df.loc[mask, "Região"] = data["regiao"].strip()
    df.loc[mask, "Nome"] = data["nome"].strip()
    df.loc[mask, "PDV"] = data["pdv"].strip()
    df.loc[mask, "Operador"] = data["operador"].strip()

    # Salvar no Excel
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
