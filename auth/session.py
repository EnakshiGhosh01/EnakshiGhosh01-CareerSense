import streamlit as st

def initialize_session():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if "user" not in st.session_state:
        st.session_state.user = None

def login_session(user):
    st.session_state.logged_in = True
    st.session_state.user = user

def logout_session():
    st.session_state.logged_in = False
    st.session_state.user = None

def is_logged_in():
    return st.session_state.logged_in

def get_current_user():
    return st.session_state.user

def get_current_user_name():
    user = get_current_user()
    return user["name"] if user else "Guest"

def get_current_user_email():
    user = get_current_user()
    return user["email"] if user else "Not available"