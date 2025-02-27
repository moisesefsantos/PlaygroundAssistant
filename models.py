from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from config import db

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    google_id = db.Column(db.String(255), unique=True, nullable=False)
    nome = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    @staticmethod
    def save_user(google_id, nome, email):
        existing_user = Usuario.query.filter_by(google_id=google_id).first()
        if not existing_user:
            novo_usuario = Usuario(google_id=google_id, nome=nome, email=email)
            db.session.add(novo_usuario)
            db.session.commit()
            return novo_usuario
        return existing_user

class Agente(db.Model):
    __tablename__ = 'agentes'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='CASCADE'))
    nome = db.Column(db.String(100), nullable=False)
    modelo = db.Column(db.String(50), nullable=False, default='gpt-4-turbo')
    system_instructions = db.Column(db.Text)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

class Mensagem(db.Model):
    __tablename__ = 'mensagens'
    id = db.Column(db.Integer, primary_key=True)
    agente_id = db.Column(db.Integer, db.ForeignKey('agentes.id', ondelete='CASCADE'))
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='CASCADE'))
    mensagem = db.Column(db.Text, nullable=False)
    resposta = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Arquivo(db.Model):
    __tablename__ = 'arquivos'
    id = db.Column(db.Integer, primary_key=True)
    agente_id = db.Column(db.Integer, db.ForeignKey('agentes.id', ondelete='CASCADE'), nullable=False)
    nome = db.Column(db.String(255), nullable=False)
    caminho = db.Column(db.String(500), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
