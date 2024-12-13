import os
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy

# Configuração do Flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dados_lojas.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelo para a tabela "Loja"
class Loja(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    regiao = db.Column(db.String(100), nullable=False)
    loja = db.Column(db.String(100), unique=True, nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    pdv = db.Column(db.String(100), nullable=False)
    operador = db.Column(db.String(100), nullable=True)

# Rota inicial
@app.route('/')
def index():
    # Obter dados agrupados por região
    regionais = {}
    lojas = Loja.query.all()
    for loja in lojas:
        if loja.regiao not in regionais:
            regionais[loja.regiao] = []
        regionais[loja.regiao].append(loja)
    return render_template('index.html', regionais=regionais)

# Rota para adicionar uma nova loja
@app.route('/adicionar', methods=['POST'])
def adicionar():
    try:
        data = request.get_json()
        nova_loja = Loja(
            regiao=data.get("regiao").strip(),
            loja=str(data.get("loja")).strip(),
            nome=data.get("nome").strip(),
            pdv=data.get("pdv").strip(),
            operador=data.get("operador", "").strip()
        )
        db.session.add(nova_loja)
        db.session.commit()
        return jsonify({"status": "success", "message": "Loja adicionada com sucesso."})
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

# Rota para editar uma loja existente
@app.route('/editar', methods=['POST'])
def editar():
    try:
        data = request.get_json()
        loja_id = str(data.get("loja")).strip()
        loja = Loja.query.filter_by(loja=loja_id).first()

        if not loja:
            return jsonify({"status": "error", "message": "Loja não encontrada."}), 404

        loja.regiao = data.get("regiao").strip()
        loja.nome = data.get("nome").strip()
        loja.pdv = data.get("pdv").strip()
        loja.operador = data.get("operador", "").strip()

        db.session.commit()
        return jsonify({"status": "success", "message": "Dados editados com sucesso."})
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

# Rota para excluir uma loja
@app.route('/excluir', methods=['POST'])
def excluir():
    try:
        data = request.get_json()
        loja_id = str(data.get("loja")).strip()
        loja = Loja.query.filter_by(loja=loja_id).first()

        if not loja:
            return jsonify({"status": "error", "message": "Loja não encontrada."}), 404

        db.session.delete(loja)
        db.session.commit()
        return jsonify({"status": "success", "message": "Loja excluída com sucesso."})
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

# Rota para excluir todos os dados
@app.route('/excluir_tudo', methods=['POST'])
def excluir_tudo():
    try:
        db.session.query(Loja).delete()
        db.session.commit()
        return jsonify({"status": "success", "message": "Todos os dados foram excluídos."})
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

# Rota para exportar os dados
@app.route('/exportar', methods=['GET'])
def exportar():
    try:
        lojas = Loja.query.all()
        data = [{"Região": loja.regiao, "Loja": loja.loja, "Nome": loja.nome, "PDV": loja.pdv, "Operador": loja.operador} for loja in lojas]
        return jsonify(data)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Inicialização do Banco de Dados
@app.before_first_request
def setup():
    db.create_all()
    if Loja.query.count() == 0:
        # Dados iniciais
        initial_data = [
            {"regiao": "ZONA DA MATA", "loja": 97, "nome": "Viçosa", "pdv": "não tem cx", "operador": "Operador 1"},
            {"regiao": "OURO PRETO", "loja": 15, "nome": "Ponte Nova", "pdv": "16", "operador": "Operador 2"},
            {"regiao": "CARATINGA", "loja": 44, "nome": "Inhapim", "pdv": "6", "operador": "Operador 3"},
        ]
        for item in initial_data:
            loja = Loja(**item)
            db.session.add(loja)
        db.session.commit()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
