import json
import sys
from pathlib import Path

import streamlit as st

from auth.session import (
    initialize_session,
    login_session,
    logout_session,
    is_logged_in,
)


# ==========================================================
# BASE DIRECTORY
# ==========================================================

current_dir = Path(__file__).resolve().parent

if str(current_dir) not in sys.path:
    sys.path.append(str(current_dir))


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
# DEFAULT PAGE
# ==========================================================

if "current_page" not in st.session_state:
    st.session_state.current_page = "landing"


# ==========================================================
# USERS FILE
# ==========================================================

USERS_FILE = current_dir / "users.json"


# ==========================================================
# LOAD USERS
# ==========================================================

def load_users():

    if USERS_FILE.exists():

        try:

            with open(
                USERS_FILE,
                "r",
                encoding="utf-8",
            ) as file:

                data = json.load(file)

            if isinstance(data, list):
                return data

        except Exception:
            pass

    return [
        "test@example.com",
        "enakshi@example.com",
        "enakshi.ghosh@gmail.com",
    ]


# ==========================================================
# SAVE USERS
# ==========================================================

def save_users(users):

    with open(
        USERS_FILE,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            users,
            file,
            indent=4,
        )


# ==========================================================
# LEGACY USERS.JSON SESSION DATA
# ==========================================================

if "registered_users" not in st.session_state:
    st.session_state.registered_users = load_users()

if "registered_user_names" not in st.session_state:
    st.session_state.registered_user_names = {}


# ==========================================================
# URL → SESSION STATE
# ==========================================================

requested_page = st.query_params.get(
    "page",
    None,
)

valid_pages = {
    "landing",
    "login",
    "register",
    "dashboard",
}

if requested_page in valid_pages:
    st.session_state.current_page = requested_page


# ==========================================================
# IMPORT UI MODULES
# ==========================================================

try:

    from ui.landing import render_landing

    from ui.auth import (
        render_login_ui,
        render_register_ui,
    )

    from ui.career_analysis import (
        render_career_analysis,
    )

except Exception as exc:

    st.error(
        "🚨 Import Failed! "
        "Please check your `ui/` folder structure."
    )

    st.exception(exc)
    st.stop()


# ==========================================================
# PAGE NAVIGATION
# ==========================================================

def go_to_page(page):

    if page not in valid_pages:
        page = "landing"

    st.session_state.current_page = page
    st.query_params["page"] = page
    st.rerun()


# ==========================================================
# MAIN
# ==========================================================

def main():

    page = st.session_state.get(
        "current_page",
        "landing",
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
            login_clicked,
        ) = render_login_ui()

        if login_clicked:

            cleaned_email = (
                str(email)
                .strip()
                .lower()
            )

            registered_lower = [
                str(user)
                .strip()
                .lower()
                for user in st.session_state.registered_users
            ]

            if cleaned_email in registered_lower:

                user_name = (
                    st.session_state
                    .get(
                        "registered_user_names",
                        {},
                    )
                    .get(
                        cleaned_email,
                        "",
                    )
                )

                if not user_name:

                    email_name = (
                        cleaned_email
                        .split("@")[0]
                    )

                    user_name = (
                        email_name
                        .replace(".", " ")
                        .replace("_", " ")
                        .title()
                    )

                login_session(
                    {
                        "name": user_name,
                        "email": cleaned_email,
                    }
                )

                # Keep the user details explicitly available
                # to the Career Analysis page.
                st.session_state.current_user = {
                    "name": user_name,
                    "email": cleaned_email,
                }

                # Login goes directly to Career Analysis.
                st.session_state.current_page = "dashboard"
                st.query_params["page"] = "dashboard"
                st.rerun()

            else:

                st.error(
                    "⚠️ You are not registered yet! "
                    "Please go register first."
                )

        col1, col2, col3 = st.columns(
            [1, 1.4, 1]
        )

        with col2:

            if st.button(
                "⬅ Back to Landing Page",
                use_container_width=True,
                key="login_back_landing",
            ):
                go_to_page("landing")

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
            register_clicked,
        ) = render_register_ui()

        if register_clicked:

            cleaned_email = (
                str(email)
                .strip()
                .lower()
            )

            cleaned_name = str(name).strip()

            registered_lower = [
                str(user)
                .strip()
                .lower()
                for user in st.session_state.registered_users
            ]

            if not cleaned_name:

                st.error(
                    "Please enter your full name."
                )

            elif not cleaned_email:

                st.error(
                    "Please enter your email address."
                )

            elif not password:

                st.error(
                    "Please enter a password."
                )

            elif password != confirm_password:

                st.error(
                    "Passwords do not match!"
                )

            elif cleaned_email in registered_lower:

                st.warning(
                    "Email already registered! "
                    "Please log in."
                )

            else:

                st.session_state.registered_users.append(
                    cleaned_email
                )

                save_users(
                    st.session_state.registered_users
                )

                st.session_state.registered_user_names[
                    cleaned_email
                ] = cleaned_name

                st.session_state.current_page = "login"
                st.query_params["page"] = "login"
                st.rerun()

        col1, col2, col3 = st.columns(
            [1, 1.4, 1]
        )

        with col2:

            if st.button(
                "⬅ Back to Landing Page",
                use_container_width=True,
                key="register_back_landing",
            ):
                go_to_page("landing")

        return

    # ======================================================
    # MY CAREER ANALYSIS
    # ======================================================

    if page == "dashboard":

        # Career Analysis is protected.
        if not is_logged_in():

            st.session_state.current_page = "login"
            st.query_params["page"] = "login"
            st.rerun()
            return

        # IMPORTANT:
        # Call the function. Do not use:
        #     if is_logged_in:
        # because that only tests whether the function exists.
        render_career_analysis()
        return

    # ======================================================
    # FALLBACK
    # ======================================================

    go_to_page("landing")


# ==========================================================
# RUN APPLICATION
# ==========================================================

if __name__ == "__main__":
    main()
