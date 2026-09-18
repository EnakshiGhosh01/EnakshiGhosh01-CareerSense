import re
import textwrap
from pathlib import Path

import pandas as pd
import streamlit as st

from resume.parser import extract_resume_text
from resume.analyzer import analyze_resume
from matching.job_matcher import load_jobs, rank_jobs

from auth.session import (
    get_current_user_name,
    get_current_user_email,
    logout_session,
)


# ==========================================================
# PATH
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATASET_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "jobs_cleaned.csv"
)


# ==========================================================
# HTML HELPER
# ==========================================================

def render_html(html, unsafe_allow_html=True):
    html = textwrap.dedent(html).strip()
    st.markdown(html, unsafe_allow_html=unsafe_allow_html)


# ==========================================================
# GLOBAL STYLES
# ==========================================================

def inject_styles():
    render_html(
        """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}

        .stApp {
            background: #f5f8fc;
        }

        .block-container {
            padding-top: 0.7rem;
            padding-bottom: 2rem;
            max-width: 1500px;
        }

        /* ==================================================
           CUSTOM SIDEBAR CONTAINER STYLING
        ================================================== */
        .cs-sidebar {
            background: #102b45;
            color: white;
            border-radius: 14px;
            min-height: calc(100vh - 1.4rem);
            padding: 20px 14px 18px 14px;
            box-sizing: border-box;
            width: 100%;
            display: flex;
            flex-direction: column;
        }

        .cs-brand {
            color: white;
            font-size: 1.1rem;
            font-weight: 800;
            padding: 2px 4px 14px 4px;
            letter-spacing: -0.2px;
        }

        .cs-user {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 10px 4px 14px 4px;
            border-bottom: 1px solid rgba(255,255,255,0.12);
            margin-bottom: 12px;
        }

        .cs-avatar {
            width: 36px;
            height: 36px;
            min-width: 36px;
            border-radius: 50%;
            background: #2f80ed;
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 800;
            font-size: 0.78rem;
        }

        .cs-hello {
            color: #b9c8d8;
            font-size: 0.6rem;
            line-height: 1.2;
        }

        .cs-user-name {
            color: white;
            font-size: 0.74rem;
            font-weight: 750;
            line-height: 1.25;
            margin-top: 2px;
        }

        .cs-user-email {
            color: #9fb4ca;
            font-size: 0.54rem;
            line-height: 1.25;
            margin-top: 2px;
            word-break: break-word;
        }

        .cs-nav-label {
            color: #7891aa;
            font-size: 0.56rem;
            text-transform: uppercase;
            letter-spacing: 0.8px;
            padding: 4px 4px 6px 4px;
        }

        /* ==================================================
           STREAMLIT RADIO NAVIGATION OVERRIDES
        ================================================== */
        div[data-testid="stRadio"] > label {
            display: none !important;
        }

        div[data-testid="stRadio"] div[role="radiogroup"] {
            gap: 3px;
        }

        div[data-testid="stRadio"] div[role="radiogroup"] label {
            background: transparent;
            border-radius: 8px;
            padding: 7px 10px;
            margin: 2px 0;
            color: #dbeafe;
            font-size: 0.71rem;
            font-weight: 500;
            width: 100%;
            border: none;
            box-sizing: border-box;
            transition: background 0.2s ease;
        }

        div[data-testid="stRadio"] div[role="radiogroup"] label:hover {
            background: #194670;
            color: white;
        }

        div[data-testid="stRadio"] div[role="radiogroup"] label[data-baseweb="radio"] input:checked + div {
            background: #1d5fa0;
        }

        div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) {
            background: #1d5fa0;
            color: white;
            font-weight: 700;
        }

        div[data-testid="stRadio"] div[role="radiogroup"] input[type="radio"] {
            display: none;
        }

        /* Sidebar action buttons */
        .sidebar-logout-holder .stButton > button {
            background: transparent;
            border: 1px solid rgba(255, 255, 255, 0.15);
            color: #dbeafe;
            text-align: left;
            border-radius: 8px;
            min-height: 34px;
            font-size: 0.7rem;
            padding: 4px 8px;
            box-shadow: none;
            width: 100%;
            margin-top: 10px;
        }
        .sidebar-logout-holder .stButton > button:hover {
            background: #7f1d1d;
            border-color: #7f1d1d;
            color: white;
        }

        /* ==================================================
           PAGE HERO & CARDS
        ================================================== */
        .page-hero {
            background: linear-gradient(110deg, #eef5ff 0%, #e4efff 60%, #d9eaff 100%);
            border: 1px solid #d5e3f5;
            border-radius: 12px;
            padding: 1.2rem 1.5rem;
            margin-bottom: 0.8rem;
        }

        .card {
            background: white;
            border: 1px solid #e1e8f1;
            border-radius: 10px;
            padding: 0.9rem 1rem;
            box-shadow: 0 2px 8px rgba(15, 23, 42, 0.035);
            height: 100%;
            box-sizing: border-box;
        }

        .card-title {
            color: #10244b;
            font-size: 0.86rem;
            font-weight: 750;
            margin-bottom: 0.5rem;
        }

        .skill-chip {
            display: inline-block;
            background: #eaf9f1;
            color: #198754;
            border-radius: 7px;
            padding: 5px 8px;
            margin: 3px 3px 3px 0;
            font-size: 0.67rem;
            font-weight: 650;
            border: 1px solid #d1f2e1;
        }

        .skill-chip.blue {
            background: #eaf2ff;
            color: #2d67b1;
            border: 1px solid #d0e3fc;
        }

        .job-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.66rem;
        }
        .job-table th {
            color: #71839b;
            font-weight: 650;
            text-align: left;
            padding: 6px 5px;
            border-bottom: 1px solid #e8edf4;
        }
        .job-table td {
            color: #213957;
            padding: 7px 5px;
            border-bottom: 1px solid #edf1f5;
            vertical-align: middle;
        }
        .match-pill {
            display: inline-block;
            background: #dff6ea;
            color: #16814e;
            padding: 3px 7px;
            border-radius: 5px;
            font-weight: 750;
        }

        .empty-state {
            background: #f8fbff;
            border: 1px dashed #b7cce6;
            border-radius: 9px;
            padding: 1.2rem;
            text-align: center;
            color: #60748f;
            font-size: 0.72rem;
            margin-top: 0.6rem;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


# ==========================================================
# HELPERS
# ==========================================================

def safe_text(value, fallback="Not available"):
    if value is None:
        return fallback
    text = str(value).strip()
    if not text or text.lower() in {"nan", "none", "null"}:
        return fallback
    return text


def get_initials(name):
    name = safe_text(name, "User")
    parts = name.split()
    if len(parts) == 1:
        return parts[0][0].upper()
    return (parts[0][0] + parts[1][0]).upper()


def get_score_message(score):
    if score >= 85:
        return "Good job! Your resume is strong, but there is still room for improvement."
    if score >= 70:
        return "Your resume has a solid foundation. A few improvements could make it stronger."
    if score >= 50:
        return "Your resume has a moderate profile. Consider improving skills and supporting details."
    return "Your resume needs improvement. Add relevant skills, projects, education and supporting information."


def extract_resume_location(text):
    cities = [
        "Bengaluru", "Bangalore", "Hyderabad", "Pune", "Chennai", "Gurugram",
        "Gurgaon", "Mumbai", "Noida", "Delhi", "Kolkata", "Kochi", "Jaipur",
        "Ahmedabad", "Indore", "Lucknow", "Chandigarh", "Bhubaneswar", "Patna",
        "Visakhapatnam", "Nagpur", "Coimbatore", "Mysuru", "Mysore", "New Delhi"
    ]
    text = str(text).lower()
    for city in cities:
        if re.search(r"\b" + re.escape(city.lower()) + r"\b", text):
            return city
    return "Not detected"


# ==========================================================
# SIDEBAR
# ==========================================================

def render_sidebar(user_name, user_email):
    initials = get_initials(user_name)

    # Open the sidebar container wrapper div
    render_html(
        f"""
        <div class="cs-sidebar">
            <div>
                <div class="cs-brand">
                    📊 CareerSense
                </div>
                <div class="cs-user">
                    <div class="cs-avatar">
                        {initials}
                    </div>
                    <div style="min-width:0;">
                        <div class="cs-hello">Hello,</div>
                        <div class="cs-user-name">{safe_text(user_name, "User")}</div>
                        <div class="cs-user-email">{safe_text(user_email)}</div>
                    </div>
                </div>
                <div class="cs-nav-label">
                    Workspace
                </div>
            </div>
        """
    )

    # Interactive Navigation Tabs inside the sidebar column
    nav_tabs = [
        "🏠 My Career Analysis",
        "📊 Job Market Insights",
        "📚 Recommended Learning",
        "🔖 Saved Jobs",
        "👤 Profile",
        "⚙️ Settings"
    ]
    
    selected_tab = st.radio(
        "Workspace Navigation",
        options=nav_tabs,
        index=0,
        key="sidebar_navigation_tab",
        label_visibility="collapsed"
    )

    # Render footer and close container wrapper div properly
    render_html(
        """
            <div style="margin-top: auto; padding-top: 15px;">
                <div style="padding-top: 10px; border-top: 1px solid rgba(255,255,255,0.12);">
                    <div style="color: white; font-size: 0.74rem; font-weight: 750;">📊 CareerSense</div>
                    <div style="color: #9fb4ca; font-size: 0.54rem; margin-top: 2px;">Your Career. Smarter.</div>
                </div>
            </div>
        </div>
        """
    )

    st.markdown('<div class="sidebar-logout-holder">', unsafe_allow_html=True)
    if st.button("↪ Logout", use_container_width=True, key="career_logout"):
        logout_session()
        st.session_state.current_page = "landing"
        st.query_params.clear()
        st.query_params["page"] = "landing"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    return selected_tab


# ==========================================================
# PAGE HEADER
# ==========================================================

def render_header(user_name):
    render_html(
        f"""
        <div class="page-hero">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <div style="color: #0b1f45; font-size: 1.65rem; font-weight: 800;">My Career Analysis</div>
                    <div style="color: #49617f; font-size: 0.75rem; margin-top: 0.3rem;">
                        Upload your resume and get personalized insights, job recommendations and skill gap analysis.
                    </div>
                </div>
                <div style="color: #49617f; font-size: 0.72rem; text-align: right;">
                    Hello, <b>{safe_text(user_name, "User")}</b><br>
                    Your skills today,<br>
                    <b>new opportunities tomorrow.</b>
                </div>
            </div>
        </div>
        """
    )


# ==========================================================
# COMPONENTS
# ==========================================================

def render_resume_score(score):
    total = max(0, min(int(round(float(score.get("total_score", 0)))), 100))
    degrees = total * 3.6
    render_html(
        f"""
        <div class="card">
            <div class="card-title">Resume Score</div>
            <div style="display: flex; align-items: center; gap: 14px; margin-top: 10px;">
                <div style="width: 90px; height: 90px; border-radius: 50%; background: conic-gradient(#18b779 0deg {degrees}deg, #e5edf4 {degrees}deg 360deg); display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
                    <div style="width: 68px; height: 68px; border-radius: 50%; background: white; display: flex; flex-direction: column; align-items: center; justify-content: center;">
                        <div style="color: #10244b; font-size: 1.35rem; font-weight: 800; line-height: 1;">{total}</div>
                        <div style="color: #7b8da6; font-size: 0.6rem; margin-top: 3px;">/100</div>
                    </div>
                </div>
                <div style="color: #465d7a; font-size: 0.68rem; line-height: 1.45;">
                    {get_score_message(total)}
                </div>
            </div>
        </div>
        """
    )


def render_skills(skills):
    skills = list(skills or [])
    chips = "".join(
        f'<span class="skill-chip {"blue" if i % 4 == 3 else ""}">{safe_text(s).title()}</span>'
        for i, s in enumerate(skills[:14])
    ) or '<span style="color:#71839b;font-size:.7rem;">No skills detected yet.</span>'

    render_html(
        f"""
        <div class="card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                <div class="card-title" style="margin-bottom:0;">Key Skills Detected</div>
            </div>
            <div style="margin-top: 4px;">{chips}</div>
        </div>
        """
    )


def render_detected_information(user_name, user_email, experience, education, location):
    exp_display = f"{float(experience):g} years" if isinstance(experience, (int, float)) else safe_text(experience)
    rows = [
        ("Name", safe_text(user_name, "User")),
        ("Email", safe_text(user_email)),
        ("Experience", exp_display),
        ("Education", safe_text(education, "Not detected")),
        ("Location", safe_text(location, "Not detected")),
    ]
    body = "".join(
        f'<div style="display: grid; grid-template-columns: 90px 1fr; gap: 8px; padding: 4px 0; font-size: 0.68rem;">'
        f'<div style="color: #7b8da6;">{lbl}</div><div style="color: #1e3556; font-weight: 600;">{val}</div></div>'
        for lbl, val in rows
    )
    render_html(
        f"""
        <div class="card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                <div class="card-title" style="margin-bottom:0;">Detected Information</div>
            </div>
            <div style="margin-top: 4px;">{body}</div>
        </div>
        """
    )


def render_skill_gap(resume_skills, jobs):
    render_html(
        """
        <div class="card">
            <div class="card-title">Skill Gap Analysis <span style="font-weight: normal; font-size: 0.72rem; color: #64748b;">(for Data Analyst)</span></div>
            <div style="display: flex; gap: 12px; font-size: 0.6rem; color: #64748b; margin-bottom: 6px;">
                <span>● Your Skills</span><span>■ Required in Job Market</span>
            </div>
        """
    )

    if jobs is None or jobs.empty:
        render_html('<div class="empty-state" style="margin-top:0;">Upload a resume to see skill gaps.</div></div>')
        return

    required = {}
    for _, job in jobs.iterrows():
        missing = job.get("missing_skills", [])
        missing_skills = missing if isinstance(missing, (list, tuple, set)) else [s.strip() for s in safe_text(missing, "").split(",") if s.strip()]
        for skill in missing_skills:
            if skill:
                required[skill] = required.get(skill, 0) + 1

    if not required:
        render_html('<div style="color:#198754;font-size:.7rem;margin-top:10px;">No major missing skills found.</div></div>')
        return

    resume_set = {str(s).lower() for s in (resume_skills or [])}
    max_count = max(required.values()) if required else 1
    rows = []
    for skill, count in sorted(required.items(), key=lambda x: x[1], reverse=True)[:6]:
        if skill.lower() in resume_set:
            continue
        width = int((count / max_count) * 100)
        rows.append(
            f'<div style="display: grid; grid-template-columns: 100px 1fr 42px; gap: 7px; align-items: center; margin: 8px 0; font-size: 0.64rem; color: #445a77;">'
            f'<div>{safe_text(skill).title()}</div>'
            f'<div style="height: 8px; border-radius: 20px; background: #e7edf5; overflow: hidden;"><div style="height: 100%; border-radius: 20px; background: #2f80ed; width: {width}%;"></div></div>'
            f'<div>{count}</div></div>'
        )

    render_html("".join(rows) + "</div>")


def render_job_matches(jobs):
    if jobs is None or jobs.empty:
        render_html(
            """
            <div class="card">
                <div class="card-title">Top Job Matches for You</div>
                <div class="empty-state">No matching jobs found.</div>
            </div>
            """
        )
        return

    rows = []
    for rank, (_, job) in enumerate(jobs.head(5).iterrows(), start=1):
        title = safe_text(job.get("title"))
        company = safe_text(job.get("company", job.get("companyName")))
        location = safe_text(job.get("location"))
        try:
            score = float(job.get("match_score", 0))
        except (TypeError, ValueError):
            score = 0.0
        if score <= 1:
            score *= 100

        rows.append(
            f'<tr>'
            f'<td style="color:#6d7f98;font-weight:700;">{rank}</td>'
            f'<td style="color:#122b52;font-weight:700;">{title}</td>'
            f'<td>{company}</td><td>{location}</td>'
            f'<td><span class="match-pill">{score:.0f}%</span></td>'
            f'<td><a href="#" style="background: #2f80ed; color: white; padding: 3px 10px; border-radius: 6px; text-decoration: none; font-weight: 700; font-size: 0.64rem;">View</a></td>'
            f'</tr>'
        )

    render_html(
        f"""
        <div class="card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                <div class="card-title" style="margin-bottom:0;">Top Job Matches for You</div>
                <span style="font-size:.65rem;color:#2f80ed;font-weight:600;cursor:pointer;">View All →</span>
            </div>
            <table class="job-table">
                <thead>
                    <tr><th>#</th><th>Job Title</th><th>Company</th><th>Location</th><th>Match Score</th><th>Action</th></tr>
                </thead>
                <tbody>{''.join(rows)}</tbody>
            </table>
        </div>
        """
    )


@st.cache_data(show_spinner=False)
def load_job_dataset():
    return load_jobs()


@st.cache_data(show_spinner=False)
def calculate_top_jobs(resume_text, resume_skills, resume_experience, resume_education):
    jobs = load_job_dataset()
    return rank_jobs(
        resume_text=resume_text,
        resume_skills=list(resume_skills),
        resume_experience=resume_experience,
        resume_education=list(resume_education),
        jobs=jobs,
        top_n=10,
    )


# ==========================================================
# MAIN RENDER
# ==========================================================

def render_career_analysis():
    inject_styles()

    user_name = get_current_user_name() or "Enakshi"
    user_email = get_current_user_email() or "enakshi@gmail.com"

    # Well-balanced columns for the sidebar and main content area
    sidebar_col, content_col = st.columns([2.0, 6.0], gap="medium")

    with sidebar_col:
        selected_tab = render_sidebar(user_name, user_email)

    with content_col:
        if selected_tab != "🏠 My Career Analysis":
            render_html(
                f"""
                <div class="page-hero">
                    <div style="color: #0b1f45; font-size: 1.5rem; font-weight: 800;">{selected_tab}</div>
                    <div style="color: #49617f; font-size: 0.75rem; margin-top: 0.3rem;">
                        This section is currently under development. Switch back to "My Career Analysis" to view your resume insights.
                    </div>
                </div>
                """
            )
            return

        render_header(user_name)

        render_html(
            """
            <div class="card" style="margin-bottom: 0.8rem;">
                <div style="color: #10244b; font-size: 0.86rem; font-weight: 750;">Upload Your Resume</div>
                <div style="color: #64748b; font-size: 0.68rem; margin-top: 2px;">Upload your resume to start your personalized career analysis.</div>
            </div>
            """
        )

        upload_left, upload_right = st.columns([2.8, 1.2], gap="small")
        with upload_left:
            uploaded_resume = st.file_uploader(
                "Upload resume",
                type=["pdf", "docx"],
                key="career_resume_upload",
                label_visibility="collapsed",
            )
        with upload_right:
            render_html('<div style="font-size: 0.72rem; color: #64748b; text-align: center; margin-top: 6px;">Or try a sample resume</div>')
            if st.button("Use Sample Resume", use_container_width=True, key="use_sample_btn"):
                st.info("Sample resume functionality triggered!")

        if uploaded_resume is None:
            render_html(
                """
                <div class="empty-state">
                    <b>Start your Career Analysis</b><br><br>
                    Upload a PDF or DOCX resume above.<br><br>
                    CareerSense will analyze your skills, education and professional experience.
                </div>
                """
            )
            return

        try:
            with st.spinner("Analyzing your resume..."):
                resume_text = extract_resume_text(uploaded_resume)

            if not resume_text.strip():
                st.error("No readable text could be extracted from this resume.")
                return

            result = analyze_resume(resume_text)
            score = result.get("score", {})
            skills = result.get("skills", [])
            experience = result.get("experience", 0)
            education_list = result.get("education", [])

            education = ", ".join(str(item).replace("_", " ").title() for item in education_list) if isinstance(education_list, (list, tuple, set)) else safe_text(education_list, "Not detected")
            location = extract_resume_location(resume_text)

            st.session_state["career_resume_name"] = uploaded_resume.name
            st.session_state["career_resume_result"] = result

            col1, col2, col3 = st.columns([1.0, 1.25, 1.25], gap="small")
            with col1:
                render_resume_score(score)
            with col2:
                render_skills(skills)
            with col3:
                render_detected_information(user_name, user_email, experience, education, location)

            render_html('<div style="color: #10244b; font-size: 0.95rem; font-weight: 800; margin: 0.7rem 0 0.55rem 0;">Career Opportunities</div>')

            top_jobs = st.session_state.get("career_top_jobs")
            previous_resume = st.session_state.get("career_top_jobs_resume")

            if top_jobs is None or previous_resume != uploaded_resume.name:
                try:
                    with st.spinner("Finding the best matching jobs..."):
                        education_for_match = education_list if isinstance(education_list, (list, tuple, set)) else [education_list]
                        top_jobs = calculate_top_jobs(resume_text, tuple(skills), float(experience or 0), tuple(education_for_match))
                    st.session_state["career_top_jobs"] = top_jobs
                    st.session_state["career_top_jobs_resume"] = uploaded_resume.name
                except Exception as exc:
                    st.warning(f"Job matching could not be completed: {exc}")
                    top_jobs = pd.DataFrame()

            col4, col5 = st.columns([1.05, 1.95], gap="small")
            with col4:
                render_skill_gap(skills, top_jobs)
            with col5:
                render_job_matches(top_jobs)

        except Exception as exc:
            st.error("Something went wrong while analyzing the resume.")
            st.exception(exc)