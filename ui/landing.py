import streamlit as st
from pathlib import Path
import base64

def render_landing(logged_in=False):
    base_dir = Path(__file__).resolve().parent

    html_file = base_dir / "landing.html"
    image_file = base_dir / "landing-person.png"

    if not html_file.exists():
        st.error("landing.html was not found inside the ui folder.")
        return

    if not image_file.exists():
        st.error("landing-person.png was not found inside the ui folder.")
        return

    html = html_file.read_text(encoding="utf-8")

    image_base64 = base64.b64encode(image_file.read_bytes()).decode("utf-8")
    image_data = f"data:image/png;base64,{image_base64}"
    html = html.replace("{{LANDING_PERSON_IMAGE}}", image_data)

    if logged_in:
        get_started_link = "?page=dashboard"
        get_started_script = """window.parent.location.href = window.parent.location.pathname + "?page=dashboard";"""
        login_link = "?page=dashboard"
        login_script = """window.parent.location.href = window.parent.location.pathname + "?page=dashboard";"""
        register_link = "?page=dashboard"
        register_script = """window.parent.location.href = window.parent.location.pathname + "?page=dashboard";"""
    else:
        get_started_link = "#"
        get_started_script = """
            event.preventDefault();
            showToast("Please create an account first.", "Create an account to continue to CareerSense.");
        """
        login_link = "?page=login"
        login_script = """window.parent.location.href = window.parent.location.pathname + "?page=login";"""
        register_link = "?page=register"
        register_script = """window.parent.location.href = window.parent.location.pathname + "?page=register";"""

    html = html.replace("{{GET_STARTED_LINK}}", get_started_link)
    html = html.replace("{{GET_STARTED_SCRIPT}}", get_started_script)
    html = html.replace("{{LOGIN_LINK}}", login_link)
    html = html.replace("{{LOGIN_SCRIPT}}", login_script)
    html = html.replace("{{REGISTER_LINK}}", register_link)
    html = html.replace("{{REGISTER_SCRIPT}}", register_script)

    # Increased height to 1100 and scrolling=False to completely prevent inner scrollbars
    st.components.v1.html(html, height=1100, scrolling=False)