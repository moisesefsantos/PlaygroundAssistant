import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

# Configurações do banco de dados
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")

# Função para criar a conexão com o banco de dados
def create_connection():
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    return conn

# Função para criar a tabela de assistentes, se não existir
def create_table():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS assistants (
            id SERIAL PRIMARY KEY,
            user_id TEXT NOT NULL,
            name VARCHAR(255) NOT NULL,
            context TEXT NOT NULL,
            model VARCHAR(50) NOT NULL,
            file BYTEA,
            file_id VARCHAR,  -- Nova coluna para armazenar o ID do arquivo
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    cursor.close()
    conn.close()

# Função para criar todas as tabelas necessárias
def create_tables():
    create_table()  # Adicione aqui outras funções para criar mais tabelas, se necessário

# Função para excluir todas as tabelas (cuidado ao usar!)
def drop_all_tables():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("DROP SCHEMA public CASCADE; CREATE SCHEMA public;")
    conn.commit()
    cursor.close()
    conn.close()

# Função para salvar um assistente
def save_assistant(user_id, name, context, model, file, file_id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO assistants (user_id, name, context, model, file, file_id)
        VALUES (%s, %s, %s, %s, %s, %s);
    """, (user_id, name, context, model, file, file_id))
    conn.commit()
    cursor.close()
    conn.close()

# Função para obter assistentes de um usuário
def get_assistants(user_id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name, context, model, file, file_id FROM assistants WHERE user_id = %s;
    """, (user_id,))
    assistants = cursor.fetchall()
    cursor.close()
    conn.close()
    return assistants

# Função para deletar um assistente
def delete_assistant(user_id, assistant_id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        DELETE FROM assistants WHERE id = %s AND user_id = %s;
    """, (assistant_id, user_id))
    conn.commit()
    cursor.close()
    conn.close()

# Função para atualizar um assistente
def update_assistant(user_id, assistant_id, name, context, model, file, file_id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE assistants SET name = %s, context = %s, model = %s, file = %s, file_id = %s 
        WHERE id = %s AND user_id = %s;
    """, (name, context, model, file, file_id, assistant_id, user_id))
    conn.commit()
    cursor.close()
    conn.close()

# Chame drop_all_tables() apenas se você quiser excluir todas as tabelas.
# drop_all_tables()  # Descomente esta linha para excluir todas as tabelas

# Chame create_tables quando o aplicativo iniciar
if __name__ == "__main__":
    create_tables()
