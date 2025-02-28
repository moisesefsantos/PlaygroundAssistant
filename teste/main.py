import streamlit as st
import os
from assistant_manager import AssistantManager
from thread_manager import ThreadManager

# Page configuration must be the first Streamlit command
st.set_page_config(
    page_title="OpenAI Playground",
    page_icon="🤖",
    layout="wide",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': "OpenAI Playground"
    }
)


# Initialize managers
manager = AssistantManager()
manager_thread = ThreadManager()

st.markdown("## OpenAI Playground")

# Sidebar for Assistant Configuration
with st.sidebar:
    st.markdown("### Assistant Configuration")

    # List available assistants
    assistentes = manager.listar_assistentes()
    option_list = ['Choose Agent', 'Create New'] + [assist.name for assist in assistentes.values()]
    selected = st.selectbox("Select Assistant", option_list)

    # Create new assistant
    if selected == 'Create New':
        with st.form("new_assistant"):
            name_message = st.text_input('Assistant Name', placeholder="Name your assistant")
            system_message = st.text_area("Instructions", placeholder="Enter system instructions...")
            model = st.selectbox("Model", ["gpt-4o", "gpt-4", "gpt-3.5-turbo"])

            if st.form_submit_button("Create Assistant"):
                if name_message and system_message:
                    assist_id = manager.criar_assistente(name_message, system_message, modelo=model)
                    if assist_id:
                        st.success("Assistant created successfully!")
                        st.rerun()
                else:
                    st.error("Please fill all fields")

    # Edit existing assistant
    elif selected in [assist.name for assist in assistentes.values()]:
        assist_id = [k for k, v in assistentes.items() if v.name == selected][0]
        with st.form("edit_assistant"):
            name_message = st.text_input('Nome do Assistente', value=assistentes[assist_id].name)
            system_message = st.text_area("Instrucao", value=assistentes[assist_id].instructions)

            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("Modificar"):
                    if manager.alterar_assistente(assist_id, name_message, system_message):
                        st.success("Assistant updated!")
                        st.rerun()

            with col2:
                if st.form_submit_button("Delete", type="secondary"):
                    if manager.remover_assistente(assist_id):
                        st.success("Assistant deleted!")
                        st.rerun()
        
        # Seção para gerenciamento de arquivos RAG
        st.markdown("### 📎 Arquivos (RAG)")
        
        # Mostrar arquivos existentes
        files = manager.get_assistant_files(assist_id)
        if files:
            st.write(f"📚 Arquivos associados ao assistente ({len(files)}):")
            for file in files:
                col1, col2 = st.columns([5, 1])
                with col1:
                    st.write(f"• {file.filename}")
                with col2:
                    if st.button("🗑️", key=f"del_file_{file.id}", help="Remover arquivo"):
                        if manager.remove_file(assist_id, file.id):
                            st.success(f"Arquivo {file.filename} removido!")
                            st.rerun()
        else:
            st.info(" Faça upload abaixo.")
        
        # Interface para upload de novos arquivos
        uploaded_file = st.file_uploader("📎 Adicionar conhecimento ao assistente", 
                                        type=["pdf", "txt", "docx", "csv"],
                                        help="Adicione arquivos PDF, TXT, DOCX ou CSV para que o assistente possa acessar essas informações")
        
        if uploaded_file is not None:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"Arquivo selecionado: {uploaded_file.name}")
            with col2:
                if st.button("📤 Upload", key="upload_file"):
                    with st.spinner("Processando arquivo..."):
                        file_id = manager.upload_file(assist_id, uploaded_file)
                        if file_id:
                            st.success(f"Arquivo {uploaded_file.name} adicionado ao assistente!")
                            st.rerun()

