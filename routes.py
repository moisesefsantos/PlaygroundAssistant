from flask import Blueprint, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
import requests
from models import Usuario, Agente, Mensagem, Arquivo
from config import db, app, ALLOWED_EXTENSIONS
import openai
from dotenv import load_dotenv

load_dotenv()

# Definir Blueprints
mensagem_bp = Blueprint('mensagem_bp', __name__)
auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/login', methods=['GET'])
def login_google():
    auth_code = request.args.get('code')
    if not auth_code:
        return jsonify({"message": "Código de autenticação não encontrado!"}), 400
    
    # Trocar o código pelo token
    token_data = get_google_token(auth_code)
    if "access_token" not in token_data:
        return jsonify({"message": "Erro ao obter o token do Google"}), 400
    
    # Obter informações do usuário
    user_info = requests.get(
        "https://www.googleapis.com/oauth2/v1/userinfo",
        headers={"Authorization": f"Bearer {token_data['access_token']}"}
    ).json()
    
    # Extrair informações
    google_id = user_info.get('id')
    nome = user_info.get('name')
    email = user_info.get('email')

    # Salvar ou atualizar usuário
    usuario = Usuario.save_user(google_id, nome, email)
    
    return jsonify({
        "message": "Login bem-sucedido!",
        "usuario_id": usuario.id,
        "nome": usuario.nome,
        "email": usuario.email
    })

@auth_bp.route('/salvar_usuario', methods=['POST'])
def salvar_usuario():
    data = request.get_json()
    google_id = data.get("google_id")
    nome = data.get("nome")
    email = data.get("email")
    
    if not google_id or not nome or not email:
        return jsonify({"message": "Dados insuficientes!"}), 400
    
    usuario = Usuario.save_user(google_id, nome, email)
    return jsonify({
        "message": "Usuário salvo com sucesso!",
        "usuario_id": usuario.id,
        "nome": usuario.nome,
        "email": usuario.email
    })

def get_google_token(auth_code):
    CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
    CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
    REDIRECT_URI = "http://localhost:5000/login"

    data = {
        "code": auth_code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code"
    }
    response = requests.post("https://oauth2.googleapis.com/token", data=data)
    return response.json()

# Nova rota para listar todos os agentes de um usuário
@mensagem_bp.route('/agentes/usuario/<int:usuario_id>', methods=['GET'])
def listar_agentes_por_usuario(usuario_id):
    agenes = Agente.query.filter_by(usuario_id=usuario_id).all()  # Filtrando agentes pelo usuário_id
    if not agenes:
        return jsonify({"message": "Nenhum agente encontrado para este usuário"}), 404
    
    return jsonify([{
        "id": agente.id,
        "nome": agente.nome,
        "modelo": agente.modelo,
        "system_instructions": agente.system_instructions,
        "criado_em": agente.criado_em
    } for agente in agenes])

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

@mensagem_bp.route('/gerar_resposta', methods=['POST'])
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

        # Carregar arquivos associados ao agente
        arquivos = Arquivo.query.filter_by(agente_id=agente_id).all()
        arquivos_texto = "\n".join([  
            f"--- {arquivo.nome} ---\n{open(arquivo.caminho, 'r', encoding='utf-8').read()}"
            for arquivo in arquivos
        ])

        system_message = agente.system_instructions or "Você é um assistente prestativo."
        if arquivos_texto:
            system_message += f"\n\n--- Arquivos anexados ---\n{arquivos_texto}"

        # Chamada para a API OpenAI com a estrutura de mensagens correta
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Modelo que você está utilizando
            messages=[{
                "role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ]
        )

        resposta = response['choices'][0]['message']['content']

        # Salvar a mensagem e resposta no banco de dados
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

def register_routes(app):
    app.register_blueprint(mensagem_bp)
    app.register_blueprint(auth_bp)

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

    @app.route('/agentes/<int:id>', methods=['PUT'])
    def update_agent(id):
        agente = Agente.query.get(id)
        if not agente:
            return jsonify({"message": "Agente não encontrado"}), 404
        
        data = request.get_json()
        if "nome" in data:
            agente.nome = data["nome"]
        if "modelo" in data:
            agente.modelo = data["modelo"]
        if "system_instructions" in data:
            agente.system_instructions = data["system_instructions"]

        db.session.commit()

        return jsonify({
            "message": "Agente atualizado com sucesso!",
            "agente": {
                "id": agente.id,
                "nome": agente.nome,
                "modelo": agente.modelo,
                "system_instructions": agente.system_instructions
            }
        })

    @app.route('/agentes/<int:id>', methods=['DELETE'])
    def delete_agent(id):
        agente = Agente.query.get(id)
        if not agente:
            return jsonify({"message": "Agente não encontrado"}), 404
        
        db.session.delete(agente)
        db.session.commit()

        return jsonify({"message": "Agente excluído com sucesso!"})

    @app.route('/upload/<int:agente_id>', methods=['POST'])
    def upload_file(agente_id):
        if 'file' not in request.files:
            return jsonify({"message": "Nenhum arquivo enviado"}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({"message": "Nome de arquivo inválido"}), 400

        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            novo_arquivo = Arquivo(
                agente_id=agente_id,
                nome=filename,
                caminho=filepath,
                tipo=filename.rsplit('.', 1)[1].lower()
            )
            db.session.add(novo_arquivo)
            db.session.commit()

            return jsonify({"message": "Arquivo enviado com sucesso!", "arquivo_id": novo_arquivo.id}), 201

        return jsonify({"message": "Tipo de arquivo não permitido"}), 400

    return app
