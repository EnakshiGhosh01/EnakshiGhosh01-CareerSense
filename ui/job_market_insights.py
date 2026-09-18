import streamlit as st
import pandas as pd

from analytics.market_insights import (
    load_market_data,
    prepare_market_data,
    generate_market_insights,
)


# ==========================================================
# PAGE STYLING
# ==========================================================

def render_market_styles():

    st.markdown(
        """
        <style>

        .market-header {
            background: linear-gradient(
                135deg,
                #eef4ff 0%,
                #f8fbff 100%
            );
            border: 1px solid #dbe7f7;
            border-radius: 18px;
            padding: 24px 28px;
            margin-bottom: 20px;
        }

        .market-title {
            color: #0b1f45;
            font-size: 1.75rem;
            font-weight: 800;
            margin-bottom: 5px;
        }

        .market-subtitle {
            color: #49617f;
            font-size: 0.85rem;
        }

        .filter-box {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 16px;
            padding: 18px 20px 8px 20px;
            margin-bottom: 20px;
        }

        .section-title {
            color: #0b1f45;
            font-size: 1.15rem;
            font-weight: 750;
            margin-top: 20px;
            margin-bottom: 12px;
        }

        .metric-card {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 16px;
            padding: 18px;
            min-height: 125px;
            box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
        }

        .metric-label {
            color: #64748b;
            font-size: 0.78rem;
            font-weight: 600;
            margin-bottom: 8px;
        }

        .metric-value {
            color: #0b1f45;
            font-size: 1.35rem;
            font-weight: 800;
            line-height: 1.25;
        }

        .metric-description {
            color: #64748b;
            font-size: 0.70rem;
            margin-top: 6px;
        }

        .chart-card {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 16px;
            padding: 16px;
            margin-bottom: 18px;
        }

        .chart-title {
            color: #0b1f45;
            font-size: 1rem;
            font-weight: 750;
            margin-bottom: 4px;
        }

        .chart-caption {
            color: #64748b;
            font-size: 0.72rem;
            margin-bottom: 12px;
        }

        </style>
        """,
        unsafe_allow_html=True
    )


# ==========================================================
# HELPER FUNCTIONS
# ==========================================================

def safe_text(value, fallback="Not available"):

    if value is None:
        return fallback

    text = str(value).strip()

    if not text:
        return fallback

    if text.lower() in {
        "nan",
        "none",
        "null"
    }:
        return fallback

    return text


def format_lpa(value):

    if value is None:
        return "Not available"

    try:
        value = float(value)
    except (
        TypeError,
        ValueError
    ):
        return "Not available"

    return f"₹{value:.1f} LPA"


def format_salary_range_from_values(
    minimum_salary,
    maximum_salary
):

    if (
        minimum_salary is None
        or pd.isna(minimum_salary)
    ):

        if (
            maximum_salary is None
            or pd.isna(maximum_salary)
        ):
            return "Not disclosed"

        return f"Up to ₹{float(maximum_salary):.1f} LPA"

    if (
        maximum_salary is None
        or pd.isna(maximum_salary)
    ):

        return f"From ₹{float(minimum_salary):.1f} LPA"

    minimum_salary = float(
        minimum_salary
    )

    maximum_salary = float(
        maximum_salary
    )

    if minimum_salary > maximum_salary:

        minimum_salary, maximum_salary = (
            maximum_salary,
            minimum_salary
        )

    return (
        f"₹{minimum_salary:.1f} – "
        f"₹{maximum_salary:.1f} LPA"
    )


# ==========================================================
# FILTER INPUTS
# ==========================================================

