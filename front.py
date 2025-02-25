import streamlit as st
from streamlit import expander
from streamlit_navigation_bar import st_navbar
from streamlit_option_menu import option_menu

#Definindo os títulos
st.set_page_config(layout="wide", page_title="Playground - Assistants")
#st.title('Playground Assistant')

#Configuração da sidebar
#st.sidebar.button("Chat")

st.markdown("# Playground")

with st.sidebar:
    selected = option_menu("Playground", ["Assistants",'Help'], 
        icons=['chat','exclamation'], menu_icon="cast", default_index=1)
    selected

if selected == 'Playground':
    st.subheader('Welcome to Playground')
    

elif selected=='Assistants':
    st.markdown("## Welcome to Playground Assistants")
    # Alterado para placeholder
    with st.sidebar:
         st.markdown("### Assistant Configuration")

         #Criação de novos Assistants
         
         created = 'Assistant 1'
         option_list = ['Choose Agent',created,'Create New']
         name = st.selectbox("Select Assistant", option_list)
        
         if name=='Create New':
            name_message = st.text_input('Assistant',placeholder="Name your new assistant")

            # Alterado para placeholder
            system_message = st.text_area("Context", placeholder="Enter system instructions...")

            with st.container():
                st.markdown('<div class="model-config">', unsafe_allow_html=True)

                model = st.selectbox("Model", ["gpt-4o", "gpt-4", "gpt-3.5-turbo"])
                temperature = st.slider("Temperature", 0.0, 1.0, 0.5)
                max_tokens = st.slider("Max tokens", 1, 4096, 2048)
                top_p = st.slider("Top P", 0.0, 1.0, 0.5)
                freq_penalty = st.slider("Frequency penalty", 0.0, 2.0, 0.0)
                pres_penalty = st.slider("Presence penalty", 0.0, 2.0, 0.0)

                st.markdown('<div class="save-preset-container">', unsafe_allow_html=True)
                st.button("Save")
                st.markdown('</div>', unsafe_allow_html=True)
            
                st.markdown('</div>', unsafe_allow_html=True)


         if name=='Assistant 1':
            name_message = st.text_input('Assistant',placeholder="Assistant 1")

            # Alterado para placeholder
            system_message = st.text_area("Context", placeholder="Old instructions")

            with st.container():
                st.markdown('<div class="model-config">', unsafe_allow_html=True)

                #model = st.selectbox("Model", ["gpt-4o", "gpt-4", "gpt-3.5-turbo"])
                temperature = st.slider("Temperature", 0.0, 1.0, 0.5)
                max_tokens = st.slider("Max tokens", 1, 4096, 2048)
                top_p = st.slider("Top P", 0.0, 1.0, 0.5)
                freq_penalty = st.slider("Frequency penalty", 0.0, 1.0, 0.0)
                pres_penalty = st.slider("Presence penalty", 0.0, 1.0, 0.0)

                st.markdown('<div class="save-preset-container">', unsafe_allow_html=True)
                st.button("Save")
                st.markdown('</div>', unsafe_allow_html=True)
            
                st.markdown('</div>', unsafe_allow_html=True)
    

    st.subheader("Thread")
    with st.container(border=True):
        chat_history = st.text_area("Chat history", height=250, key="chat_history")
        st.write(' ')

    with st.form('Messages'):
        col_input, col_button = st.columns([10, 1])
        with col_input:
            user_input = st.text_input('Enter your message',placeholder="Type here...")
        with col_button:
            st.write(' ')
            run = st.form_submit_button('Run')
        if run:
            st.write("Loading...")

    with st.container(border=True):
        st.file_uploader("Upload file", type=["txt", "pdf", "json", "csv"])

     # Botão "Clear the thread"

    clear = st.button('Clear History',type="primary")
    

elif selected=='Help':
    st.subheader('Help')
    st.write("Hope you are enjoying our app! In case you need help with it's funcions, please contact us")
