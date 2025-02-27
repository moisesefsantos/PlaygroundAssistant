 
from openai import OpenAI
import os
import streamlit as st
from ragAssis import FileSearchManager

 
 
   
manager = FileSearchManager(assist_id)
 
 
with st.container(border=True):
        uploaded_file =  st.file_uploader("Upload file", type=["txt", "pdf", "json", "csv"])
                      
        files= manager.get_vector_store_files()
    
        if files:
            st.write(f"📚 Arquivos associados ao assistente ({len(files)}):")
            for file in files:
                col1, col2 = st.columns([5, 1])
                with col1:
                    st.write(f"• {file.filename}")
                with col2:
                    if st.button("🗑️", key=f"del_file_{file.id}", help="Remover arquivo"):
                        if manager.remove_file(file.id):
                            st.success(f"Arquivo {file.filename} removido!")
                            st.rerun()
        else:
            st.info(" Faça upload abaixo.")
        
        
        if uploaded_file is not None:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"Arquivo selecionado: {uploaded_file.name}")
            with col2:
                if st.button("📤 Upload", key="upload_file"):
                    with st.spinner("Processando arquivo..."):
                        file_id = manager.upload_file(uploaded_file)
                        if file_id:
                            st.success(f"Arquivo {uploaded_file.name} adicionado ao assistente!")
                            st.rerun()

   
