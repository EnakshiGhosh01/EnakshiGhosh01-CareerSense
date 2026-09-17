import streamlit as st
from auth.authentication import register_user
from auth.session import is_logged_in

def render_register():
    if is_logged_in():
        st.session_state.page = "app"
        st.rerun()
        
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    
    with col2:
        st.markdown("## 📊 CareerSense")
        st.markdown("### Create Your Account")
        st.caption("Join CareerSense and start your journey")
        
        with st.form("register_form"):
            fullname = st.text_input("Full Name", placeholder="Enakshi Ghosh")
            email = st.text_input("Email address", placeholder="name@example.com")
            password = st.text_input("Password", type="password", placeholder="••••••••")
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="••••••••")
            
            submitted = st.form_submit_button("Register", use_container_width=True)
            if submitted:
                if not fullname or not email or not password or not confirm_password:
                    st.warning("Please fill in all fields.")
                elif password != confirm_password:
                    st.error("Passwords do not match!")
                else:
                    success, msg = register_user(fullname, email, password)
                    if success:
                        st.success(msg + " Please proceed to login.")
                        st.session_state.page = "login"
                        st.rerun()
                    else:
                        st.error(msg)
                        
        st.markdown("<p style='text-align: center; color: gray;'>OR</p>", unsafe_allow_html=True)
        if st.button("🔵 Continue with Google", use_container_width=True, key="reg_google"):
            st.info("Google OAuth placeholder.")
        if st.button("⚫ Continue with GitHub", use_container_width=True, key="reg_github"):
            st.info("GitHub OAuth placeholder.")
            
        st.markdown("---")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("← Back to Home", key="reg_home"):
                st.session_state.page = "landing"
                st.rerun()
        with c2:
            if st.button("Login here", key="reg_login"):
                st.session_state.page = "login"
                st.rerun()