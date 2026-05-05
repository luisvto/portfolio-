from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)

def conectar():
    conn = sqlite3.connect("barbearia.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS agendamentos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente TEXT NOT NULL,
        servico TEXT NOT NULL,
        valor REAL NOT NULL,
        data TEXT NOT NULL,
        hora TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS custos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        valor REAL NOT NULL,
        mes TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()

init_db()

@app.route("/")
def home():
    return "API Barbearia rodando!"

@app.route("/agendamentos", methods=["GET"])
def listar_agendamentos():
    conn = conectar()
    agendamentos = conn.execute("SELECT * FROM agendamentos").fetchall()
    conn.close()
    return jsonify([dict(item) for item in agendamentos])

@app.route("/agendamentos", methods=["POST"])
def criar_agendamento():
    dados = request.json

    cliente = dados.get("cliente")
    servico = dados.get("servico")
    valor = dados.get("valor")
    data = dados.get("data")
    hora = dados.get("hora")

    if not cliente or not servico or not valor or not data or not hora:
        return jsonify({"erro": "Preencha todos os campos."}), 400

    conn = conectar()
    conflito = conn.execute(
        "SELECT id FROM agendamentos WHERE data = ? AND hora = ?",
        (data, hora)
    ).fetchone()

    if conflito:
        conn.close()
        return jsonify({"erro": "Já existe agendamento nesse dia e horário."}), 409

    conn.execute("""
        INSERT INTO agendamentos (cliente, servico, valor, data, hora)
        VALUES (?, ?, ?, ?, ?)
    """, (cliente, servico, valor, data, hora))

    conn.commit()
    conn.close()

    return jsonify({"mensagem": "Agendamento criado com sucesso!"}), 201

@app.route("/agendamentos/<int:id>", methods=["DELETE"])
def deletar_agendamento(id):
    conn = conectar()
    conn.execute("DELETE FROM agendamentos WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return jsonify({"mensagem": "Agendamento removido com sucesso!"})

@app.route("/custos", methods=["GET"])
def listar_custos():
    conn = conectar()
    custos = conn.execute("SELECT * FROM custos").fetchall()
    conn.close()
    return jsonify([dict(item) for item in custos])

@app.route("/custos", methods=["POST"])
def criar_custo():
    dados = request.json

    nome = dados.get("nome")
    valor = dados.get("valor")
    mes = dados.get("mes")

    if not nome or not valor or not mes:
        return jsonify({"erro": "Preencha nome, valor e mês."}), 400

    conn = conectar()
    conn.execute("""
        INSERT INTO custos (nome, valor, mes)
        VALUES (?, ?, ?)
    """, (nome, valor, mes))

    conn.commit()
    conn.close()

    return jsonify({"mensagem": "Custo criado com sucesso!"}), 201

@app.route("/custos/<int:id>", methods=["PUT"])
def editar_custo(id):
    dados = request.json

    nome = dados.get("nome")
    valor = dados.get("valor")
    mes = dados.get("mes")

    if not nome or not valor or not mes:
        return jsonify({"erro": "Preencha nome, valor e mês."}), 400

    conn = conectar()
    conn.execute("""
        UPDATE custos
        SET nome = ?, valor = ?, mes = ?
        WHERE id = ?
    """, (nome, valor, mes, id))

    conn.commit()
    conn.close()

    return jsonify({"mensagem": "Custo atualizado com sucesso!"})

@app.route("/custos/<int:id>", methods=["DELETE"])
def deletar_custo(id):
    conn = conectar()
    conn.execute("DELETE FROM custos WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return jsonify({"mensagem": "Custo removido com sucesso!"})

if __name__ == "__main__":
    app.run(debug=True)