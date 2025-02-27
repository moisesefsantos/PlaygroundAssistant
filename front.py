import streamlit as st
from streamlit import expander
from streamlit_navigation_bar import st_navbar
from streamlit_option_menu import option_menu

#Definindo os títulos
#st.set_page_config(layout="wide", page_title="Playground Assistants")

    
st.markdown("## :material/dashboard: Welcome to Playground Assistants")
            
    # Menu Lateral
with st.sidebar:
    st.markdown("### Assistant Configuration")

        #Criação de novos Assistants
         
    created = ['Assistant 1', 'Assistant 2']
    option_list = ['Choose Agent','Create New'] + created
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

        if st.button('Save', type='primary'):
            created.append(st.session_state.name_message)
            st.success('Assistant Created!')


    if name in created:
        with st.container(border=True):
            name_message = st.text_input('Assistant Name',value=name)
            system_message = st.text_area("Context", value="Old instructions")

        with st.container():
            st.markdown('<div class="model-config">', unsafe_allow_html=True)

            model = st.selectbox("Model", ["gpt-4o", "gpt-4", "gpt-3.5-turbo"])
            temperature = st.slider("Temperature", 0.0, 1.0, 0.5)
            max_tokens = st.slider("Max tokens", 1, 4096, 2048)
            top_p = st.slider("Top P", 0.0, 1.0, 0.5)
            freq_penalty = st.slider("Frequency penalty", 0.0, 1.0, 0.0)
            pres_penalty = st.slider("Presence penalty", 0.0, 1.0, 0.0)

            
            st.markdown('</div>', unsafe_allow_html=True)

        if st.button('Save', type='primary'):
            st.success('Saved!')

        if st.button('Delete', type='primary',icon=':material/bomb:'):
            st.success('Assistant deleted')
    

st.subheader("Thread")
with st.container(border=True):
    chat_history = st.text_area("Chat history", height=250, key="chat_history")
    st.write(' ')

#with st.form('Messages'):
    #col_input, col_button = st.columns([10, 1])
    #with col_input:
    user_input = st.chat_input('Enter your message') #,placeholder="Type here..."
    #with col_button:
    #    st.write(' ')
    #    run = st.button('Run', type='primary')
    #if run:
    #    st.write("Loading...")

    with st.container(border=True):
        st.file_uploader("Upload file", type=["txt", "pdf", "json", "csv"])

     # Botão "Clear the thread"

clear = st.button('Clear History',type="primary")
    