import pandas as pd
import streamlit as st
import altair as alt

from analytics.market_insights import (
    load_market_data,
    prepare_market_data,
    filter_jobs,
    calculate_total_jobs,
    calculate_remote_percentage,
    calculate_salary_range,
    calculate_top_hiring_role,
    calculate_salary_by_experience,
    calculate_top_locations_by_salary,
    calculate_top_skills,
    calculate_industry_distribution,
    calculate_top_roles_by_salary,
    calculate_six_month_change,
    calculate_remote_six_month_change,
)


# ============================================================
# DATA
# ============================================================


@st.cache_data(show_spinner="Loading job-market dataset...")
def get_market_dataset():
    return prepare_market_data(load_market_data())


def safe_value(value, fallback="Not available"):
    if value is None:
        return fallback
    try:
        if pd.isna(value):
            return fallback
    except (TypeError, ValueError):
        pass
    value = str(value).strip()
    return value if value and value.lower() not in {"nan", "none", "null"} else fallback


def salary_display(salary_range):
    if not isinstance(salary_range, dict):
        return "Not disclosed"
    return safe_value(salary_range.get("display"), "Not disclosed")


def make_salary_range_chart(data, category_column, title_column=None, height=300):
    """Render salary minimum-to-maximum ranges as horizontal interval bars."""
    if data is None or data.empty:
        st.info("There is not enough disclosed salary data for this comparison.")
        return

    chart_data = data.copy()
    chart_data["Minimum Salary"] = pd.to_numeric(
        chart_data["Minimum Salary"], errors="coerce"
    )
    chart_data["Maximum Salary"] = pd.to_numeric(
        chart_data["Maximum Salary"], errors="coerce"
    )
    chart_data = chart_data.dropna(
        subset=["Minimum Salary", "Maximum Salary"], how="all"
    )
    chart_data["Minimum Salary"] = chart_data["Minimum Salary"].fillna(
        chart_data["Maximum Salary"]
    )
    chart_data["Maximum Salary"] = chart_data["Maximum Salary"].fillna(
        chart_data["Minimum Salary"]
    )
    chart_data = chart_data[
        chart_data["Maximum Salary"] >= chart_data["Minimum Salary"]
    ]

    if chart_data.empty:
        st.info("There is not enough valid salary information to draw this chart.")
        return

    chart_data["Salary Range"] = (
        "₹" + chart_data["Minimum Salary"].round(1).astype(str)
        + " – ₹" + chart_data["Maximum Salary"].round(1).astype(str) + " LPA"
    )

    chart = (
        alt.Chart(chart_data)
        .mark_bar(size=18, cornerRadius=4, color="#3978E8")
        .encode(
            y=alt.Y(
                f"{category_column}:N",
                sort="-x",
                title=None,
                axis=alt.Axis(labelLimit=180),
            ),
            x=alt.X(
                "Minimum Salary:Q",
                title="Salary (LPA)",
                scale=alt.Scale(zero=True),
            ),
            x2=alt.X2("Maximum Salary:Q"),
            tooltip=[
                alt.Tooltip(f"{category_column}:N", title=title_column or category_column),
                alt.Tooltip("Minimum Salary:Q", format=".1f", title="Minimum (LPA)"),
                alt.Tooltip("Maximum Salary:Q", format=".1f", title="Maximum (LPA)"),
                alt.Tooltip("Salary Range:N"),
            ],
        )
        .properties(height=height)
    )
    st.altair_chart(chart, use_container_width=True)


def render_metric_card(label, value, help_text):
    # Native Streamlit card: no HTML strings are used.
    with st.container(border=True):
        st.caption(label)
        st.markdown(f"### {value}")
        st.caption(help_text)


# ============================================================
# FILTERS
# ============================================================


