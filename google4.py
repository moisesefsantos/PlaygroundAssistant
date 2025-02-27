import streamlit as st
import requests
import urllib.parse
import webbrowser
import os
from dotenv import load_dotenv

load_dotenv()

# Configuração do Google OAuth
CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
REDIRECT_URI = "http://localhost:8501"
BACKEND_URL = "http://localhost:5000/salvar_usuario"  # Endpoint do backend

AUTH_URL = "https://accounts.google.com/o/oauth2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"

# Scopes necessários
SCOPES = ["openid", "email", "profile"]

# Gerar URL de login
def get_google_auth_url():
    params = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": " ".join(SCOPES),
        "access_type": "offline",
        "include_granted_scopes": "true",
        "prompt": "consent"
    }
    return f"{AUTH_URL}?{urllib.parse.urlencode(params)}"

# Trocar código pelo token
def get_google_token(auth_code):
    data = {
        "code": auth_code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code"
    }
    response = requests.post(TOKEN_URL, data=data)
    return response.json()

if "token" not in st.session_state:
    st.session_state.token = None

query_params = st.query_params.to_dict()
auth_code = query_params.get("code")

if auth_code and not st.session_state.token:
    token_data = get_google_token(auth_code)
    if "access_token" in token_data:
        st.session_state.token = token_data
        st.rerun()

#Definindo pages de Assistants e Logout

def logout():
    if st.button("Log out",type="primary"):
        st.session_state.token = False
        st.rerun()

login_page = st.Page(get_google_auth_url, title="Log in", icon=":material/login:")
logout_page = st.Page(logout, title="Log out", icon=":material/logout:")

#Tentando fazer o redirecionamento com outro botão
#def redirect(_url):
#    auth_url = get_google_auth_url()
#    st.markdown(auth_url, unsafe_allow_html=True)
    

#Redireciona para page do front
if st.session_state.token:
    
    #st.success("Login realizado com sucesso! 🎉")
    user_info = requests.get(
       "https://www.googleapis.com/oauth2/v1/userinfo",
        headers={"Authorization": f"Bearer {st.session_state.token['access_token']}"}
    ).json()

    #st.write(f"**Nome:** {user_info.get('name')}")
    #st.write(f"**Email:** {user_info.get('email')}")
    #st.image(user_info.get("picture"), width=100)

    # Enviar dados para o backend
    response = requests.post(BACKEND_URL, json={
        "google_id": user_info.get("id"),
        "nome": user_info.get("name"),
        "email": user_info.get("email")
    })
    
    #if response.status_code == 200:
     #   st.success("Usuário salvo com sucesso no banco de dados! ✅")

    #else:
    #    st.error("Erro ao salvar usuário no banco de dados! ❌")


else:
    col1,col2 = st.columns([10,26])
    with col2:
        st.markdown("# Login with Google")
        auth_url = get_google_auth_url()
    col_a,col_b = st.columns([10,14])
    with col_b:
        #st.button('Login', type='primary')
        #webbrowser.open('auth_url')
        st.markdown(f'<a href="{auth_url}" target="_self"><button>Login com Google</button></a>', unsafe_allow_html=True)


Assistants = st.Page(
    "front.py", title="Assistants", icon=":material/dashboard:", default=True
)

def initial_page():
    if Assistants:
        st.session_state.menu = True
        st.rerun()

    if st.button("Logout"):
        st.session_state.token = None
        st.rerun()

    else:
        st.session_state.menu = False

if st.session_state.token:

    st.markdown('# Playground Assistants')
    pg = st.navigation(
        {
            "Account": [logout_page],
            "Dashboard": [Assistants],
        }
    )
else:
    pg = st.navigation([login_page])

pg.run()