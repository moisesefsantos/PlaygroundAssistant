import streamlit as st

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

user_email = ['sofia', 'heloiza']
user_password = ['senha', '123']

def login():
    if st.button("Log in"):
        if email in user_email and password in user_password:
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Login failed")

def logout():
    if st.button("Log out",type="primary"):
        st.session_state.logged_in = False
        st.rerun()

login_page = st.Page(login, title="Log in", icon=":material/login:")
logout_page = st.Page(logout, title="Log out", icon=":material/logout:")

if st.session_state.logged_in == False:
    st.markdown("#### Enter your credentials")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

Assistants = st.Page(
    "front.py", title="Assistants", icon=":material/dashboard:", default=True
)

def initial_page():
    if Assistants:
        st.session_state.menu = True
        st.rerun()

    else:
        st.session_state.menu = False
#bugs = st.Page("reports/bugs.py", title="Bug reports", icon=":material/bug_report:")
#alerts = st.Page(
#    "reports/alerts.py", title="System alerts", icon=":material/notification_important:"
#)

#search = st.Page("tools/search.py", title="Search", icon=":material/search:")
#history = st.Page("tools/history.py", title="History", icon=":material/history:")

if st.session_state.logged_in:
    pg = st.navigation(
        {
            "Account": [logout_page],
            "Dashboard": [Assistants],
            #"Tools": [search, history],
        }
    )
else:
    pg = st.navigation([login_page])

pg.run()