def render_filters(jobs):
    """
    Collect filters and only generate dashboard results after Apply Filters.
    Dropdown choices come from the dataset to avoid invalid free-text filters.
    """
    st.subheader("🔎 Explore Job Market")
    st.caption(
        "Choose a role, location and experience level, then apply filters "
        "to generate the market insights."
    )

    role_counts = (
        jobs["title"]
        .dropna()
        .astype(str)
        .str.strip()
        .replace("", pd.NA)
        .dropna()
        .value_counts()
    )
    role_options = role_counts.head(250).index.tolist()

    location_counts = (
        jobs["location"]
        .dropna()
        .astype(str)
        .str.strip()
        .replace("", pd.NA)
        .dropna()
        .value_counts()
    )
    location_options = location_counts.head(150).index.tolist()

    if "market_filters_native" not in st.session_state:
        st.session_state.market_filters_native = {
            "job_role": None,
            "location": None,
            "experience_level": "All",
        }

    if "market_filters_submitted" not in st.session_state:
        st.session_state.market_filters_submitted = False

    saved = st.session_state.market_filters_native
    saved_role = saved.get("job_role") or "All Roles"
    saved_location = saved.get("location") or "All Locations"
    saved_experience = saved.get("experience_level", "All")
    saved_experience = (
        "All Levels" if saved_experience == "All" else saved_experience
    )

    role_choices = ["All Roles"] + role_options
    location_choices = ["All Locations"] + location_options
    experience_choices = ["All Levels", "0-1", "1-3", "3-5", "5-7", "7+"]

    if saved_role not in role_choices:
        saved_role = "All Roles"
    if saved_location not in location_choices:
        saved_location = "All Locations"
    if saved_experience not in experience_choices:
        saved_experience = "All Levels"

    with st.form("market_insights_filter_form", clear_on_submit=False):
        col1, col2, col3, col4 = st.columns([2.3, 2.0, 1.5, 1.0])

        with col1:
            role_input = st.selectbox(
                "Job Role",
                role_choices,
                index=role_choices.index(saved_role),
                help="Choose a role available in the dataset.",
            )

        with col2:
            location_input = st.selectbox(
                "Location",
                location_choices,
                index=location_choices.index(saved_location),
                help="Choose a location available in the dataset.",
            )

        with col3:
            experience_input = st.selectbox(
                "Experience Level",
                experience_choices,
                index=experience_choices.index(saved_experience),
            )

        with col4:
            st.write("")
            submitted = st.form_submit_button(
                "Apply Filters", type="primary", use_container_width=True
            )

    if submitted:
        st.session_state.market_filters_native = {
            "job_role": None if role_input == "All Roles" else role_input,
            "location": (
                None if location_input == "All Locations" else location_input
            ),
            "experience_level": (
                "All" if experience_input == "All Levels" else experience_input
            ),
        }
        st.session_state.market_filters_submitted = True

    return (
        st.session_state.market_filters_native,
        st.session_state.market_filters_submitted,
    )


def render_active_filters(filters):
    active = []
    if filters.get("job_role"):
        active.append(f"Role: {filters['job_role']}")
    if filters.get("location"):
        active.append(f"Location: {filters['location']}")
    if filters.get("experience_level") != "All":
        active.append(f"Experience: {filters['experience_level']} years")

    if active:
        st.caption("Active filters: " + "  •  ".join(active))
    else:
        st.caption("Showing all available job postings")


# ============================================================
# SUMMARY CARDS
# ============================================================


def render_summary_cards(jobs):
    total_jobs = calculate_total_jobs(jobs)
    remote_pct = calculate_remote_percentage(jobs)
    salary_range = calculate_salary_range(jobs)
    top_role = calculate_top_hiring_role(jobs)

    cols = st.columns(4, gap="medium")
    metrics = [
        ("💼 Total Job Postings", f"{total_jobs:,}", "Matching job postings"),
        ("🏠 Remote Jobs", f"{remote_pct:.1f}%", "Share marked as remote"),
        ("💰 Salary Range", salary_display(salary_range), "Disclosed salary boundaries"),
        ("🏆 Top Hiring Role", safe_value(top_role), "Most frequently posted title"),
    ]

    for col, (label, value, help_text) in zip(cols, metrics):
        with col:
            render_metric_card(label, value, help_text)


# ============================================================
# CHARTS
# ============================================================


def render_salary_by_experience(data):
    st.markdown("#### 💰 Salary Range by Experience")
    if data is None or data.empty:
        st.info("Salary information is not available for these filters.")
        return
    make_salary_range_chart(data, "Experience", height=260)


def render_top_locations(data):
    st.markdown("#### 📍 Top Locations by Salary Range")
    if data is None or data.empty:
        st.info("There is not enough disclosed salary data across locations.")
        return
    make_salary_range_chart(data, "Location", height=260)


def render_top_skills(data):
    st.markdown("#### 🛠️ Top In-Demand Skills")
    if data is None or data.empty:
        st.info("No skill-demand information is available for these filters.")
        return

    chart_data = data.copy()
    chart_data["Demand"] = pd.to_numeric(chart_data["Demand"], errors="coerce")
    chart_data = chart_data.dropna(subset=["Demand"]).nlargest(10, "Demand")
    if chart_data.empty:
        st.info("No valid skill counts are available.")
        return

    chart = (
        alt.Chart(chart_data)
        .mark_bar(color="#2878D0", cornerRadiusEnd=4)
        .encode(
            x=alt.X("Demand:Q", title="Number of job postings"),
            y=alt.Y("Skill:N", sort="-x", title=None, axis=alt.Axis(labelLimit=150)),
            tooltip=["Skill", alt.Tooltip("Demand:Q", format=",")],
        )
        .properties(height=300)
    )
    st.altair_chart(chart, use_container_width=True)
    st.caption("Demand represents the number of postings containing each skill.")


