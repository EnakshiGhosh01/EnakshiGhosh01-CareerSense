import streamlit as st


# ==========================================================
# INITIALIZE SESSION
# ==========================================================

def initialize_session():

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if "user" not in st.session_state:
        st.session_state.user = None


# ==========================================================
# LOGIN SESSION
# ==========================================================

def login_session(user):

    st.session_state.logged_in = True

    st.session_state.user = user


# ==========================================================
# LOGOUT
# ==========================================================

def logout_session():

    st.session_state.logged_in = False

    st.session_state.user = None


# ==========================================================
# CHECK LOGIN
# ==========================================================

def is_logged_in():

    return st.session_state.get(
        "logged_in",
        False
    )


# ==========================================================
# CURRENT USER
# ==========================================================

def get_current_user():

    return st.session_state.get(
        "user"
    )


# ==========================================================
# CURRENT USER NAME
# ==========================================================

def get_current_user_name():

    user = get_current_user()

    if user is None:
        return ""

    return user.get(
        "name",
        ""
    )


# ==========================================================
# CURRENT USER EMAIL
# ==========================================================

def get_current_user_email():

    user = get_current_user()

    if user is None:
        return ""

    return user.get(
        "email",
        ""
    )


# ==========================================================
# INITIALIZE
# ==========================================================

initialize_session()