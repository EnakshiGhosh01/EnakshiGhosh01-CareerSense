from ui.job_market_insights import render_job_market_insights
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
# GLOBAL STYLES (Enhanced UI)
# ==========================================================

def inject_styles():
    render_html(
        """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}

        .stApp {
            background: #f4f7fc;
        }

        .block-container {
            padding-top: 1rem;
            padding-bottom: 2.5rem;
            max-width: 1520px;
        }

        /* ==================================================
           CUSTOM SIDEBAR CONTAINER STYLING
        ================================================== */
        .st-key-career_sidebar {
            background: linear-gradient(180deg, #0b1f36 0%, #081628 100%);
            color: white;
            border-radius: 16px;
            min-height: calc(100vh - 2rem);
            padding: 22px 14px 20px 14px !important;
            box-sizing: border-box;
            width: 100%;
            box-shadow: 0 10px 25px -5px rgba(11, 31, 54, 0.2);
        }

        .cs-sidebar {
            background: transparent;
            color: white;
            width: 100%;
            box-sizing: border-box;
        }

        .st-key-career_sidebar div[data-testid="stRadio"] {
            width: 100%;
            margin-top: 0;
            margin-bottom: 0;
        }

        .cs-brand {
            color: white;
            font-size: 1.15rem;
            font-weight: 800;
            padding: 2px 4px 16px 4px;
            letter-spacing: -0.3px;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .cs-user {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 12px 6px 16px 6px;
            border-bottom: 1px solid rgba(255,255,255,0.08);
            margin-bottom: 14px;
            background: rgba(255, 255, 255, 0.03);
            border-radius: 10px;
        }

        .cs-avatar {
            width: 42px;
            height: 42px;
            min-width: 42px;
            border-radius: 50%;
            background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 800;
            font-size: 0.9rem;
            box-shadow: 0 4px 10px rgba(59, 130, 246, 0.3);
        }

        .cs-hello {
            color: #94a3b8;
            font-size: 0.68rem;
            line-height: 1.2;
            font-weight: 500;
        }

        .cs-user-name {
            color: #ffffff;
            font-size: 1rem;
            font-weight: 800;
            line-height: 1.25;
            margin-top: 1px;
        }

        .cs-user-email {
            color: #cbd5e1;
            font-size: 0.75rem;
            line-height: 1.25;
            margin-top: 2px;
            word-break: break-word;
        }

        .cs-nav-label {
            color: #64748b;
            font-size: 0.58rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            padding: 6px 4px 8px 4px;
            font-weight: 700;
        }

        /* ==================================================
           STREAMLIT RADIO NAVIGATION OVERRIDES
        ================================================== */
        div[data-testid="stRadio"] > label {
            display: none !important;
        }

        div[data-testid="stRadio"] div[role="radiogroup"] {
            gap: 4px;
        }

        div[data-testid="stRadio"] div[role="radiogroup"] label {
            background: transparent;
            border-radius: 10px;
            padding: 9px 12px;
            margin: 2px 0;
            color: #cbd5e1 !important;
            font-size: 0.78rem;
            font-weight: 500;
            width: 100%;
            border: none;
            box-sizing: border-box;
            transition: all 0.2s ease;
        }

        div[data-testid="stRadio"] div[role="radiogroup"] label:hover {
            background: rgba(255, 255, 255, 0.06);
            color: #ffffff !important;
            transform: translateX(3px);
        }

        div[data-testid="stRadio"] div[role="radiogroup"] label * {
            color: inherit !important;
        }

        div[data-testid="stRadio"] div[role="radiogroup"] label[data-baseweb="radio"] input:checked + div {
            background: #2563eb;
        }

        div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) {
            background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
            color: #ffffff !important;
            font-weight: 700;
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
        }

        div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) * {
            color: #ffffff !important;
        }

        div[data-testid="stRadio"] div[role="radiogroup"] input[type="radio"] {
            display: none;
        }

        /* ==================================================
           LOGOUT BUTTON STYLING
        ================================================== */
        .st-key-career_logout button {
            background-color: rgba(255, 255, 255, 0.04) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            color: #cbd5e1 !important;
            text-align: left !important;
            border-radius: 10px !important;
            min-height: 40px !important;
            font-size: 0.76rem !important;
            font-weight: 600 !important;
            padding: 8px 12px !important;
            box-shadow: none !important;
            width: 100% !important;
            margin-top: 12px !important;
            transition: all 0.2s ease !important;
        }
        .st-key-career_logout button * {
            color: inherit !important;
        }
        .st-key-career_logout button:hover {
            background-color: #dc2626 !important;
            border-color: #dc2626 !important;
            color: #ffffff !important;
            box-shadow: 0 4px 12px rgba(220, 38, 38, 0.3) !important;
        }

        /* ==================================================
           PAGE HERO & CARDS
        ================================================== */
        .page-hero {
            background: linear-gradient(135deg, #eff6ff 0%, #e0e7ff 100%);
            border: 1px solid #c7d2fe;
            border-radius: 16px;
            padding: 1.4rem 1.8rem;
            margin-bottom: 1rem;
            box-shadow: 0 4px 20px -2px rgba(79, 70, 229, 0.06);
        }

        .card {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 14px;
            padding: 1.1rem 1.25rem;
            box-shadow: 0 4px 16px -4px rgba(15, 23, 42, 0.05);
            height: 100%;
            box-sizing: border-box;
            transition: all 0.2s ease;
        }
        
        .card:hover {
            box-shadow: 0 6px 20px -4px rgba(15, 23, 42, 0.08);
            border-color: #cbd5e1;
        }

        .card-title {
            color: #0f172a;
            font-size: 0.92rem;
            font-weight: 750;
            margin-bottom: 0.6rem;
            letter-spacing: -0.2px;
        }

        .skill-badge {
            display: inline-flex;
            align-items: center;
            gap: 5px;
            background: #f0fdf4;
            color: #15803d;
            border-radius: 8px;
            padding: 4px 9px;
            margin: 3px 4px 3px 0;
            font-size: 0.7rem;
            font-weight: 650;
            border: 1px solid #bbf7d0;
        }

        .skill-badge.blue {
            background: #eff6ff;
            color: #1d4ed8;
            border: 1px solid #bfdbfe;
        }
        
        .skill-badge.purple {
            background: #faf5ff;
            color: #7e22ce;
            border: 1px solid #e9d5ff;
        }

        .job-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.7rem;
        }
        .job-table th {
            color: #64748b;
            font-weight: 700;
            text-align: left;
            padding: 8px 8px;
            border-bottom: 2px solid #f1f5f9;
            text-transform: uppercase;
            font-size: 0.62rem;
            letter-spacing: 0.5px;
        }
        .job-table td {
            color: #1e293b;
            padding: 10px 8px;
            border-bottom: 1px solid #f1f5f9;
            vertical-align: middle;
        }
        .match-pill {
            display: inline-block;
            background: #dcfce7;
            color: #166534;
            padding: 4px 8px;
            border-radius: 6px;
            font-weight: 750;
            font-size: 0.68rem;
        }

        .empty-state {
            background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
            border: 2px dashed #cbd5e1;
            border-radius: 12px;
            padding: 1.6rem;
            text-align: center;
            color: #475569;
            font-size: 0.76rem;
            margin-top: 0.8rem;
        }

        /* ==================================================
           STREAMLIT FILE UPLOADER ENHANCEMENTS
        ================================================== */
        div[data-testid="stFileUploader"] {
            background: #ffffff;
            border: 2px dashed #93c5fd;
            border-radius: 12px;
            padding: 12px;
            transition: all 0.2s ease;
        }
        div[data-testid="stFileUploader"]:hover {
            border-color: #2563eb;
            background: #f8fafc;
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

    render_html(
        f"""
        <div class="cs-sidebar">
            <div>
                <div class="cs-brand">
                    <span style="font-size: 1.3rem;">📊</span> CareerSense
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
                    Workspace Navigation
                </div>
            </div>
        """
    )

    nav_tabs = [
        "📤 My Career Analysis",
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

    render_html(
        """
            <div style="margin-top: auto; padding-top: 18px;">
                <div style="padding-top: 12px; border-top: 1px solid rgba(255,255,255,0.08);">
                    <div style="color: #f8fafc; font-size: 0.78rem; font-weight: 750;">📊 CareerSense</div>
                    <div style="color: #94a3b8; font-size: 0.58rem; margin-top: 3px;">Your Career. Smarter.</div>
                </div>
            </div>
        """
    )

    st.markdown('<div class="st-key-career_logout">', unsafe_allow_html=True)
    if st.button("🚪 Logout", use_container_width=True, key="career_logout"):
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
                    <div style="color: #0f172a; font-size: 1.75rem; font-weight: 850; letter-spacing: -0.5px;">My Career Analysis</div>
                    <div style="color: #475569; font-size: 0.8rem; margin-top: 0.35rem; font-weight: 500;">
                        Upload your resume and get personalized insights, job recommendations and skill gap analysis.
                    </div>
                </div>
                <div>
                    <div style="color: #475569; font-size: 0.82rem; text-align: right; line-height: 1.4;">
                        Hello, <b style="font-size: 0.96rem; color: #0f172a; font-weight: 800;">{safe_text(user_name, "User")}</b><br>
                        Your skills today,<br>
                        <b style="color: #2563eb;">new opportunities tomorrow.</b>
                    </div>
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
            <div style="display: flex; align-items: center; gap: 16px; margin-top: 12px;">
                <div style="width: 96px; height: 96px; border-radius: 50%; background: conic-gradient(#10b981 0deg {degrees}deg, #f1f5f9 {degrees}deg 360deg); display: flex; align-items: center; justify-content: center; flex-shrink: 0; box-shadow: 0 4px 12px rgba(16, 185, 129, 0.2);">
                    <div style="width: 74px; height: 74px; border-radius: 50%; background: white; display: flex; flex-direction: column; align-items: center; justify-content: center;">
                        <div style="color: #0f172a; font-size: 1.45rem; font-weight: 850; line-height: 1;">{total}</div>
                        <div style="color: #64748b; font-size: 0.62rem; margin-top: 2px; font-weight: 600;">/100</div>
                    </div>
                </div>
                <div style="color: #334155; font-size: 0.72rem; line-height: 1.5; font-weight: 500;">
                    {get_score_message(total)}
                </div>
            </div>
        </div>
        """
    )


