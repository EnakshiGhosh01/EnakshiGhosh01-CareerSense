import streamlit as st
from pathlib import Path
import base64


def render_landing(logged_in=False):

    base_dir = Path(__file__).resolve().parent

    html_file = base_dir / "landing.html"
    image_file = base_dir / "landing-person.png"


    if not html_file.exists():

        st.error(
            "landing.html was not found inside the ui folder."
        )

        return


    if not image_file.exists():

        st.error(
            "landing-person.png was not found inside the ui folder."
        )

        return


    # ------------------------------------------------------
    # Read HTML
    # ------------------------------------------------------

    html = html_file.read_text(
        encoding="utf-8"
    )


    # ------------------------------------------------------
    # Convert image to Base64
    # ------------------------------------------------------

    image_base64 = base64.b64encode(
        image_file.read_bytes()
    ).decode("utf-8")


    image_data = (
        f"data:image/png;base64,{image_base64}"
    )


    # ------------------------------------------------------
    # Insert image
    # ------------------------------------------------------

    html = html.replace(
        "{{LANDING_PERSON_IMAGE}}",
        image_data
    )


    # ------------------------------------------------------
    # Get Started behaviour
    # ------------------------------------------------------

    if logged_in:

        html = html.replace(
            "{{GET_STARTED_LINK}}",
            "?page=dashboard"
        )

    else:

        html = html.replace(
            "{{GET_STARTED_LINK}}",
            "#"
        )


    # ------------------------------------------------------
    # Logged-in JavaScript
    # ------------------------------------------------------

    if logged_in:

        html = html.replace(
            "{{GET_STARTED_SCRIPT}}",
            """
            window.parent.location.href =
                window.parent.location.pathname +
                "?page=dashboard";
            """
        )

    else:

        html = html.replace(
            "{{GET_STARTED_SCRIPT}}",
            """
            event.preventDefault();

            showToast(
                "Please create an account first.",
                "Create an account to continue to CareerSense."
            );
            """
        )


    # ------------------------------------------------------
    # Render
    # ------------------------------------------------------

    st.components.v1.html(
        html,
        height=1200,
        scrolling=True
    )