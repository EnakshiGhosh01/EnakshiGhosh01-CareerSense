import streamlit as st

def init_session_state():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "user_email" not in st.session_state:
        st.session_state.user_email = None
    if "user_name" not in st.session_state:
        st.session_state.user_name = None
    if "page" not in st.session_state:
        st.session_state.page = "landing"  # Options: landing, login, register, app

def is_logged_in():
    return st.session_state.get("logged_in", False)