def render_skills(skills):
    st.markdown('<div class="card">', unsafe_allow_html=True)
    
    col_t1, col_t2 = st.columns([2, 1])
    with col_t1:
        st.markdown('<div class="card-title" style="margin-bottom:0;">Key Skills Detected</div>', unsafe_allow_html=True)
    with col_t2:
        with st.popover("+ Add Skill", use_container_width=True):
            st.markdown("##### Add New Skill")
            new_skill_input = st.text_input("Skill name", key="new_skill_text_input", placeholder="e.g. Docker, React")
            if st.button("Add to List", key="confirm_add_skill_btn"):
                if new_skill_input.strip():
                    skill_cleaned = new_skill_input.strip().title()
                    if skill_cleaned not in st.session_state["editable_skills"]:
                        st.session_state["editable_skills"].append(skill_cleaned)
                        st.session_state["profile_has_changed"] = True
                        st.success(f"Added '{skill_cleaned}'! Click '🚀 New Opportunities' below to update matches.")
                        st.rerun()

    if not st.session_state["editable_skills"]:
        st.markdown('<div style="color:#64748b;font-size:.72rem;margin-top:8px;">No skills detected yet.</div>', unsafe_allow_html=True)
    else:
        chips_html = '<div style="margin-top: 8px; display: flex; flex-wrap: wrap; gap: 4px;">'
        for i, s in enumerate(st.session_state["editable_skills"]):
            color_class = "purple" if i % 3 == 2 else ("blue" if i % 3 == 1 else "")
            chips_html += f'<span class="skill-badge {color_class}">{safe_text(s)}</span>'
        chips_html += '</div>'
        st.markdown(chips_html, unsafe_allow_html=True)

        with st.expander("🗑️ Delete a Skill"):
            skill_to_delete = st.selectbox("Select skill to remove", options=st.session_state["editable_skills"], key="del_skill_select")
            if st.button("Remove Selected Skill", key="confirm_del_skill_btn"):
                if skill_to_delete in st.session_state["editable_skills"]:
                    st.session_state["editable_skills"].remove(skill_to_delete)
                    st.session_state["profile_has_changed"] = True
                    st.success(f"Removed '{skill_to_delete}'! Click '🚀 New Opportunities' below to update matches.")
                    st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


