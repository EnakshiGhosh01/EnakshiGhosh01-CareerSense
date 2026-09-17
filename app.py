import streamlit as st
import json
from pathlib import Path
import sys

current_dir = Path(__file__).resolve().parent
sys.path.append(str(current_dir))

st.set_page_config(
    page_title="CareerSense",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="collapsed"
)

USERS_FILE = current_dir / "users.json"

def load_users():
    if USERS_FILE.exists():
        try:
            with open(USERS_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    return ["test@example.com", "enakshi@example.com", "enakshi.ghosh@gmail.com"]

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "current_page" not in st.session_state:
    st.session_state.current_page = "landing"

if "registered_users" not in st.session_state:
    st.session_state.registered_users = load_users()

# Sync URL Query Parameters with Session State
if "page" in st.query_params:
    requested_page = st.query_params["page"]
    if requested_page in ["landing", "login", "register", "dashboard"]:
        if requested_page == "dashboard" and not st.session_state.logged_in:
            st.session_state.current_page = "login"
        else:
            st.session_state.current_page = requested_page

try:
    from ui.landing import render_landing
    from ui.auth import render_login_ui, render_register_ui
except Exception as e:
    st.error("🚨 Import Failed! Please check your `ui/` folder structure.")
    st.exception(e)
    st.stop()

def main():
    page = st.session_state.current_page

    if page == "landing":
        render_landing(logged_in=st.session_state.logged_in)
        
    elif page == "login":
        email, password, login_clicked = render_login_ui()
        
        if login_clicked:
            cleaned_email = email.strip().lower()
            registered_lower = [u.strip().lower() for u in st.session_state.registered_users]
            
            if cleaned_email in registered_lower:
                st.session_state.logged_in = True
                st.session_state.current_page = "landing"
                st.toast("Successfully logged in to CareerSense!", icon="🎉")
                st.query_params["page"] = "landing"
                st.rerun()
            else:
                st.error("⚠️ You are not registered yet! Please go register first.")

        col1, col2, col3 = st.columns([1, 1.4, 1])
        with col2:
            if st.button("⬅ Back to Landing Page", use_container_width=True):
                st.session_state.current_page = "landing"
                st.query_params["page"] = "landing"
                st.rerun()

    elif page == "register":
        name, email, password, confirm_password, register_clicked = render_register_ui()
        
        if register_clicked:
            cleaned_email = email.strip().lower()
            registered_lower = [u.strip().lower() for u in st.session_state.registered_users]
            
            if password != confirm_password:
                st.error("Passwords do not match!")
            elif cleaned_email in registered_lower:
                st.warning("Email already registered! Please log in.")
            else:
                st.session_state.registered_users.append(cleaned_email)
                save_users(st.session_state.registered_users)
                st.toast("Registered successfully! Please log in.", icon="✅")
                st.session_state.current_page = "login"
                st.query_params["page"] = "login"
                st.rerun()

        col1, col2, col3 = st.columns([1, 1.4, 1])
        with col2:
            if st.button("⬅ Back to Landing Page", use_container_width=True):
                st.session_state.current_page = "landing"
                st.query_params["page"] = "landing"
                st.rerun()

    elif page == "dashboard":
        if not st.session_state.logged_in:
            st.warning("Please log in to access the dashboard.")
            st.session_state.current_page = "login"
            st.query_params["page"] = "login"
            st.rerun()
            
        st.title("Welcome to your CareerSense Dashboard! 🚀")
        st.write("This is your command center for resume analysis and market tools.")
        
        if st.button("Log Out"):
            st.session_state.logged_in = False
            st.session_state.current_page = "landing"
            st.query_params.clear()
            st.rerun()

if __name__ == "__main__":
    main()