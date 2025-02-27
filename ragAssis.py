
from openai import OpenAI
import os
import streamlit as st


client = OpenAI(suakey)

class FileSearchManager:
    def __init__(self, assistant_id):
        self.assistant_id = assistant_id
        self.vector_store_id = None

    def create_vector_store(self, vector_store_name):
        
        try:
            vector_store = client.beta.vector_stores.create(name=vector_store_name)
            self.vector_store_id = vector_store.id
            return self.vector_store_id
        except Exception as e:
            st.error(f"Erro ao criar Vector Store: {str(e)}")
            return None

    def upload_file(self, file_object):
     
        try:
            uploaded_file = client.files.create(
                file=file_object,
                purpose="assistants"
            )
            return uploaded_file.id
        except Exception as e:
            st.error(f"Erro no upload do arquivo: {str(e)}")
            return None

    def remove_file(self, file_id):
        
        try:
            if not self.vector_store_id:
                st.warning("Vector Store não configurado!")
                return False
            
            client.beta.vector_stores.files.delete(
                vector_store_id=self.vector_store_id,
                file_id=file_id
            )
            return True
        except Exception as e:
            st.error(f"Erro ao remover arquivo: {str(e)}")
            return False
     
    def add_files_to_vector_store(self, file_ids):
       
        try:
            
            if isinstance(file_ids, str):
                file_ids = [file_ids]

            if not self.vector_store_id:
                self.create_vector_store(f"vs_{self.assistant_id[:8]}")
                
            if not self.vector_store_id:
                st.error("Não foi possível criar Vector Store!")
                return False

            
            batch = client.beta.vector_stores.file_batches.create(
                vector_store_id=self.vector_store_id, 
                file_ids=file_ids
            )

            update_response = client.beta.assistants.update(
                assistant_id=self.assistant_id,
                tool_resources={"file_search": {"vector_store_ids": [self.vector_store_id]}}
            )
            
            return True
        except Exception as e:
            st.error(f"Erro ao adicionar arquivos ao Vector Store: {str(e)}")
            return False
            
    def get_vector_store_files(self):
      
        try:
            if not self.vector_store_id:
                return []
                
            files = client.beta.vector_stores.files.list(
                vector_store_id=self.vector_store_id
            )
            
            return files.data
        except Exception as e:
            st.error(f"Erro ao listar arquivos: {str(e)}")
            return []
