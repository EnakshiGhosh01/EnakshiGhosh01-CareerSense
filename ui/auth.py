import streamlit as st

def render_login_ui():
    st.markdown("## 📊 CareerSense - Welcome Back")
    st.markdown("Login to continue to your career journey")
    
    with st.form("login_form"):
        email = st.text_input("Email address", placeholder="name@example.com")
        password = st.text_input("Password", type="password", placeholder="••••••••")
        
        col1, col2 = st.columns([1, 1])
        remember = col1.checkbox("Remember me")
        col2.markdown("[Forgot Password?](#)")
        
        submit = st.form_submit_button("Login", use_container_width=True)
        
    st.markdown("---")
    st.markdown("Don't have an account? [Register here](?page=register)")
    
    return email, password, submit

def render_register_ui():
    st.markdown("## 📊 CareerSense - Create Your Account")
    st.markdown("Join CareerSense and start your journey")
    
    with st.form("register_form"):
        name = st.text_input("Full Name", placeholder="Full Name")
        email = st.text_input("Email address", placeholder="name@example.com")
        password = st.text_input("Password", type="password", placeholder="••••••••")
        confirm_password = st.text_input("Confirm Password", type="password", placeholder="••••••••")
        
        submit = st.form_submit_button("Register", use_container_width=True)
        
    st.markdown("---")
    st.markdown("Already have an account? [Login here](?page=login)")
    
    return name, email, password, confirm_password, submit