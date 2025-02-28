import streamlit as st
import requests
import os
import psycopg2
from dotenv import load_dotenv
import PyPDF2
import json
import pandas as pd

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

# Função para salvar um assistente
def save_assistant(user_id, name, context, model, file_data, file_id=None):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO assistants (user_id, name, context, model, file, file_id)
        VALUES (%s, %s, %s, %s, %s, %s);
    """, (user_id, name, context, model, file_data, file_id))
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

# Função para atualizar um assistente
def update_assistant(user_id, assistant_id, name, context, model, file_data, file_id=None):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE assistants SET name = %s, context = %s, model = %s, file = %s, file_id = %s 
        WHERE id = %s AND user_id = %s;
    """, (name, context, model, file_data, file_id, assistant_id, user_id))
    conn.commit()
    cursor.close()
    conn.close()

# Função para enviar o arquivo para a OpenAI
def upload_file_to_openai(file, file_name):
    url = "https://api.openai.com/v1/files"
    headers = {
        "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}"
    }
    
    # Lê o conteúdo do arquivo
    file_content = file.read()
    files = {
        "file": (file_name, file_content, "application/octet-stream")
    }
    data = {
        "purpose": "assistants"  # Defina o propósito do arquivo aqui
    }
    response = requests.post(url, headers=headers, files=files, data=data)
    return response.json()

# Função para processar o arquivo
def process_uploaded_file(file, file_type):
    if file_type == "pdf":
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    elif file_type == "json":
        return json.load(file)
    elif file_type == "csv":
        df = pd.read_csv(file)
        return df.to_json()
    elif file_type == "txt":
        return file.read().decode("utf-8")

# Verifica se o usuário está autenticado
if "token" not in st.session_state:
    st.session_state.token = None
if "messages" not in st.session_state:
    st.session_state.messages = {}
if "assistants" not in st.session_state:
    st.session_state.assistants = {}
if "selected_assistant" not in st.session_state:
    st.session_state.selected_assistant = "Escolha um Assistente"

if st.session_state.token:
    user_info = requests.get(
        "https://www.googleapis.com/oauth2/v1/userinfo",
        headers={"Authorization": f"Bearer {st.session_state.token['access_token']}"}
    ).json()
    
    user_id = user_info.get("id")  # ID do Google como user_id
    st.session_state.assistants = {
        name: {"id": id, "context": context, "model": model, "file_id": file_id} 
        for id, name, context, model, _, file_id in get_assistants(user_id)
    }

    with st.sidebar:
        st.markdown("### Configuração de Assistente")
        options = ["Escolha um Assistente", "Criar Novo"] + list(st.session_state.assistants.keys())
        selection = st.selectbox("Selecione ou crie um assistente", options)

        if selection == "Criar Novo":
            new_name = st.text_input("Nome do Assistente")
            new_context = st.text_area("Contexto do Assistente")
            new_model = st.selectbox("Modelo", ["gpt-4", "gpt-3.5-turbo"])
            uploaded_file = st.file_uploader("Faça upload de um arquivo", type=["txt", "pdf", "json", "csv"])
            if st.button("Salvar Assistente", type="primary"):
                if new_name and new_context:
                    file_id = None
                    if uploaded_file:
                        file_type = uploaded_file.name.split('.')[-1]
                        file_data = process_uploaded_file(uploaded_file, file_type)
                        upload_response = upload_file_to_openai(uploaded_file, uploaded_file.name)
                        if 'error' in upload_response:
                            st.error(f"Erro ao enviar o arquivo: {upload_response['error']}")
                        else:
                            file_id = upload_response.get("id")
                    else:
                        file_data = None

                    save_assistant(user_id, new_name, new_context, new_model, file_data, file_id)
                    st.success(f"{new_name} criado! Arquivo enviado para OpenAI: {file_id}" if file_id else f"{new_name} criado sem arquivo!")
                    st.rerun()
        elif selection in st.session_state.assistants:
            assistant = st.session_state.assistants[selection]
            assistant_id = assistant["id"]
            st.session_state.selected_assistant = selection

            edit_name = st.text_input("Nome do Assistente", value=selection, key="edit_name")
            new_context = st.text_area("Contexto do Assistente", value=assistant["context"], key="edit_context")
            new_model = st.selectbox("Modelo", ["gpt-4", "gpt-3.5-turbo"], index=0 if assistant["model"] == "gpt-4" else 1, key="edit_model")
            uploaded_file = st.file_uploader("Faça upload de um arquivo", type=["txt", "pdf", "json", "csv"], key="edit_upload")

            if st.button("Atualizar Assistente", type="primary"):
                # Verifica se o novo nome já existe
                if edit_name in st.session_state.assistants and edit_name != selection:
                    st.error("Esse nome já está em uso por outro assistente.")
                else:
                    file_id = assistant["file_id"]  # Manter o file_id existente
                    file_data = None

                    # Se um novo arquivo for carregado, processa e faz o upload
                    if uploaded_file:
                        file_type = uploaded_file.name.split('.')[-1]
                        file_data = process_uploaded_file(uploaded_file, file_type)
                        upload_response = upload_file_to_openai(uploaded_file, uploaded_file.name)
                        if 'error' in upload_response:
                            st.error(f"Erro ao enviar o arquivo: {upload_response['error']}")
                        else:
                            file_id = upload_response.get("id")

                    update_assistant(user_id, assistant_id, edit_name, new_context, new_model, file_data, file_id)
                    st.session_state.assistants[edit_name] = {"id": assistant_id, "context": new_context, "model": new_model, "file_id": file_id}
                    if selection != edit_name:  # Remove o assistente antigo apenas se o nome foi mudado
                        st.session_state.assistants.pop(selection)
                    st.session_state.selected_assistant = edit_name
                    st.success(f"{edit_name} atualizado! Arquivo enviado para OpenAI: {file_id}" if file_id else f"{edit_name} atualizado sem novo arquivo!")
                    st.rerun()

            if st.button("Deletar Assistente", type="primary"):
                st.session_state.assistants.pop(selection)
                st.success(f"{selection} foi deletado.")
                st.rerun()

    st.title("Chat com Assistente")
    if st.session_state.selected_assistant not in ["Escolha um Assistente", "Criar Novo"]:
        assistant = st.session_state.assistants[st.session_state.selected_assistant]
        context = assistant["context"]
        model = assistant["model"]
        file_id = assistant["file_id"]

        st.session_state.messages.setdefault(st.session_state.selected_assistant, [])

        for message in st.session_state.messages[st.session_state.selected_assistant]:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("Digite sua mensagem"):
            st.session_state.messages[st.session_state.selected_assistant].append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                system_prompt = {"role": "system", "content": f"Você é um assistente chamado {st.session_state.selected_assistant}. {context}"}
                messages_payload = [system_prompt] + st.session_state.messages[st.session_state.selected_assistant]

                # Se houver um file_id, inclua na consulta
                if file_id:
                    messages_payload.append({"role": "user", "content": f"Considere as informações do arquivo com ID: {file_id}."})

                response = requests.post("https://api.openai.com/v1/chat/completions", json={"model": model, "messages": messages_payload}, headers={"Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}"})
                response_data = response.json()

                assistant_reply = response_data["choices"][0]["message"]["content"]
                st.session_state.messages[st.session_state.selected_assistant].append({"role": "assistant", "content": assistant_reply})
                message_placeholder.markdown(assistant_reply)
else:
    st.warning("Por favor, faça login.")