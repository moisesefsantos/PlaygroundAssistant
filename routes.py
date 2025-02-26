from flask import Blueprint, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
from models import Usuario, Agente, Mensagem, Arquivo
from config import db, app, ALLOWED_EXTENSIONS
import openai

# Inicializar cliente OpenAI
client = openai.OpenAI()

# Definir o Blueprint no início
mensagem_bp = Blueprint('mensagem_bp', __name__)

@mensagem_bp.route('/mensagens/<int:agente_id>', methods=['GET'], endpoint='get_mensagens')
def get_mensagens(agente_id):
    mensagens = Mensagem.query.filter_by(agente_id=agente_id).order_by(Mensagem.timestamp.asc()).all()
    if not mensagens:
        return jsonify({"message": "Nenhuma mensagem encontrada para este agente"}), 404

    return jsonify([{ 
        "id": msg.id,
        "agente_id": msg.agente_id,
        "usuario_id": msg.usuario_id,
        "mensagem": msg.mensagem,
        "resposta": msg.resposta,
        "timestamp": msg.timestamp.strftime("%Y-%m-%d %H:%M:%S")
    } for msg in mensagens])

def register_routes(app):
    app.register_blueprint(mensagem_bp)

    @app.route('/usuarios', methods=['POST'])
    def create_user():
        try:
            data = request.get_json()
            novo_usuario = Usuario(**data)
            db.session.add(novo_usuario)
            db.session.commit()
            return jsonify({"message": "Usuário criado com sucesso!", "usuario_id": novo_usuario.id}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": "Erro ao criar usuário", "error": str(e)}), 400

    @app.route('/agentes', methods=['POST'])
    def create_agent():
        try:
            data = request.get_json()
            novo_agente = Agente(**data)
            db.session.add(novo_agente)
            db.session.commit()
            return jsonify({"message": "Agente criado com sucesso!", "agente_id": novo_agente.id}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": "Erro ao criar agente", "error": str(e)}), 400

    @app.route('/agentes/<int:id>', methods=['GET'])
    def get_agent(id):
        agente = Agente.query.get(id)
        if not agente:
            return jsonify({"message": "Agente não encontrado"}), 404
        return jsonify({
            "id": agente.id,
            "nome": agente.nome,
            "modelo": agente.modelo,
            "system_instructions": agente.system_instructions,
            "criado_em": agente.criado_em
        })

    @app.route('/gerar_resposta', methods=['POST'])
    def gerar_resposta():
        try:
            data = request.get_json()
            agente_id = data.get('agente_id')
            prompt = data.get('prompt', '')

            if not prompt or not agente_id:
                return jsonify({"erro": "O agente_id e o prompt são obrigatórios"}), 400

            agente = Agente.query.get(agente_id)
            if not agente:
                return jsonify({"erro": "Agente não encontrado"}), 404

            arquivos = Arquivo.query.filter_by(agente_id=agente_id).all()
            arquivos_texto = "\n".join([  
                f"--- {arquivo.nome} ---\n{open(arquivo.caminho, 'r', encoding='utf-8').read()}"
                for arquivo in arquivos
            ])

            system_message = agente.system_instructions or "Você é um assistente prestativo."
            if arquivos_texto:
                system_message += f"\n\n--- Arquivos anexados ---\n{arquivos_texto}"

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ]
            )

            resposta = response.choices[0].message.content

            nova_mensagem = Mensagem(
                agente_id=agente_id,
                usuario_id=data.get('usuario_id'),
                mensagem=prompt,
                resposta=resposta
            )
            db.session.add(nova_mensagem)
            db.session.commit()

            return jsonify({"resposta": resposta})
        except Exception as e:
            return jsonify({"erro": f"Erro ao processar requisição: {str(e)}"}), 400

    return app
