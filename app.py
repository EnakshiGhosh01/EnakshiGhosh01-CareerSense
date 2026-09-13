import streamlit as st


# Page configuration
st.set_page_config(
    page_title="CareerSense",
    page_icon="💼",
    layout="wide"
)


# Application title
st.title("💼 CareerSense")
st.write("AI-Powered Career Intelligence and Job Matching System")

st.divider()


# Main application sections
tab1, tab2 = st.tabs([
    "📊 My Career Analysis",
    "💼 Job Market Insights"
])


# Tab 1: Personal Career Analysis
with tab1:
    st.header("My Career Analysis")

    st.write(
        "Upload your resume to analyze your skills, experience, "
        "education, and job compatibility."
    )

    uploaded_resume = st.file_uploader(
        "Upload your resume",
        type=["pdf", "docx"]
    )

    if uploaded_resume is not None:
        st.success(f"Resume uploaded: {uploaded_resume.name}")

    st.subheader("Career Analysis")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Resume Score", "—")

    with col2:
        st.metric("Matching Jobs", "—")

    with col3:
        st.metric("Skill Gaps", "—")

    st.info(
        "Resume analysis, skill extraction, job matching, "
        "and skill-gap analysis will be added here."
    )


# Tab 2: Job Market Insights
with tab2:
    st.header("Job Market Insights")

    st.write(
        "Explore overall job-market trends, salary information, "
        "skill demand, locations, and industries."
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Jobs", "—")

    with col2:
        st.metric("Average Salary", "—")

    with col3:
        st.metric("Top Location", "—")

    with col4:
        st.metric("Top Skill", "—")

    st.info(
        "Job-market analytics and Power BI insights "
        "will be connected here."
    )