# Main chat interface
if selected != 'Choose Agent' and selected != 'Create New':
    # Initialize or get thread
    if 'thread_id' not in st.session_state or not st.session_state.thread_id:
        st.session_state.thread_id = manager_thread.criar_thread()
    
    # Verify thread exists
    try:
        thread_exists = st.session_state.thread_id in manager_thread.threads
        if not thread_exists:
            # Try to retrieve thread from API
            try:
                client.beta.threads.retrieve(st.session_state.thread_id)
            except:
                # Thread doesn't exist, create a new one
                st.session_state.thread_id = manager_thread.criar_thread()
    except Exception as e:
        st.error(f"Error verifying thread: {str(e)}")
        st.session_state.thread_id = manager_thread.criar_thread()

    # Display messages - usa abordagem híbrida para garantir exibição
    messages = []
    try:
        messages = manager_thread.listar_mensagens(st.session_state.thread_id)
        # Atualiza o cache para caso de falha futura
        if messages and len(messages) > 0:
            st.session_state.messages_history = messages
            print(f"Armazenando {len(messages)} mensagens no histórico")
        elif st.session_state.get('messages_history') and len(st.session_state.messages_history) > 0:
            # Se não conseguiu carregar mensagens, mas temos cache, use o cache
            messages = st.session_state.messages_history
            print(f"Usando {len(messages)} mensagens do cache")
    except Exception as e:
        st.error(f"Erro ao listar mensagens do thread: {str(e)}")
        if st.session_state.get('messages_history'):
            messages = st.session_state.messages_history
            
    # Exibir mensagens com manipulação mais robusta
    for i, msg in enumerate(messages):
        with st.container():
            msg_class = "user-message" if msg["role"] == "user" else "assistant-message"
            msg_id = msg.get("id", f"local_msg_{i}")  # Usar ID ou gerar um local se não tiver
            is_user_message = msg["role"] == "user"  # Verificar se é mensagem do usuário
            
            st.markdown(f"<div class='message-container {msg_class}'>", unsafe_allow_html=True)

            # Mostrar texto da mensagem
            if is_user_message:
                col1, col2 = st.columns([8, 2])
                with col1:
                    st.text_area("", msg["content"], disabled=True, key=f"msg_{msg_id}_{i}")
                
                # Botões de edição e exclusão apenas para mensagens do usuário
                with col2:
                    if st.button("Delete", key=f"del_{msg_id}_{i}", type="secondary"):
                        # Adicionar log para depuração
                        print(f"Tentando deletar mensagem {msg_id}")
                        if manager_thread.deletar_prompt(st.session_state.thread_id, msg_id):
                            # Se deletado com sucesso, atualizar o histórico local
                            if 'messages_history' in st.session_state:
                                st.session_state.messages_history = [
                                    m for m in st.session_state.messages_history 
                                    if m.get('id') != msg_id
                                ]
                            st.rerun()

                    if st.button("Edit", key=f"edit_{msg_id}_{i}"):
                        st.session_state[f"edit_mode_{msg_id}_{i}"] = True

                # Modo de edição para mensagens do usuário
                if st.session_state.get(f"edit_mode_{msg_id}_{i}", False):
                    new_content = st.text_area("Edit message:", msg["content"], key=f"edit_area_{msg_id}_{i}")
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Salvar", key=f"save_{msg_id}_{i}"):
                            if manager_thread.modificar_prompt(st.session_state.thread_id, msg_id, new_content):
                                del st.session_state[f"edit_mode_{msg_id}_{i}"]
                                st.rerun()
                    with col2:
                        if st.button("Salvar e reenviar", key=f"save_get_{msg_id}_{i}"):
                            if manager_thread.modificar_prompt(st.session_state.thread_id, msg_id, new_content):
                                # Obter o ID do assistente selecionado
                                assist_id = [k for k, v in assistentes.items() if v.name == selected][0]
                                
                                # Obter resposta do assistente com a mensagem editada
                                with st.spinner("Getting response from assistant..."):
                                    response = manager.enviar_mensagem(assist_id, new_content)
                                    if response:
                                        # Adicionar resposta do assistente ao thread
                                        if manager_thread.criar_prompt(st.session_state.thread_id, "assistant", response):
                                            # Atualizar o histórico de mensagens
                                            st.session_state.messages_history = manager_thread.listar_mensagens(st.session_state.thread_id)
                                            
                                            # Limpar o modo de edição
                                            del st.session_state[f"edit_mode_{msg_id}_{i}"]
                                            
                                            # Mostrar feedback e recarregar
                                            message_placeholder = st.empty()
                                            message_placeholder.success("Mensagem editada e nova resposta obtida!")
                                            st.rerun()
                                        else:
                                            st.error("Failed to add assistant response to thread")
                                    else:
                                        st.error("Failed to get response from assistant")
            else:
                # Para mensagens do assistente, apenas mostrar o conteúdo sem botões
                st.text_area("", msg["content"], disabled=True, key=f"msg_{msg_id}_{i}")

            st.markdown("</div>", unsafe_allow_html=True)

    # Message input - com inicialização correta do campo
    if "message_input" not in st.session_state:
        st.session_state.message_input = ""
        
    with st.form("message_form"):
        message = st.text_area("Message:", key="message_input")
        if st.form_submit_button("Send"):
            if message:
                assist_id = [k for k, v in assistentes.items() if v.name == selected][0]

                # Create user message
                if manager_thread.criar_prompt(st.session_state.thread_id, "user", message):
                    # Get assistant response
                    with st.spinner("Getting response from assistant..."):
                        response = manager.enviar_mensagem(assist_id, message)
                        if response:
                            # Add assistant response to thread
                            if manager_thread.criar_prompt(st.session_state.thread_id, "assistant", response):
                                # Armazenar mensagens na session_state para garantir que sejam exibidas
                                if 'messages_history' not in st.session_state:
                                    st.session_state.messages_history = []
                                
                                # Atualiza o histórico de mensagens no session_state
                                st.session_state.messages_history = manager_thread.listar_mensagens(st.session_state.thread_id)
                                
                                # Limpar o campo de entrada antes de recarregar
                                message_placeholder = st.empty()
                                message_placeholder.success("Mensagem enviada com sucesso!")
                                
                                # Forçar recarregamento mais eficiente
                                st.rerun()
                            else:
                                st.error("Failed to add assistant response to thread")
                        else:
                            st.error("Failed to get response from assistant")
                else:
                    st.error("Failed to add user message to thread")

    # Thread management
    if st.button("Limpar Thread"):
        if st.session_state.get('thread_id'):
            manager_thread.deletar_thread(st.session_state.thread_id)
        st.session_state.thread_id = manager_thread.criar_thread()
        st.rerun()

else:
    st.info("Please select or create an assistant to start chatting")
