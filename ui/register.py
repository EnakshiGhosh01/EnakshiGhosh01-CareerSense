import streamlit as st

from auth.authentication import register_user
from auth.session import is_logged_in


def render_register():

    # ------------------------------------------------------
    # Already logged in
    # ------------------------------------------------------

    if is_logged_in():

        st.query_params.clear()
        st.query_params["page"] = "dashboard"
        st.rerun()

    # ------------------------------------------------------
    # CSS
    # ------------------------------------------------------

    st.markdown(
        """
        <style>

        .register-brand {
            text-align: center;

            font-size: 28px;

            font-weight: 700;

            color: #172033;

            margin-top: 20px;

            margin-bottom: 10px;
        }


        .register-brand span {
            color: #2563eb;
        }


        .register-title {
            text-align: center;

            font-size: 34px;

            font-weight: 700;

            color: #172033;

            margin-top: 20px;

            margin-bottom: 8px;
        }


        .register-subtitle {
            text-align: center;

            color: #6b7280;

            margin-bottom: 30px;
        }


        .register-card {
            max-width: 700px;

            margin: 35px auto;

            padding: 40px 55px;

            background: white;

            border-radius: 24px;

            box-shadow:
                0 15px 45px rgba(0, 0, 0, 0.08);
        }


        .register-footer {
            text-align: center;

            margin-top: 20px;

            color: #6b7280;

            font-size: 14px;
        }


        .or-divider {
            display: flex;

            align-items: center;

            gap: 15px;

            color: #94a3b8;

            font-size: 13px;

            margin: 20px 0;
        }


        .or-divider::before,
        .or-divider::after {
            content: "";

            flex: 1;

            height: 1px;

            background: #e2e8f0;
        }

        </style>
        """,
        unsafe_allow_html=True
    )

    # ------------------------------------------------------
    # Header
    # ------------------------------------------------------

    st.markdown(
        """
        <div class="register-brand">
            Career<span>Sense</span>
        </div>

        <div class="register-title">
            Create Your Account
        </div>

        <div class="register-subtitle">
            Join CareerSense and start your journey
        </div>
        """,
        unsafe_allow_html=True
    )

    # ------------------------------------------------------
    # Form
    # ------------------------------------------------------

    with st.form("register_form"):

        name = st.text_input(
            "Full Name",
            placeholder="Enter your full name"
        )

        email = st.text_input(
            "Email address",
            placeholder="Enter your email"
        )

        password = st.text_input(
            "Password",
            type="password",
            placeholder="Create a password"
        )

        confirm_password = st.text_input(
            "Confirm Password",
            type="password",
            placeholder="Confirm your password"
        )

        submitted = st.form_submit_button(
            "Register",
            use_container_width=True,
            type="primary"
        )

    # ------------------------------------------------------
    # Registration
    # ------------------------------------------------------

    if submitted:

        if not name or not email or not password:

            st.error(
                "Please fill in all required fields."
            )

        elif password != confirm_password:

            st.error(
                "Passwords do not match."
            )

        else:

            success, message = register_user(
                name,
                email,
                password
            )

            if success:

                st.success(message)

                st.info(
                    "Your account has been created. "
                    "Please login to continue."
                )

                st.query_params.clear()
                st.query_params["page"] = "login"

                st.rerun()

            else:

                st.error(message)

    # ------------------------------------------------------
    # Social Login
    # ------------------------------------------------------

    st.markdown(
        """
        <div class="or-divider">
            <span>OR</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.button(
        "Continue with Google",
        use_container_width=True
    ):

        st.info(
            "Google login is not configured yet."
        )

    if st.button(
        "Continue with GitHub",
        use_container_width=True
    ):

        st.info(
            "GitHub login is not configured yet."
        )

    # ------------------------------------------------------
    # Login link
    # ------------------------------------------------------

    st.markdown(
        """
        <div class="register-footer">
            Already have an account?
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.button(
        "Login here",
        use_container_width=True
    ):

        st.query_params.clear()
        st.query_params["page"] = "login"
        st.rerun()