def render_filters(jobs):

    st.markdown(
        '<div class="filter-box">',
        unsafe_allow_html=True
    )

    st.markdown(
        "### 🔎 Explore Job Market",
    )

    st.caption(
        "Filter the job market by role, location and experience level."
    )

    col1, col2, col3, col4 = st.columns(
        [2.4, 2.0, 1.5, 1.0]
    )

    # ------------------------------------------------------
    # Job Role
    # ------------------------------------------------------

    with col1:

        job_role = st.text_input(
            "Job Role",
            placeholder="e.g. Data Scientist",
            key="market_job_role"
        )

    # ------------------------------------------------------
    # Location
    # ------------------------------------------------------

    with col2:

        location = st.text_input(
            "Location",
            placeholder="e.g. Bengaluru",
            key="market_location"
        )

    # ------------------------------------------------------
    # Experience
    # ------------------------------------------------------

    with col3:

        experience_level = st.selectbox(
            "Experience Level",
            options=[
                "All",
                "0-1",
                "1-3",
                "3-5",
                "5-7",
                "7+"
            ],
            key="market_experience"
        )

    # ------------------------------------------------------
    # Apply
    # ------------------------------------------------------

    with col4:

        st.write("")

        apply_filters = st.button(
            "Apply Filters",
            type="primary",
            use_container_width=True,
            key="apply_market_filters"
        )

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )

    # ------------------------------------------------------
    # Store filters
    # ------------------------------------------------------

    if "market_filters_applied" not in st.session_state:

        st.session_state.market_filters_applied = {
            "job_role": None,
            "location": None,
            "experience_level": "All"
        }

    if apply_filters:

        st.session_state.market_filters_applied = {
            "job_role": job_role.strip()
            if job_role.strip()
            else None,

            "location": location.strip()
            if location.strip()
            else None,

            "experience_level": experience_level
        }

    return st.session_state.market_filters_applied


# ==========================================================
# SUMMARY CARD
# ==========================================================

