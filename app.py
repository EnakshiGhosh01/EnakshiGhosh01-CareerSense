import streamlit as st
from pathlib import Path
import sys


# ==========================================================
# BASE DIRECTORY
# ==========================================================

CURRENT_DIR = Path(__file__).resolve().parent

if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))


# ==========================================================
# AUTHENTICATION
# ==========================================================

from auth.authentication import (
    authenticate_user,
    register_user,
)

from auth.session import (
    initialize_session,
    login_session,
    logout_session,
    is_logged_in,
)


# ==========================================================
# UI MODULES
# ==========================================================

from ui.landing import render_landing

from ui.auth import (
    render_login_ui,
    render_register_ui,
)

from ui.career_analysis import (
    render_career_analysis,
)


# ==========================================================
# PAGE CONFIGURATION
# ==========================================================

st.set_page_config(
    page_title="CareerSense",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ==========================================================
# INITIALIZE SESSION
# ==========================================================

initialize_session()


# ==========================================================
# MAIN APPLICATION
# ==========================================================

def main():

    # ------------------------------------------------------
    # IMPORTANT:
    # URL query parameter is the single source of truth
    # ------------------------------------------------------

    page = st.query_params.get(
        "page",
        "landing"
    )


    # ======================================================
    # LANDING PAGE
    # ======================================================

    if page == "landing":

        render_landing(
            logged_in=is_logged_in()
        )

        return


    # ======================================================
    # LOGIN PAGE
    # ======================================================

    if page == "login":

        (
            email,
            password,
            login_clicked
        ) = render_login_ui()


        # --------------------------------------------------
        # LOGIN BUTTON
        # --------------------------------------------------

        if login_clicked:

            cleaned_email = email.strip().lower()


            # ----------------------------------------------
            # EMAIL VALIDATION
            # ----------------------------------------------

            if not cleaned_email:

                st.error(
                    "Please enter your email address."
                )

                return


            # ----------------------------------------------
            # PASSWORD VALIDATION
            # ----------------------------------------------

            if not password:

                st.error(
                    "Please enter your password."
                )

                return


            # ----------------------------------------------
            # AUTHENTICATE USING SQLITE
            # ----------------------------------------------

            user = authenticate_user(
                cleaned_email,
                password
            )


            # ----------------------------------------------
            # INVALID LOGIN
            # ----------------------------------------------

            if user is None:

                st.error(
                    "Invalid email or password."
                )

                return


            # ----------------------------------------------
            # CREATE LOGIN SESSION
            # ----------------------------------------------

            login_session(user)


            # ----------------------------------------------
            # GO TO CAREER ANALYSIS
            # ----------------------------------------------

            st.query_params.clear()

            st.query_params["page"] = "dashboard"

            st.rerun()

            return


        return


    # ======================================================
    # REGISTER PAGE
    # ======================================================

    if page == "register":

        (
            name,
            email,
            password,
            confirm_password,
            register_clicked
        ) = render_register_ui()


        # --------------------------------------------------
        # REGISTER BUTTON
        # --------------------------------------------------

        if register_clicked:

            cleaned_name = name.strip()

            cleaned_email = email.strip().lower()


            # ----------------------------------------------
            # NAME VALIDATION
            # ----------------------------------------------

            if not cleaned_name:

                st.error(
                    "Please enter your full name."
                )

                return


            # ----------------------------------------------
            # EMAIL VALIDATION
            # ----------------------------------------------

            if not cleaned_email:

                st.error(
                    "Please enter your email address."
                )

                return


            # ----------------------------------------------
            # PASSWORD VALIDATION
            # ----------------------------------------------

            if not password:

                st.error(
                    "Please enter a password."
                )

                return


            # ----------------------------------------------
            # CONFIRM PASSWORD
            # ----------------------------------------------

            if not confirm_password:

                st.error(
                    "Please confirm your password."
                )

                return


            # ----------------------------------------------
            # PASSWORD MATCH
            # ----------------------------------------------

            if password != confirm_password:

                st.error(
                    "Passwords do not match."
                )

                return


            # ----------------------------------------------
            # REGISTER USER IN SQLITE
            # ----------------------------------------------

            success, message = register_user(
                cleaned_name,
                cleaned_email,
                password
            )


            # ----------------------------------------------
            # REGISTRATION FAILED
            # ----------------------------------------------

            if not success:

                st.error(message)

                return


            # ----------------------------------------------
            # REGISTRATION SUCCESS
            # ----------------------------------------------

            st.success(message)


            # ----------------------------------------------
            # GO TO LOGIN PAGE
            # ----------------------------------------------

            st.query_params.clear()

            st.query_params["page"] = "login"

            st.rerun()

            return


        return


    # ======================================================
    # MY CAREER ANALYSIS / DASHBOARD
    # ======================================================

    if page == "dashboard":

        # --------------------------------------------------
        # USER MUST BE LOGGED IN
        # --------------------------------------------------

        if not is_logged_in():

            st.query_params.clear()

            st.query_params["page"] = "login"

            st.rerun()

            return


        # --------------------------------------------------
        # RENDER CAREER ANALYSIS
        # --------------------------------------------------

        render_career_analysis()

        return


    # ======================================================
    # LOGOUT
    # ======================================================

    if page == "logout":

        logout_session()

        st.query_params.clear()

        st.query_params["page"] = "landing"

        st.rerun()

        return


    # ======================================================
    # UNKNOWN PAGE
    # ======================================================

    st.query_params.clear()

    st.query_params["page"] = "landing"

    st.rerun()


# ==========================================================
# RUN APPLICATION
# ==========================================================

if __name__ == "__main__":

    main()