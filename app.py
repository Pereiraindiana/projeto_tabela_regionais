from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import os

app = Flask(__name__)

# Configuração do Banco de Dados PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://matheus_pereira_da_silva_user:Jk1p0fmNU7Nxe4iUfn0pxD5OrzOdcrLh@dpg-cte54bt2ng1s73d8esn0-a/matheus_pereira_da_silva'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modelo da tabela no banco de dados
class Loja(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    regiao = db.Column(db.String(100), nullable=False)
    loja = db.Column(db.String(50), nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    pdv = db.Column(db.String(50), nullable=False)
    operador = db.Column(db.String(100), nullable=False)

# Criação da tabela no banco
with app.app_context():
    db.create_all()

# Página principal
@app.route("/")
def index():
    regionais = Loja.query.all()
    regionais_agrupados = {}
    for loja in regionais:
        regionais_agrupados.setdefault(loja.regiao, []).append(loja)
    return render_template("index.html", regionais=regionais_agrupados)

# Adicionar nova loja
@app.route("/adicionar", methods=["POST"])
def adicionar():
    data = request.get_json()
    nova_loja = Loja(
        regiao=data['regiao'].strip(),
        loja=str(data['loja']).strip(),
        nome=data['nome'].strip(),
        pdv=str(data['pdv']).strip(),
        operador=data['operador'].strip(),
    )
    db.session.add(nova_loja)
    db.session.commit()
    return jsonify({"message": "Loja adicionada com sucesso!"})

# Excluir loja
@app.route("/excluir", methods=["POST"])
def excluir():
    data = request.get_json()
    loja = Loja.query.filter_by(loja=str(data['loja']).strip()).first()
    if not loja:
        return jsonify({"message": "Erro: Loja não encontrada."}), 404
    db.session.delete(loja)
    db.session.commit()
    return jsonify({"message": "Loja excluída com sucesso!"})

# Editar loja
@app.route("/editar", methods=["POST"])
def editar():
    data = request.get_json()
    loja = Loja.query.filter_by(loja=str(data['loja']).strip()).first()
    if not loja:
        return jsonify({"message": "Erro: Loja não encontrada."}), 404

    loja.regiao = data['regiao'].strip()
    loja.nome = data['nome'].strip()
    loja.pdv = str(data['pdv']).strip()
    loja.operador = data['operador'].strip()
    db.session.commit()
    return jsonify({"message": "Loja editada com sucesso!"})

# Excluir todos os dados
@app.route("/excluir_tudo", methods=["POST"])
def excluir_tudo():
    db.session.query(Loja).delete()
    db.session.commit()
    return jsonify({"message": "Todos os dados foram excluídos!"})

# Importar dados de uma planilha Excel
@app.route("/importar", methods=["POST"])
def importar():
    file = request.files["file"]
    if not file:
        return jsonify({"message": "Erro: Nenhum arquivo enviado."}), 400

    try:
        # Ler a planilha Excel com pandas
        df = pd.read_excel(file)

        # Iterar sobre os dados e inserir no banco
        for _, row in df.iterrows():
            # Tratar dados nulos e converter para string
            nova_loja = Loja(
                regiao=str(row["Região"]).strip(),
                loja=str(row["Loja"]).strip(),
                nome=str(row["Nome"]).strip(),
                pdv=str(row["PDV"]).strip(),
                operador=str(row["Operador"]).strip(),
            )
            db.session.add(nova_loja)

        db.session.commit()
        return jsonify({"message": "Dados importados com sucesso!"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Erro ao importar dados: {str(e)}"}), 500

# Exportar os dados para Excel (Backup)
@app.route("/exportar", methods=["GET"])
def exportar():
    lojas = Loja.query.all()
    dados = [
        {"Região": loja.regiao, "Loja": loja.loja, "Nome": loja.nome, "PDV": loja.pdv, "Operador": loja.operador}
        for loja in lojas
    ]
    df = pd.DataFrame(dados)
    df.to_excel("backup_lojas.xlsx", index=False)
    return jsonify({"message": "Backup exportado com sucesso!"})

if __name__ == "__main__":
    app.run(debug=True)