def render_metric_card(
    label,
    value,
    description=""
):

    st.markdown(
        f"""
        <div class="metric-card">

            <div class="metric-label">
                {label}
            </div>

            <div class="metric-value">
                {value}
            </div>

            <div class="metric-description">
                {description}
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


# ==========================================================
# SUMMARY METRICS
# ==========================================================

def render_summary_cards(insights):

    total_jobs = insights[
        "total_jobs"
    ]

    remote_percentage = insights[
        "remote_percentage"
    ]

    salary_range = insights[
        "salary_range"
    ]

    top_role = insights[
        "top_hiring_role"
    ]

    col1, col2, col3, col4 = st.columns(4)

    # ------------------------------------------------------
    # Total jobs
    # ------------------------------------------------------

    with col1:

        render_metric_card(
            "Total Job Postings",
            f"{total_jobs:,}",
            "Matching postings in the selected market"
        )

    # ------------------------------------------------------
    # Remote jobs
    # ------------------------------------------------------

    with col2:

        render_metric_card(
            "Remote Jobs",
            f"{remote_percentage:.1f}%",
            "Share of postings marked as remote"
        )

    # ------------------------------------------------------
    # Salary range
    # ------------------------------------------------------

    with col3:

        render_metric_card(
            "Salary Range",
            salary_range["display"],
            "Range from disclosed salary postings"
        )

    # ------------------------------------------------------
    # Top hiring role
    # ------------------------------------------------------

    with col4:

        render_metric_card(
            "Top Hiring Role",
            safe_text(
                top_role,
                "Not available"
            ),
            "Most frequently posted job title"
        )


# ==========================================================
# SALARY BY EXPERIENCE
# ==========================================================

def render_salary_by_experience(
    salary_df
):

    st.markdown(
        '<div class="section-title">'
        '💰 Salary Range by Experience'
        '</div>',
        unsafe_allow_html=True
    )

    if salary_df.empty:

        st.info(
            "Salary information is not available "
            "for the selected filters."
        )

        return

    chart_df = salary_df[
        [
            "Experience",
            "Minimum Salary",
            "Maximum Salary"
        ]
    ].copy()

    chart_df = chart_df.set_index(
        "Experience"
    )

    chart_df = chart_df.rename(
        columns={
            "Minimum Salary": "Minimum",
            "Maximum Salary": "Maximum"
        }
    )

    st.line_chart(
        chart_df,
        use_container_width=True
    )

    st.caption(
        "Salary values are shown in LPA. "
        "Minimum and maximum represent the disclosed "
        "salary boundaries available in the dataset."
    )

    display_df = salary_df[
        [
            "Experience",
            "Salary Range"
        ]
    ].copy()

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )


# ==========================================================
# TOP LOCATIONS BY SALARY
# ==========================================================

def render_top_locations(
    locations_df
):

    st.markdown(
        '<div class="section-title">'
        '📍 Top Locations by Salary Range'
        '</div>',
        unsafe_allow_html=True
    )

    if locations_df.empty:

        st.info(
            "There is not enough disclosed salary data "
            "for location analysis."
        )

        return

    chart_df = locations_df[
        [
            "Location",
            "Minimum Salary",
            "Maximum Salary"
        ]
    ].copy()

    chart_df = chart_df.set_index(
        "Location"
    )

    chart_df = chart_df.rename(
        columns={
            "Minimum Salary": "Minimum",
            "Maximum Salary": "Maximum"
        }
    )

    st.bar_chart(
        chart_df,
        use_container_width=True
    )

    display_df = locations_df[
        [
            "Location",
            "Salary Range",
            "Job Count"
        ]
    ].copy()

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )


# ==========================================================
# TOP SKILLS
# ==========================================================

def render_top_skills(
    skills_df
):

    st.markdown(
        '<div class="section-title">'
        '🛠️ Top In-Demand Skills'
        '</div>',
        unsafe_allow_html=True
    )

    if skills_df.empty:

        st.info(
            "No skill-demand information is available."
        )

        return

    chart_df = skills_df[
        [
            "Skill",
            "Demand"
        ]
    ].copy()

    chart_df = chart_df.set_index(
        "Skill"
    )

    st.bar_chart(
        chart_df,
        use_container_width=True
    )

    st.caption(
        "Demand represents the number of job postings "
        "containing the skill in the dataset."
    )


# ==========================================================
# INDUSTRY DISTRIBUTION
# ==========================================================

def render_industry_distribution(
    industry_df
):

    st.markdown(
        '<div class="section-title">'
        '🏢 Job Distribution by Industry'
        '</div>',
        unsafe_allow_html=True
    )

    if industry_df.empty:

        st.info(
            "Industry information is not available."
        )

        return

    chart_df = industry_df[
        [
            "Industry",
            "Jobs"
        ]
    ].copy()

    chart_df = chart_df.set_index(
        "Industry"
    )

    st.bar_chart(
        chart_df,
        use_container_width=True
    )

    st.caption(
        "Industry is derived from job titles, descriptions "
        "and skills because the source dataset does not "
        "contain an explicit industry column."
    )


# ==========================================================
# TOP ROLES BY SALARY
# ==========================================================

def render_top_roles_by_salary(
    roles_df
):

    st.markdown(
        '<div class="section-title">'
        '💼 Top Job Roles by Salary Range'
        '</div>',
        unsafe_allow_html=True
    )

    if roles_df.empty:

        st.info(
            "There is not enough salary data "
            "for role-level analysis."
        )

        return

    chart_df = roles_df[
        [
            "Job Role",
            "Minimum Salary",
            "Maximum Salary"
        ]
    ].copy()

    chart_df = chart_df.set_index(
        "Job Role"
    )

    chart_df = chart_df.rename(
        columns={
            "Minimum Salary": "Minimum",
            "Maximum Salary": "Maximum"
        }
    )

    st.bar_chart(
        chart_df,
        use_container_width=True
    )

    display_df = roles_df[
        [
            "Job Role",
            "Salary Range",
            "Job Count"
        ]
    ].copy()

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )


# ==========================================================
# MARKET CHANGE
# ==========================================================

def render_market_changes(
    insights
):

    job_change = insights[
        "six_month_job_change"
    ]

    remote_change = insights[
        "six_month_remote_change"
    ]

    # ------------------------------------------------------
    # No historical data
    # ------------------------------------------------------

    if (
        job_change is None
        and remote_change is None
    ):

        return

    st.markdown(
        '<div class="section-title">'
        '📈 Market Changes'
        '</div>',
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    # ------------------------------------------------------
    # Job posting change
    # ------------------------------------------------------

    with col1:

        if job_change is None:

            st.info(
                "Six-month job-posting comparison "
                "is not available."
            )

        else:

            st.metric(
                "Six-Month Job Posting Change",
                f"{job_change:+.1f}%"
            )

    # ------------------------------------------------------
    # Remote change
    # ------------------------------------------------------

    with col2:

        if remote_change is None:

            st.info(
                "Six-month remote-job comparison "
                "is not available."
            )

        else:

            st.metric(
                "Six-Month Remote Share Change",
                f"{remote_change:+.1f} percentage points"
            )


# ==========================================================
# MAIN RENDER FUNCTION
# ==========================================================

@st.cache_data
def get_market_dataset():

    jobs = load_market_data()

    return prepare_market_data(
        jobs
    )


def render_job_market_insights():

    render_market_styles()

    # ======================================================
    # HEADER
    # ======================================================

    st.markdown(
        """
        <div class="market-header">

            <div class="market-title">
                Job Market Insights
            </div>

            <div class="market-subtitle">
                Explore current job-market demand,
                salary ranges, skills, locations,
                experience levels and industries.
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    # ======================================================
    # LOAD DATA
    # ======================================================

    try:

        jobs = get_market_dataset()

    except FileNotFoundError as error:

        st.error(
            str(error)
        )

        return

    except Exception as error:

        st.error(
            "Unable to load the job-market dataset."
        )

        st.exception(error)

        return

    # ======================================================
    # FILTERS
    # ======================================================

    filters = render_filters(
        jobs
    )

    # ======================================================
    # GENERATE INSIGHTS
    # ======================================================

    try:

        insights = generate_market_insights(
            jobs,
            job_role=filters["job_role"],
            location=filters["location"],
            experience_level=filters[
                "experience_level"
            ]
        )

    except Exception as error:

        st.error(
            "Unable to calculate market insights."
        )

        st.exception(error)

        return

    # ======================================================
    # FILTER STATUS
    # ======================================================

    active_filters = []

    if filters["job_role"]:

        active_filters.append(
            f"Role: {filters['job_role']}"
        )

    if filters["location"]:

        active_filters.append(
            f"Location: {filters['location']}"
        )

    if (
        filters["experience_level"]
        != "All"
    ):

        active_filters.append(
            "Experience: "
            + filters["experience_level"]
        )

    if active_filters:

        st.caption(
            "Active filters: "
            + " • ".join(active_filters)
        )

    # ======================================================
    # NO RESULTS
    # ======================================================

    if insights["total_jobs"] == 0:

        st.warning(
            "No job postings match the selected filters. "
            "Try a broader role or location."
        )

        return

    # ======================================================
    # SUMMARY
    # ======================================================

    render_summary_cards(
        insights
    )

    st.divider()

    # ======================================================
    # FIRST ROW
    # ======================================================

    col1, col2 = st.columns(
        2,
        gap="large"
    )

    with col1:

        render_salary_by_experience(
            insights[
                "salary_by_experience"
            ]
        )

    with col2:

        render_top_locations(
            insights[
                "top_locations_by_salary"
            ]
        )

    # ======================================================
    # SECOND ROW
    # ======================================================

    col3, col4 = st.columns(
        2,
        gap="large"
    )

    with col3:

        render_top_skills(
            insights[
                "top_skills"
            ]
        )

    with col4:

        render_industry_distribution(
            insights[
                "industry_distribution"
            ]
        )

    # ======================================================
    # THIRD ROW
    # ======================================================

    render_top_roles_by_salary(
        insights[
            "top_roles_by_salary"
        ]
    )

    # ======================================================
    # MARKET CHANGE
    # ======================================================

    render_market_changes(
        insights
    )

    # ======================================================
    # DATA NOTE
    # ======================================================

    st.divider()

    st.caption(
        "Salary analytics use disclosed salary information "
        "from the processed job dataset. "
        "Salary ranges are displayed instead of a single "
        "fixed salary value. "
        "Industry categories are derived because the source "
        "dataset does not contain an explicit industry field."
    )