def render_industry_distribution(data):
    st.markdown("#### 🏢 Job Distribution by Industry")
    if data is None or data.empty:
        st.info("Industry information is not available for these filters.")
        return

    chart_data = data.copy()
    chart_data["Jobs"] = pd.to_numeric(chart_data["Jobs"], errors="coerce")
    chart_data = chart_data.dropna(subset=["Jobs"])
    if chart_data.empty:
        st.info("No valid industry counts are available.")
        return

    chart = (
        alt.Chart(chart_data)
        .mark_arc(innerRadius=65, outerRadius=115)
        .encode(
            theta=alt.Theta("Jobs:Q", stack=True),
            color=alt.Color("Industry:N", title="Industry"),
            tooltip=["Industry", alt.Tooltip("Jobs:Q", format=",")],
        )
        .properties(height=300)
    )
    st.altair_chart(chart, use_container_width=True)
    st.caption(
        "Industry categories are inferred from job titles, descriptions and skills; "
        "the source dataset has no explicit industry column."
    )


def render_top_roles(data):
    st.markdown("#### 💼 Top Job Roles by Salary Range")
    if data is None or data.empty:
        st.info("There is not enough disclosed salary data for role-level comparison.")
        return
    make_salary_range_chart(data, "Job Role", height=300)


def render_market_changes(jobs):
    job_change = calculate_six_month_change(jobs)
    remote_change = calculate_remote_six_month_change(jobs)
    if job_change is None and remote_change is None:
        return

    st.divider()
    st.markdown("#### 📈 Market Changes")
    col1, col2 = st.columns(2)
    with col1:
        if job_change is None:
            st.caption("Six-month job-posting comparison is not available.")
        else:
            st.metric("Six-Month Job Posting Change", f"{job_change:+.1f}%")
    with col2:
        if remote_change is None:
            st.caption("Six-month remote-job comparison is not available.")
        else:
            st.metric("Six-Month Remote Share Change", f"{remote_change:+.1f} percentage points")


# ============================================================
# MAIN PAGE
# ============================================================


def render_job_market_insights():
    st.title("📊 Job Market Insights")
    st.caption(
        "Explore job demand, salary ranges, in-demand skills, locations, "
        "experience levels and industry distribution."
    )

    try:
        jobs = get_market_dataset()
    except FileNotFoundError as error:
        st.error(str(error))
        return
    except Exception as error:
        st.error("Unable to load the job-market dataset.")
        st.exception(error)
        return

    if jobs.empty:
        st.warning("The processed job-market dataset contains no postings.")
        return

    filters, filters_submitted = render_filters(jobs)

    # Do not display previous or unfiltered results before the user
    # explicitly submits the filter form.
    if not filters_submitted:
        st.info("Select your filters and click **Apply Filters** to generate job-market insights.")
        return

    render_active_filters(filters)

    role = filters.get("job_role")
    location = filters.get("location")
    experience = filters.get("experience_level", "All")

    # KPI cards follow every active filter.
    kpi_jobs = filter_jobs(
        jobs, job_role=role, location=location, experience_level=experience
    )

    if kpi_jobs.empty:
        st.warning(
            "No job postings match the selected filters. Clear one or more filters "
            "or try a broader search."
        )
        return

    # Chart datasets intentionally relax only the filter that would make
    # that comparison meaningless (e.g. location comparison ignores location).
    experience_jobs = filter_jobs(
        jobs, job_role=role, location=location, experience_level="All"
    )
    location_jobs = filter_jobs(
        jobs, job_role=role, location=None, experience_level=experience
    )
    skills_industry_jobs = filter_jobs(
        jobs, job_role=role, location=location, experience_level="All"
    )
    role_jobs = filter_jobs(
        jobs, job_role=None, location=location, experience_level=experience
    )

    render_summary_cards(kpi_jobs)
    st.divider()

    row1_left, row1_right = st.columns(2, gap="large")
    with row1_left:
        render_salary_by_experience(
            calculate_salary_by_experience(experience_jobs)
        )
    with row1_right:
        render_top_locations(
            calculate_top_locations_by_salary(location_jobs, top_n=5)
        )

    row2_left, row2_right = st.columns(2, gap="large")
    with row2_left:
        render_top_skills(calculate_top_skills(skills_industry_jobs, top_n=10))
    with row2_right:
        render_industry_distribution(
            calculate_industry_distribution(skills_industry_jobs)
        )

    render_top_roles(
        calculate_top_roles_by_salary(role_jobs, top_n=6)
    )
    render_market_changes(experience_jobs)

    st.divider()
    st.caption(
        "Salary analysis uses disclosed salary information from the processed dataset. "
        "Salary ranges are shown instead of a single fixed salary value. Industry "
        "categories are inferred because the source dataset has no explicit industry field."
    )
