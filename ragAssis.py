from openai import OpenAI

class FileSearchManager:
    def __init__(self, assistant_id):
        self.client = OpenAI(api_key="suakey")
        self.assistant_id = assistant_id
        self.vector_store_id = None  

    def create_vector_store(self, vector_store_name):
        """Cria um novo Vector Store e retorna o ID."""
        vector_store = self.client.beta.vector_stores.create(name=vector_store_name)
        self.vector_store_id = vector_store.id
        print(f"Vector Store criado: {self.vector_store_id}")
        return self.vector_store_id


    def upload_file(self, file_path):
         """Faz upload de um único arquivo e retorna o ID."""
         with open(file_path, "rb") as file:
             uploaded_file = self.client.files.create(file=file, purpose="assistants")
    
         print(f"Arquivo {file_path} enviado! ID: {uploaded_file.id}")
         return uploaded_file.id

    

    def remove_file(self, file_id):
        """Remove um arquivo do Vector Store."""
        if not self.vector_store_id:
            print("Vector Store não configurado!")
            return
        
        self.client.beta.vector_stores.files.delete(vector_store_id=self.vector_store_id, file_id=file_id)
        print(f"Arquivo {file_id} removido do Vector Store!")
     
    def add_files_to_vector_store(self, file_ids):
         """Adiciona arquivos ao Vector Store e atualiza o assistente."""
    
        
         if isinstance(file_ids, str):
       
             file_ids = [file_ids]  
        

         if not self.vector_store_id:
             print("Vector Store ainda não foi criado!")
             return

         try:
        
             batch = self.client.beta.vector_stores.file_batches.create(
             vector_store_id=self.vector_store_id, 
             file_ids=file_ids
             )

             
             print(f"Arquivos adicionados ao Vector Store. Batch ID: {batch.id}")
        
             
              
             update_response = self.client.beta.assistants.update(
             assistant_id=self.assistant_id,
             tool_resources={"file_search": {"vector_store_ids": [self.vector_store_id]}}
             )
             print("Assistente atualizado para acessar o Vector Store!")

         except Exception as e:
              print(f"Erro ao adicionar arquivos ao Vector Store: {e}")

