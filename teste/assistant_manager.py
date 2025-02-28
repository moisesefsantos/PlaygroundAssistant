
from openai import OpenAI
import os
import streamlit as st


client = OpenAI(suakey)


class AssistantManager:
    def __init__(self):
        self.assistants = {}
        self.file_managers = {}
    
    def criar_assistente(self, nome, instrucoes, modelo="gpt-4"):
        """Creates a new assistant with file search capability"""
        try:
            with st.spinner("Creating assistant..."):
                assistant = client.beta.assistants.create(
                    name=nome,
                    instructions=instrucoes,
                    model=modelo
                )
                self.assistants[assistant.id] = assistant
                return assistant.id
        except Exception as e:
            st.error(f"Error creating assistant: {str(e)}")
            return None

    def remover_assistente(self, assist_id):
        """Removes an assistant"""
        try:
            with st.spinner("Removing assistant..."):
                if assist_id in self.assistants:
                    client.beta.assistants.delete(assist_id)
                    del self.assistants[assist_id]
                    return True
                return False
        except Exception as e:
            st.error(f"Error removing assistant: {str(e)}")
            return False
    
    def alterar_assistente(self, assist_id, novo_nome=None, novas_instrucoes=None):
        """Updates assistant configuration"""
        try:
            with st.spinner("Updating assistant..."):
                if assist_id not in self.assistants:
                    st.warning(f"Assistant {assist_id} not found!")
                    return False
                
                assistente_atual = self.assistants[assist_id]
                nome = novo_nome if novo_nome else assistente_atual.name
                instruções = novas_instrucoes if novas_instrucoes else assistente_atual.instructions
                
                response = client.beta.assistants.update(
                    assistant_id=assist_id,
                    name=nome,
                    instructions=instruções
                )
                
                self.assistants[assist_id] = response
                return True
        except Exception as e:
            st.error(f"Error updating assistant: {str(e)}")
            return False

    def listar_assistentes(self):
        """Lists all available assistants"""
        try:
            with st.spinner("Loading assistants..."):
                response = client.beta.assistants.list()
                self.assistants = {assist.id: assist for assist in response.data}
                return self.assistants
        except Exception as e:
            st.error(f"Error listing assistants: {str(e)}")
            return {}

    def get_file_manager(self, assist_id):
        """Gets or creates a file manager for the assistant"""
        if assist_id not in self.file_managers:
            from file_search_manager import FileSearchManager
            self.file_managers[assist_id] = FileSearchManager(assist_id)
        return self.file_managers[assist_id]

    def upload_file(self, assist_id, file_object):
        """Uploads a file and associates it with the assistant"""
        file_manager = self.get_file_manager(assist_id)
        file_id = file_manager.upload_file(file_object)
        if file_id:
            file_manager.add_files_to_vector_store(file_id)
        return file_id
        
    def remove_file(self, assist_id, file_id):
        """Removes a file from the assistant"""
        file_manager = self.get_file_manager(assist_id)
        return file_manager.remove_file(file_id)
        
    def get_assistant_files(self, assist_id):
        """Gets files associated with the assistant"""
        file_manager = self.get_file_manager(assist_id)
        return file_manager.get_vector_store_files()
        
    def enviar_mensagem(self, assist_id, mensagem_usuario):
        """Sends a message to the assistant and gets response"""
        try:
            with st.spinner("Processing message..."):
                assistente = self.assistants.get(assist_id)
                if not assistente:
                    raise ValueError(f"Assistant {assist_id} not found!")
                
                # Criar um novo thread para esta conversa
                thread = client.beta.threads.create()
                
                # Adicionar a mensagem do usuário ao thread
                client.beta.threads.messages.create(
                    thread_id=thread.id,
                    role="user",
                    content=mensagem_usuario
                )
                
                # Executar o assistente no thread
                run = client.beta.threads.runs.create(
                    thread_id=thread.id,
                    assistant_id=assist_id
                )
                
                # Aguardar a conclusão da execução com timeout e melhor indicação de progresso
                import time
                timeout = 60  # 60 segundos de timeout
                start_time = time.time()
                
                while True:
                    run_status = client.beta.threads.runs.retrieve(
                        thread_id=thread.id,
                        run_id=run.id
                    )
                    
                    if run_status.status == 'completed':
                        st.success("Response received!")
                        break
                    elif run_status.status == 'failed':
                        st.error(f"Run failed: {run_status.last_error}")
                        return None
                    elif run_status.status in ('expired', 'cancelled'):
                        st.warning(f"Run {run_status.status}")
                        return None
                    elif time.time() - start_time > timeout:
                        st.error("Response timeout. Please try again.")
                        return None
                        
                    # Feedback mais visível do status durante processamento
                    status_placeholder = st.empty()
                    status_text = f"Processando resposta... Status: {run_status.status}"
                    if hasattr(run_status, 'progress') and run_status.progress:
                        status_text += f" - {run_status.progress}%"
                    status_placeholder.info(status_text)
                    
                    time.sleep(1)
                
                # Obter a resposta do assistente
                messages = client.beta.threads.messages.list(
                    thread_id=thread.id
                )
                
                # A resposta mais recente é a do assistente
                # Usar uma abordagem mais robusta para encontrar a resposta
                if not messages or not hasattr(messages, 'data') or len(messages.data) == 0:
                    st.error("Nenhuma mensagem retornada pela API")
                    return "Não foi possível obter uma resposta do assistente."
                
                # Primeiro procurar a mensagem mais recente do assistente
                for msg in messages.data:
                    if msg.role == "assistant":
                        try:
                            # Verificar se msg.content existe e contém itens
                            if hasattr(msg, 'content') and msg.content and len(msg.content) > 0:
                                if hasattr(msg.content[0], 'text') and hasattr(msg.content[0].text, 'value'):
                                    response_content = msg.content[0].text.value
                                    print(f"Resposta encontrada: {response_content[:100]}...")  # Log para depuração
                                    # Garantir que há conteúdo na resposta
                                    if response_content:
                                        # Adicione mais logs para garantir visibilidade
                                        print(f"Retornando resposta completa de {len(response_content)} caracteres")
                                        return response_content
                        except (IndexError, AttributeError) as e:
                            st.error(f"Erro ao extrair resposta: {str(e)}")
                            import traceback
                            print(traceback.format_exc())  # Log para depuração
                            continue
                
                st.warning("Não foi possível obter uma resposta do assistente.")
                return "Não foi possível obter uma resposta do assistente."
        except Exception as e:
            st.error(f"Error processing message: {str(e)}")
            return None
