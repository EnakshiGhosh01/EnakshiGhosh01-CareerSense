import streamlit as st
from auth.authentication import verify_user

def render_login():
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    
    with col2:
        st.markdown("## 📊 CareerSense")
        st.markdown("### Welcome Back")
        st.caption("Login to continue to your career journey")
        
        with st.form("login_form"):
            email = st.text_input("Email address", placeholder="name@example.com")
            password = st.text_input("Password", type="password", placeholder="••••••••")
            remember = st.checkbox("Remember me")
            
            submitted = st.form_submit_button("Login", use_container_width=True)
            if submitted:
                if email and password:
                    success, name = verify_user(email, password)
                    if success:
                        st.session_state.logged_in = True
                        st.session_state.user_email = email
                        st.session_state.user_name = name
                        st.session_state.page = "app"
                        st.rerun()
                    else:
                        st.error("Invalid email or password.")
                else:
                    st.warning("Please fill in all fields.")
                    
        st.markdown("<p style='text-align: center; color: gray;'>OR</p>", unsafe_allow_html=True)
        if st.button("🔵 Continue with Google", use_container_width=True):
            st.info("Google OAuth placeholder.")
        if st.button("⚫ Continue with GitHub", use_container_width=True):
            st.info("GitHub OAuth placeholder.")
            
        st.markdown("---")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("← Back to Home"):
                st.session_state.page = "landing"
                st.rerun()
        with c2:
            if st.button("Register here"):
                st.session_state.page = "register"
                st.rerun()