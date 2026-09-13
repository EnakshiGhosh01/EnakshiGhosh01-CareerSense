import streamlit as st

from resume.parser import extract_resume_text
from resume.analyzer import analyze_resume


# ==========================================================
# PAGE CONFIGURATION
# ==========================================================

st.set_page_config(
    page_title="CareerSense",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ==========================================================
# CUSTOM STYLING
# ==========================================================

st.markdown(
    """
    <style>

    /* Main content */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1400px;
    }

    /* Header */
    .main-title {
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }

    .subtitle {
        font-size: 1.1rem;
        opacity: 0.75;
        margin-bottom: 2rem;
    }

    /* Section headings */
    .section-title {
        font-size: 1.5rem;
        font-weight: 650;
        margin-top: 1rem;
        margin-bottom: 1rem;
    }

    /* Skill card */
    .skill-card {
        padding: 0.65rem 0.9rem;
        border-radius: 8px;
        border: 1px solid rgba(128, 128, 128, 0.25);
        margin-bottom: 0.6rem;
        text-align: center;
        font-size: 0.95rem;
    }

    /* Category card */
    .category-card {
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid rgba(128, 128, 128, 0.25);
        margin-bottom: 1rem;
    }

    /* Score */
    .score-number {
        font-size: 3rem;
        font-weight: 700;
        text-align: center;
    }

    .score-label {
        text-align: center;
        opacity: 0.7;
        font-size: 0.9rem;
    }

    /* Info cards */
    .info-card {
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid rgba(128, 128, 128, 0.25);
        min-height: 120px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ==========================================================
# HELPER FUNCTIONS
# ==========================================================

def display_skill_cards(skills):
    """Display detected skills in a grid."""

    if not skills:
        st.info("No recognized skills were detected.")
        return

    columns = st.columns(4)

    for index, skill in enumerate(skills):

        with columns[index % 4]:

            st.markdown(
                f"""
                <div class="skill-card">
                    {skill.title()}
                </div>
                """,
                unsafe_allow_html=True
            )


def display_score_breakdown(score):
    """Display resume score components."""

    col1, col2 = st.columns(2)

    with col1:

        st.write(
            f"**Skills — {score['skill_score']}/40**"
        )

        st.progress(
            score["skill_score"] / 40
        )

        st.write(
            f"**Education — {score['education_score']}/20**"
        )

        st.progress(
            score["education_score"] / 20
        )

        st.write(
            f"**Projects — {score['project_score']}/15**"
        )

        st.progress(
            score["project_score"] / 15
        )

    with col2:

        st.write(
            f"**Certifications — "
            f"{score['certification_score']}/10**"
        )

        st.progress(
            score["certification_score"] / 10
        )

        st.write(
            f"**Completeness — "
            f"{score['completeness_score']}/15**"
        )

        st.progress(
            score["completeness_score"] / 15
        )


def get_score_message(score):
    """Return a simple interpretation of the resume score."""

    if score >= 85:
        return (
            "Excellent resume profile. Your resume contains "
            "strong skills and good supporting information."
        )

    elif score >= 70:
        return (
            "Good resume profile. A few improvements could "
            "make your resume stronger."
        )

    elif score >= 50:
        return (
            "Moderate resume profile. Consider improving "
            "your skills, projects, certifications, or "
            "resume completeness."
        )

    else:
        return (
            "Your resume needs improvement. Add relevant "
            "skills, projects, education details, and "
            "supporting information."
        )


# ==========================================================
# HEADER
# ==========================================================

st.markdown(
    '<div class="main-title">💼 CareerSense</div>',
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="subtitle">
        AI-Powered Career Intelligence and Job Matching System
    </div>
    """,
    unsafe_allow_html=True
)

st.divider()


# ==========================================================
# MAIN NAVIGATION
# ==========================================================

tab1, tab2 = st.tabs(
    [
        "📊 My Career Analysis",
        "💼 Job Market Insights"
    ]
)


# ==========================================================
# TAB 1 — MY CAREER ANALYSIS
# ==========================================================

with tab1:

    st.header("My Career Analysis")

    st.write(
        "Upload your resume to understand your skills, "
        "experience, education, and resume strength."
    )

    # ------------------------------------------------------
    # Resume Upload
    # ------------------------------------------------------

    uploaded_resume = st.file_uploader(
        "Upload your resume",
        type=["pdf", "docx"],
        help="Supported formats: PDF and DOCX"
    )

    # ======================================================
    # NO RESUME UPLOADED
    # ======================================================

    if uploaded_resume is None:

        st.info(
            "Upload a PDF or DOCX resume to start your analysis."
        )

        st.markdown(
            '<div class="section-title">What CareerSense analyzes</div>',
            unsafe_allow_html=True
        )

        col1, col2, col3, col4 = st.columns(4)

        with col1:

            st.markdown(
                """
                <div class="info-card">
                    <h4>🛠️ Skills</h4>
                    <p>
                    Detect technical and professional
                    skills from your resume.
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col2:

            st.markdown(
                """
                <div class="info-card">
                    <h4>💼 Experience</h4>
                    <p>
                    Extract your professional experience
                    for job matching.
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col3:

            st.markdown(
                """
                <div class="info-card">
                    <h4>🎓 Education</h4>
                    <p>
                    Identify your educational
                    qualifications.
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col4:

            st.markdown(
                """
                <div class="info-card">
                    <h4>📈 Resume Score</h4>
                    <p>
                    Evaluate your resume using
                    explainable scoring criteria.
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )


    # ======================================================
    # RESUME UPLOADED
    # ======================================================

    else:

        st.success(
            f"Resume uploaded: {uploaded_resume.name}"
        )

        try:

            # --------------------------------------------------
            # STEP 1 — PARSE RESUME
            # --------------------------------------------------

            resume_text = extract_resume_text(
                uploaded_resume
            )

            if not resume_text.strip():

                st.error(
                    "No readable text could be extracted from "
                    "this resume. Please upload a text-based "
                    "PDF or DOCX file."
                )

            else:

                # --------------------------------------------------
                # STEP 2 — ANALYZE RESUME
                # --------------------------------------------------

                result = analyze_resume(
                    resume_text
                )

                score = result["score"]

                # ==================================================
                # PROFILE OVERVIEW
                # ==================================================

                st.markdown(
                    '<div class="section-title">'
                    '📋 Profile Overview'
                    '</div>',
                    unsafe_allow_html=True
                )

                col1, col2, col3 = st.columns(3)

                with col1:

                    st.metric(
                        "Resume Score",
                        f"{score['total_score']}/100"
                    )

                with col2:

                    st.metric(
                        "Experience",
                        f"{result['experience']} years"
                    )

                with col3:

                    st.metric(
                        "Skills Detected",
                        len(result["skills"])
                    )

                st.caption(
                    "Experience is extracted separately and "
                    "is not included in the Resume Score."
                )

                # ==================================================
                # RESUME SCORE
                # ==================================================

                st.markdown(
                    '<div class="section-title">'
                    '📈 Resume Score'
                    '</div>',
                    unsafe_allow_html=True
                )

                score_col1, score_col2 = st.columns(
                    [1, 2]
                )

                with score_col1:

                    st.markdown(
                        f"""
                        <div class="score-number">
                            {score['total_score']}
                        </div>

                        <div class="score-label">
                            out of 100
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                with score_col2:

                    st.write(
                        get_score_message(
                            score["total_score"]
                        )
                    )

                    st.progress(
                        score["total_score"] / 100
                    )

                # ==================================================
                # SCORE BREAKDOWN
                # ==================================================

                st.subheader(
                    "Score Breakdown"
                )

                display_score_breakdown(
                    score
                )

                st.divider()

                # ==================================================
                # DETECTED SKILLS
                # ==================================================

                st.subheader(
                    "🛠️ Detected Skills"
                )

                display_skill_cards(
                    result["skills"]
                )

                st.divider()

                # ==================================================
                # SKILLS BY CATEGORY
                # ==================================================

                st.subheader(
                    "📂 Skills by Category"
                )

                if result["skills_by_category"]:

                    for category, skills in result[
                        "skills_by_category"
                    ].items():

                        with st.expander(
                            f"{category.replace('_', ' ').title()} "
                            f"({len(skills)})"
                        ):

                            st.write(
                                ", ".join(
                                    skill.title()
                                    for skill in skills
                                )
                            )

                else:

                    st.info(
                        "No skill categories were detected."
                    )

                # ==================================================
                # EDUCATION
                # ==================================================

                st.subheader(
                    "🎓 Education"
                )

                if result["education"]:

                    education_columns = st.columns(
                        min(len(result["education"]), 3)
                    )

                    for index, education in enumerate(
                        result["education"]
                    ):

                        with education_columns[
                            index % len(education_columns)
                        ]:

                            st.info(
                                education
                                .replace("_", " ")
                                .title()
                            )

                else:

                    st.info(
                        "No recognized education qualification "
                        "was detected."
                    )

                # ==================================================
                # EXPERIENCE
                # ==================================================

                st.subheader(
                    "💼 Experience"
                )

                st.metric(
                    "Detected Experience",
                    f"{result['experience']} years"
                )

                st.caption(
                    "Internships and professional experience "
                    "will be handled separately as the resume "
                    "pipeline becomes more detailed."
                )

                # ==================================================
                # EXTRACTED RESUME TEXT
                # ==================================================

                with st.expander(
                    "📄 View Extracted Resume Text"
                ):

                    st.text_area(
                        "Extracted text",
                        resume_text,
                        height=350,
                        label_visibility="collapsed"
                    )

        # ==================================================
        # ERROR HANDLING
        # ==================================================

        except ValueError as error:

            st.error(
                str(error)
            )

        except Exception as error:

            st.error(
                "An unexpected error occurred while "
                "analyzing the resume."
            )

            st.exception(error)


# ==========================================================
# TAB 2 — JOB MARKET INSIGHTS
# ==========================================================

with tab2:

    st.header("Job Market Insights")

    st.write(
        "Explore job-market trends, salary information, "
        "skill demand, locations, and industries."
    )

    # ------------------------------------------------------
    # Placeholder metrics
    # ------------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Total Jobs",
            "—"
        )

    with col2:

        st.metric(
            "Average Salary",
            "—"
        )

    with col3:

        st.metric(
            "Top Location",
            "—"
        )

    with col4:

        st.metric(
            "Top Skill",
            "—"
        )

    st.divider()

    st.info(
        "Job-market analytics will be connected to the "
        "processed job dataset in the next stage."
    )

    st.markdown(
        """
        ### Planned Job Market Features

        - 📊 Job demand by skill
        - 📍 Job distribution by location
        - 💰 Salary trends and ranges
        - 🏢 Top hiring companies
        - 💼 Most common job roles
        - 📈 Experience-level analysis
        """
    )