import streamlit as st

from auth.authentication import authenticate_user
from auth.session import (
    login_session,
    is_logged_in
)


def render_login():

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

        .login-container {
            max-width: 1050px;
            margin: 50px auto;
            min-height: 620px;

            display: flex;

            border-radius: 24px;

            overflow: hidden;

            background: white;

            box-shadow:
                0 15px 45px rgba(0, 0, 0, 0.10);
        }


        .login-left {
            width: 55%;
            padding: 55px 65px;
        }


        .login-right {
            width: 45%;

            display: flex;

            align-items: center;
            justify-content: center;

            text-align: center;

            padding: 50px;

            background:
                linear-gradient(
                    135deg,
                    #eef5ff,
                    #f7faff
                );
        }


        .brand {
            font-size: 27px;
            font-weight: 700;
            color: #172033;

            margin-bottom: 55px;
        }


        .brand span {
            color: #2563eb;
        }


        .login-title {
            font-size: 34px;
            font-weight: 700;

            color: #172033;

            margin-bottom: 8px;
        }


        .login-subtitle {
            color: #6b7280;

            font-size: 15px;

            margin-bottom: 35px;
        }


        .login-link {
            color: #2563eb;
            text-decoration: none;
            font-weight: 600;
        }


        .login-footer {
            margin-top: 25px;

            text-align: center;

            color: #6b7280;

            font-size: 14px;
        }


        .quote {
            max-width: 330px;
        }


        .quote h2 {
            font-size: 31px;

            color: #172033;

            line-height: 1.3;

            margin-bottom: 18px;
        }


        .quote p {
            color: #64748b;

            line-height: 1.7;

            font-size: 15px;
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
    # Layout
    # ------------------------------------------------------

    left, right = st.columns(
        [1.1, 0.9],
        gap="large"
    )

    # ======================================================
    # LEFT
    # ======================================================

    with left:

        st.markdown(
            """
            <div class="brand">
                Career<span>Sense</span>
            </div>

            <div class="login-title">
                Welcome Back
            </div>

            <div class="login-subtitle">
                Login to continue to your career journey
            </div>
            """,
            unsafe_allow_html=True
        )

        email = st.text_input(
            "Email address",
            placeholder="Enter your email",
            key="login_email"
        )

        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password",
            key="login_password"
        )

        remember = st.checkbox(
            "Remember me",
            key="remember_me"
        )

        col1, col2 = st.columns(2)

        with col1:

            if st.button(
                "Login",
                use_container_width=True,
                type="primary"
            ):

                if not email or not password:

                    st.error(
                        "Please enter your email and password."
                    )

                else:

                    user = authenticate_user(
                        email,
                        password
                    )

                    if user is None:

                        st.error(
                            "Invalid email or password."
                        )

                    else:

                        login_session(user)

                        st.success(
                            "Login successful!"
                        )

                        st.query_params.clear()
                        st.query_params["page"] = "dashboard"

                        st.rerun()

        with col2:

            if st.button(
                "Forgot Password?",
                use_container_width=True
            ):

                st.info(
                    "Password recovery will be added later."
                )

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

        st.markdown(
            """
            <div class="login-footer">
                Don't have an account?
            </div>
            """,
            unsafe_allow_html=True
        )

        if st.button(
            "Register here",
            use_container_width=True
        ):

            st.query_params.clear()
            st.query_params["page"] = "register"
            st.rerun()

    # ======================================================
    # RIGHT
    # ======================================================

    with right:

        st.markdown(
            """
            <div class="quote">

                <h2>
                    Better insights.<br>
                    Brighter opportunities.
                </h2>

                <p>
                    CareerSense helps you understand
                    your skills, discover relevant jobs,
                    and make smarter career decisions.
                </p>

            </div>
            """,
            unsafe_allow_html=True
        )