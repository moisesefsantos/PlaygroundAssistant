from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv
import openai

load_dotenv()

ALLOWED_EXTENSIONS = {'c', 'cs', 'cpp', 'doc', 'docx', 'go', 'html', 'java', 'json',
'md', 'pdf', 'php', 'pptx', 'py', 'rb', 'tex', 'txt', 'css', 'js',
'sh', 'ts', 'dot', 'htm', 'shtml', 'ehtml', 'shtm', 'text', 'mjs'}

class Config:
    SQLALCHEMY_DATABASE_URI = 'postgresql://playground:smlh1224@localhost:5432/playground?client_encoding=utf8'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'uploads/'

# Criar pasta de uploads
os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)

# Configuração do OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

# Inicialização do app e db
app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)