def render_detected_information(user_name, user_email):
    st.markdown('<div class="card">', unsafe_allow_html=True)
    
    col_d1, col_d2 = st.columns([2, 1])
    with col_d1:
        st.markdown('<div class="card-title" style="margin-bottom:0;">Detected Information</div>', unsafe_allow_html=True)
    with col_d2:
        with st.popover("Edit Info", use_container_width=True):
            st.markdown("##### Edit Details")
            with st.form("edit_detected_info_form"):
                ed_name = st.text_input("Name", value=st.session_state.get("editable_name", user_name))
                ed_email = st.text_input("Email", value=st.session_state.get("editable_email", user_email))
                ed_exp = st.text_input("Experience", value=st.session_state.get("editable_experience", "0 years"))
                ed_edu = st.text_input("Education", value=st.session_state.get("editable_education", "Bachelors"))
                ed_loc = st.text_input("Location", value=st.session_state.get("editable_location", "Not detected"))
                
                submitted = st.form_submit_button("Save Changes")
                if submitted:
                    st.session_state["editable_name"] = ed_name
                    st.session_state["editable_email"] = ed_email
                    st.session_state["editable_experience"] = ed_exp
                    st.session_state["editable_education"] = ed_edu
                    st.session_state["editable_location"] = ed_loc
                    st.session_state["profile_has_changed"] = True
                    st.success("Updated successfully! Click '🚀 New Opportunities' below to refresh matches.")
                    st.rerun()

    current_info = {
        "Name": st.session_state.get("editable_name", user_name),
        "Email": st.session_state.get("editable_email", user_email),
        "Experience": st.session_state.get("editable_experience", "0 years"),
        "Education": st.session_state.get("editable_education", "Not detected"),
        "Location": st.session_state.get("editable_location", "Not detected"),
    }

    body = "".join(
        f'<div style="display: grid; grid-template-columns: 90px 1fr; gap: 8px; padding: 5px 0; font-size: 0.72rem;">'
        f'<div style="color: #64748b; font-weight: 500;">{lbl}</div><div style="color: #0f172a; font-weight: 700; word-break: break-word;">{val}</div></div>'
        for lbl, val in current_info.items()
    )
    st.markdown(f'<div style="margin-top: 6px;">{body}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


def render_skill_gap(resume_skills, jobs):
    render_html(
        """
        <div class="card">
            <div class="card-title">Skill Gap Analysis</div>
            <div style="display: flex; gap: 14px; font-size: 0.62rem; color: #64748b; margin-bottom: 8px; font-weight: 500;">
                <span>● Your Skills</span><span>■ Required in Job Market</span>
            </div>
        """
    )

    if jobs is None or jobs.empty:
        render_html('<div class="empty-state" style="margin-top:0;">Click "🚀 New Opportunities" below to calculate skill gaps.</div></div>')
        return

    required = {}
    for _, job in jobs.iterrows():
        missing = job.get("missing_skills", [])
        missing_skills = missing if isinstance(missing, (list, tuple, set)) else [s.strip() for s in safe_text(missing, "").split(",") if s.strip()]
        for skill in missing_skills:
            if skill:
                required[skill] = required.get(skill, 0) + 1

    if not required:
        render_html('<div style="color:#15803d;font-size:.72rem;margin-top:10px;font-weight:600;">No major missing skills found.</div></div>')
        return

    resume_set = {str(s).lower() for s in (resume_skills or [])}
    max_count = max(required.values()) if required else 1
    rows = []
    for skill, count in sorted(required.items(), key=lambda x: x[1], reverse=True)[:6]:
        if skill.lower() in resume_set:
            continue
        width = int((count / max_count) * 100)
        rows.append(
            f'<div style="display: grid; grid-template-columns: 105px 1fr 45px; gap: 8px; align-items: center; margin: 9px 0; font-size: 0.68rem; color: #334155; font-weight: 500;">'
            f'<div style="font-weight: 600;">{safe_text(skill).title()}</div>'
            f'<div style="height: 9px; border-radius: 20px; background: #f1f5f9; overflow: hidden;"><div style="height: 100%; border-radius: 20px; background: linear-gradient(90deg, #3b82f6 0%, #1d4ed8 100%); width: {width}%;"></div></div>'
            f'<div style="text-align: right; font-weight: 700; color: #64748b;">{count}</div></div>'
        )

    render_html("".join(rows) + "</div>")


# ==========================================================
# MODAL FOR "VIEW ALL"
# ==========================================================

@st.dialog("All Matching Career Opportunities", width="large")
def show_all_jobs_modal(jobs_df):
    st.markdown("Here is the complete list of matching jobs sorted by your highest compatibility score:")
    
    h_col1, h_col2, h_col3, h_col4, h_col5 = st.columns([0.5, 3.5, 2.5, 2.5, 1.2])
    with h_col1:
        st.markdown('**#**')
    with h_col2:
        st.markdown('**Job Title**')
    with h_col3:
        st.markdown('**Company**')
    with h_col4:
        st.markdown('**Location**')
    with h_col5:
        st.markdown('**Match**')

    st.markdown("<hr style='margin: 4px 0 8px 0;'>", unsafe_allow_html=True)

    for rank, (idx, job) in enumerate(jobs_df.iterrows(), start=1):
        title = safe_text(job.get("title"))
        company = safe_text(job.get("company", job.get("companyName")))
        location = safe_text(job.get("location"))
        try:
            score = float(job.get("match_score", 0))
        except (TypeError, ValueError):
            score = 0.0
        if score <= 1:
            score *= 100

        r_col1, r_col2, r_col3, r_col4, r_col5 = st.columns([0.5, 3.5, 2.5, 2.5, 1.2])
        with r_col1:
            st.markdown(f'<div style="color:#64748b;font-weight:800;font-size:0.7rem;padding-top:8px;">{rank}</div>', unsafe_allow_html=True)
        with r_col2:
            st.markdown(f'<div style="color:#0f172a;font-weight:750;font-size:0.7rem;padding-top:8px;">{title}</div>', unsafe_allow_html=True)
        with r_col3:
            st.markdown(f'<div style="color:#334155;font-weight:500;font-size:0.7rem;padding-top:8px;">{company}</div>', unsafe_allow_html=True)
        with r_col4:
            st.markdown(f'<div style="color:#64748b;font-size:0.7rem;padding-top:8px;">{location}</div>', unsafe_allow_html=True)
        with r_col5:
            st.markdown(f'<div style="padding-top:6px;"><span class="match-pill">{score:.0f}%</span></div>', unsafe_allow_html=True)


def render_job_matches(jobs):
    if jobs is None or jobs.empty:
        render_html(
            """
            <div class="card">
                <div class="card-title">Top Job Matches for You</div>
                <div class="empty-state">Click "🚀 New Opportunities" below to find matching jobs based on your updated profile.</div>
            </div>
            """
        )
        return

    st.markdown('<div class="card">', unsafe_allow_html=True)
    
    col_h1, col_h2 = st.columns([3, 1])
    with col_h1:
        st.markdown('<div class="card-title" style="margin-bottom:0;">Top Job Matches for You</div>', unsafe_allow_html=True)
    with col_h2:
        if st.button("View All →", key="view_all_jobs_btn", use_container_width=True):
            show_all_jobs_modal(jobs)

    render_html(
        """
        <div style="margin-top: 10px;">
            <table class="job-table">
                <thead>
                    <tr><th>#</th><th>Job Title</th><th>Company</th><th>Location</th><th>Match Score</th></tr>
                </thead>
            </table>
        </div>
        """
    )

    for rank, (idx, job) in enumerate(jobs.head(5).iterrows(), start=1):
        title = safe_text(job.get("title"))
        company = safe_text(job.get("company", job.get("companyName")))
        location = safe_text(job.get("location"))
        try:
            score = float(job.get("match_score", 0))
        except (TypeError, ValueError):
            score = 0.0
        if score <= 1:
            score *= 100

        r_col1, r_col2, r_col3, r_col4, r_col5 = st.columns([0.5, 3.2, 2.5, 2.5, 1.3])
        with r_col1:
            st.markdown(f'<div style="color:#64748b;font-weight:800;font-size:0.7rem;padding-top:8px;">{rank}</div>', unsafe_allow_html=True)
        with r_col2:
            st.markdown(f'<div style="color:#0f172a;font-weight:750;font-size:0.7rem;padding-top:8px;">{title}</div>', unsafe_allow_html=True)
        with r_col3:
            st.markdown(f'<div style="color:#334155;font-weight:500;font-size:0.7rem;padding-top:8px;">{company}</div>', unsafe_allow_html=True)
        with r_col4:
            st.markdown(f'<div style="color:#64748b;font-size:0.7rem;padding-top:8px;">{location}</div>', unsafe_allow_html=True)
        with r_col5:
            st.markdown(f'<div style="padding-top:6px;"><span class="match-pill">{score:.0f}%</span></div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


@st.cache_data(show_spinner=False)
def load_job_dataset():
    return load_jobs()


@st.cache_data(show_spinner=False)
def calculate_top_jobs(resume_text, resume_skills, resume_experience, resume_education, location_filter=""):
    jobs = load_job_dataset()
    
    if location_filter and location_filter.lower() != "not detected":
        loc_lower = location_filter.lower()
        jobs = jobs[jobs['location'].astype(str).str.lower().str.contains(loc_lower, na=False)]
        if jobs.empty:
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

    user_name = get_current_user_name() or "User"
    user_email = get_current_user_email() or "user@example.com"

    sidebar_col, content_col = st.columns([2.0, 6.0], gap="medium")

    with sidebar_col:
        with st.container(key="career_sidebar"):
            selected_tab = render_sidebar(user_name, user_email)

    with content_col:

        if selected_tab == "📊 Job Market Insights":
            render_job_market_insights()
            return

        if selected_tab != "📤 My Career Analysis":
            render_html(
            f"""
            <div class="page-hero">
                <div style="color: #0f172a; font-size: 1.6rem; font-weight: 850;">
                    {selected_tab}
                </div>
                <div style="color: #475569; font-size: 0.8rem; margin-top: 0.35rem; font-weight: 500;">
                    This section is currently under development. Switch back to "My Career Analysis" to view your resume insights.
                </div>
            </div>
            """
        )
            return

        render_header(user_name)

        render_html(
            """
            <div class="card" style="margin-bottom: 1rem;">
                <div style="color: #0f172a; font-size: 0.92rem; font-weight: 750;">Upload Your Resume</div>
                <div style="color: #64748b; font-size: 0.72rem; margin-top: 3px; font-weight: 500;">Upload your resume to start your personalized career analysis.</div>
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
            render_html('<div style="font-size: 0.74rem; color: #64748b; text-align: center; margin-top: 10px; font-weight: 600;">Or try a sample resume</div>')
            if st.button("Use Sample Resume", use_container_width=True, key="use_sample_btn"):
                st.info("Sample resume functionality triggered!")

        if uploaded_resume is None:
            render_html(
                """
                <div class="empty-state">
                    <b style="font-size: 0.9rem; color: #1e293b;">Start your Career Analysis</b><br><br>
                    Upload a PDF or DOCX resume above.<br><br>
                    <span style="color: #64748b;">CareerSense will analyze your skills, education and professional experience.</span>
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
            parsed_skills = result.get("skills", [])
            experience = result.get("experience", 0)
            education_list = result.get("education", [])

            education = ", ".join(str(item).replace("_", " ").title() for item in education_list) if isinstance(education_list, (list, tuple, set)) else safe_text(education_list, "Not detected")
            location = extract_resume_location(resume_text)

            is_new_upload = st.session_state.get("last_uploaded_file") != uploaded_resume.name

            if "editable_skills" not in st.session_state or is_new_upload:
                st.session_state["editable_skills"] = list(parsed_skills)
                st.session_state["editable_name"] = user_name
                st.session_state["editable_email"] = user_email
                st.session_state["editable_experience"] = f"{float(experience):g} years" if isinstance(experience, (int, float)) else safe_text(experience)
                st.session_state["editable_education"] = education
                st.session_state["editable_location"] = location
                st.session_state["last_uploaded_file"] = uploaded_resume.name
                st.session_state["profile_has_changed"] = True

            st.session_state["career_resume_name"] = uploaded_resume.name
            st.session_state["career_resume_result"] = result

            col1, col2, col3 = st.columns([1.0, 1.25, 1.25], gap="small")
            with col1:
                render_resume_score(score)
            with col2:
                render_skills(st.session_state["editable_skills"])
            with col3:
                render_detected_information(user_name, user_email)

            # ==========================================================
            # NEW OPPORTUNITIES ACTION BUTTON SECTION
            # ==========================================================
            render_html('<div style="margin: 1.2rem 0 0.4rem 0;"></div>')
            
            if st.session_state.get("profile_has_changed", False) and not is_new_upload:
                render_html(
                    """
                    <div style="background: #eff6ff; border: 1px solid #bfdbfe; color: #1e40af; padding: 8px 14px; border-radius: 8px; font-size: 0.74rem; font-weight: 600; margin-bottom: 10px; display: flex; align-items: center; justify-content: space-between;">
                        <span>ℹ️ You have modified your profile, skills, or location details. Click <b>🚀 New Opportunities</b> below to refresh your job matches and skill gap analysis.</span>
                    </div>
                    """
                )

            btn_col1, btn_col2, btn_col3 = st.columns([2, 2, 2])
            with btn_col2:
                trigger_new_opps = st.button("🚀 New Opportunities", use_container_width=True, key="trigger_new_opportunities_btn", type="primary")

            render_html('<div style="color: #0f172a; font-size: 1.05rem; font-weight: 850; margin: 1rem 0 0.6rem 0; letter-spacing: -0.3px;">Career Opportunities</div>')

            exp_str = str(st.session_state.get("editable_experience", experience))
            exp_match = re.search(r"([\d\.]+)", exp_str)
            parsed_exp_val = float(exp_match.group(1)) if exp_match else float(experience or 0)
            current_location = st.session_state.get("editable_location", location)

            top_jobs = st.session_state.get("career_top_jobs")

            if is_new_upload or trigger_new_opps:
                try:
                    spinner_text = "Analyzing and finding job matches for your new resume..." if is_new_upload else "Finding new opportunities and recalculating skill gap based on your updates..."
                    with st.spinner(spinner_text):
                        education_for_match = education_list if isinstance(education_list, (list, tuple, set)) else [education_list]
                        top_jobs = calculate_top_jobs(
                            resume_text,
                            tuple(st.session_state["editable_skills"]),
                            parsed_exp_val,
                            tuple(education_for_match),
                            current_location
                        )
                    st.session_state["career_top_jobs"] = top_jobs
                    st.session_state["career_top_jobs_resume"] = uploaded_resume.name
                    st.session_state["profile_has_changed"] = False
                    if trigger_new_opps:
                        st.success("Successfully updated job matches and skill gaps based on your current profile!")
                except Exception as exc:
                    st.warning(f"Job matching could not be completed: {exc}")
                    top_jobs = pd.DataFrame()

            col4, col5 = st.columns([1.05, 1.95], gap="small")
            with col4:
                render_skill_gap(st.session_state["editable_skills"], top_jobs)
            with col5:
                render_job_matches(top_jobs)

        except Exception as exc:
            st.error("Something went wrong while analyzing the resume.")
            st.exception(exc)