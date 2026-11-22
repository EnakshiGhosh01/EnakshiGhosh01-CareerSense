import re
from pathlib import Path

import pandas as pd


# ==========================================================
# PATHS
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATASET_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "jobs_cleaned.csv"
)


# ==========================================================
# DATA LOADING
# ==========================================================

def load_market_data():
    """
    Load the processed job-market dataset.
    """

    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found at: {DATASET_PATH}"
        )

    jobs = pd.read_csv(
        DATASET_PATH
    )

    return jobs


# ==========================================================
# DATA PREPARATION
# ==========================================================

def prepare_market_data(jobs):
    """
    Prepare columns required for market analytics.
    """

    jobs = jobs.copy()

    # ------------------------------------------------------
    # Salary columns
    # ------------------------------------------------------

    jobs["minimumSalary"] = pd.to_numeric(
        jobs["minimumSalary"],
        errors="coerce"
    )

    jobs["maximumSalary"] = pd.to_numeric(
        jobs["maximumSalary"],
        errors="coerce"
    )

    # Remove invalid negative salaries
    jobs.loc[
        jobs["minimumSalary"] < 0,
        "minimumSalary"
    ] = pd.NA

    jobs.loc[
        jobs["maximumSalary"] < 0,
        "maximumSalary"
    ] = pd.NA

    # ------------------------------------------------------
    # Salary midpoint
    #
    # Used internally for calculations where a single
    # numeric value is required.
    # ------------------------------------------------------

    jobs["salary_midpoint"] = (
        jobs["minimumSalary"]
        + jobs["maximumSalary"]
    ) / 2

    # If only minimum salary exists
    jobs.loc[
        jobs["salary_midpoint"].isna()
        & jobs["minimumSalary"].notna(),
        "salary_midpoint"
    ] = jobs["minimumSalary"]

    # If only maximum salary exists
    jobs.loc[
        jobs["salary_midpoint"].isna()
        & jobs["maximumSalary"].notna(),
        "salary_midpoint"
    ] = jobs["maximumSalary"]

    # ------------------------------------------------------
    # Date
    # ------------------------------------------------------

    jobs["job_date"] = pd.to_datetime(
        jobs["jobUploaded"],
        format="mixed",
        errors="coerce"
    )

    # ------------------------------------------------------
    # Experience
    # ------------------------------------------------------

    jobs["minimumExperience"] = pd.to_numeric(
        jobs["minimumExperience"],
        errors="coerce"
    )

    jobs["maximumExperience"] = pd.to_numeric(
        jobs["maximumExperience"],
        errors="coerce"
    )

    jobs["experience_midpoint"] = (
        jobs["minimumExperience"]
        + jobs["maximumExperience"]
    ) / 2

    # If only minimum experience exists
    jobs.loc[
        jobs["experience_midpoint"].isna()
        & jobs["minimumExperience"].notna(),
        "experience_midpoint"
    ] = jobs["minimumExperience"]

    # If only maximum experience exists
    jobs.loc[
        jobs["experience_midpoint"].isna()
        & jobs["maximumExperience"].notna(),
        "experience_midpoint"
    ] = jobs["maximumExperience"]

    return jobs


# ==========================================================
# FILTERING
# ==========================================================

def filter_jobs(
    jobs,
    job_role=None,
    location=None,
    experience_level=None
):
    """
    Filter postings using values selected from the dataset.

    The dashboard's display labels (All Roles, All Locations,
    All Levels) are treated as no filter.
    """
    filtered = jobs.copy()

    # Normalize dashboard sentinel labels.
    role_value = str(job_role).strip() if job_role is not None else ""
    location_value = str(location).strip() if location is not None else ""
    experience_value = (
        str(experience_level).strip()
        if experience_level is not None
        else ""
    )

    if role_value.casefold() in {
        "", "none", "all", "all roles", "all jobs", "any role"
    }:
        role_value = None

    if location_value.casefold() in {
        "", "none", "all", "all locations", "any location"
    }:
        location_value = None

    if experience_value.casefold() in {
        "", "none", "all", "all levels", "any"
    }:
        experience_value = None

    # Job role: literal, case-insensitive matching.
    if role_value:
        title_text = (
            filtered["title"]
            .fillna("")
            .astype(str)
            .str.strip()
        )
        filtered = filtered[
            title_text.str.contains(
                role_value,
                case=False,
                regex=False,
                na=False
            )
        ]

    # Location: literal, case-insensitive matching.
    if location_value:
        location_text = (
            filtered["location"]
            .fillna("")
            .astype(str)
            .str.strip()
        )
        filtered = filtered[
            location_text.str.contains(
                location_value,
                case=False,
                regex=False,
                na=False
            )
        ]

    # Experience ranges are matched by interval overlap.
    if experience_value:
        experience_ranges = {
            "0-1": (0, 1),
            "1-3": (1, 3),
            "3-5": (3, 5),
            "5-7": (5, 7),
            "7+": (7, float("inf")),
        }

        if experience_value in experience_ranges:
            lower, upper = experience_ranges[experience_value]

            min_exp = pd.to_numeric(
                filtered["minimumExperience"], errors="coerce"
            )
            max_exp = pd.to_numeric(
                filtered["maximumExperience"], errors="coerce"
            )

            # Use the known boundary when one side is missing.
            # Rows with neither boundary are not treated as matching
            # every experience band.
            overlaps = (
                min_exp.notna()
                & (min_exp <= upper)
                & (
                    max_exp.isna()
                    | (max_exp >= lower)
                )
            ) | (
                min_exp.isna()
                & max_exp.notna()
                & (max_exp >= lower)
                & (max_exp <= upper)
            )

            filtered = filtered[overlaps]

    return filtered


# ==========================================================
# FILTER OPTIONS
# ==========================================================

def get_job_role_options(jobs):
    """
    Return available job-role filter options.
    """

    roles = (
        jobs["title"]
        .dropna()
        .astype(str)
        .str.strip()
    )

    roles = sorted(
        roles[
            roles != ""
        ].unique()
    )

    return [
        "All"
    ] + roles


def get_location_options(jobs):
    """
    Return available location filter options.
    """

    locations = (
        jobs["location"]
        .dropna()
        .astype(str)
        .str.strip()
    )

    locations = sorted(
        locations[
            locations != ""
        ].unique()
    )

    return [
        "All"
    ] + locations


def get_experience_options():
    """
    Return available experience-level options.
    """

    return [
        "All",
        "0-1",
        "1-3",
        "3-5",
        "5-7",
        "7+"
    ]


# ==========================================================
# BASIC MARKET METRICS
# ==========================================================

def calculate_total_jobs(jobs):
    """
    Calculate total number of job postings.
    """

    return len(jobs)


def calculate_remote_percentage(jobs):
    """
    Calculate percentage of remote jobs.
    """

    if len(jobs) == 0:
        return 0.0

    location_text = (
        jobs["location"]
        .fillna("")
        .astype(str)
        .str.lower()
    )

    remote_mask = location_text.str.contains(
        r"\bremote\b",
        regex=True,
        na=False
    )

    return (
        remote_mask.mean()
        * 100
    )


# ==========================================================
# SALARY RANGE HELPERS
# ==========================================================

def salary_to_lpa(value):
    """
    Convert salary value into LPA.

    The dataset salary fields are represented in
    Lacs/LPA for the processed dataset.
    """

    if pd.isna(value):
        return None

    try:
        value = float(value)
    except (
        TypeError,
        ValueError
    ):
        return None

    return value


def format_salary_range(
    minimum_salary,
    maximum_salary
):
    """
    Convert minimum and maximum salary into a
    display-friendly LPA range.
    """

    minimum_salary = salary_to_lpa(
        minimum_salary
    )

    maximum_salary = salary_to_lpa(
        maximum_salary
    )

    if (
        minimum_salary is None
        and maximum_salary is None
    ):
        return "Not disclosed"

    if minimum_salary is None:
        return (
            f"Up to ₹{maximum_salary:.1f} LPA"
        )

    if maximum_salary is None:
        return (
            f"From ₹{minimum_salary:.1f} LPA"
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
# OVERALL SALARY RANGE
# ==========================================================

def calculate_salary_range(jobs):
    """
    Calculate the overall salary range from the
    minimumSalary and maximumSalary columns.

    Returns:
        {
            "minimum": ...,
            "maximum": ...,
            "display": "₹X.X – ₹Y.Y LPA"
        }
    """

    salary_jobs = jobs[
        jobs["minimumSalary"].notna()
        |
        jobs["maximumSalary"].notna()
    ].copy()

    if salary_jobs.empty:
        return {
            "minimum": None,
            "maximum": None,
            "display": "Not disclosed"
        }

    minimum_values = (
        salary_jobs["minimumSalary"]
        .dropna()
    )

    maximum_values = (
        salary_jobs["maximumSalary"]
        .dropna()
    )

    minimum_salary = (
        minimum_values.min()
        if not minimum_values.empty
        else None
    )

    maximum_salary = (
        maximum_values.max()
        if not maximum_values.empty
        else None
    )

    return {
        "minimum": minimum_salary,
        "maximum": maximum_salary,
        "display": format_salary_range(
            minimum_salary,
            maximum_salary
        )
    }


# ==========================================================
# SALARY BY EXPERIENCE
# ==========================================================

def calculate_salary_by_experience(jobs):
    """
    Calculate salary ranges for each experience group.

    The dashboard receives minimum and maximum salary
    values instead of one fixed salary amount.
    """

    experience_groups = [
        ("0-1", 0, 1),
        ("1-3", 1, 3),
        ("3-5", 3, 5),
        ("5-7", 5, 7),
        ("7+", 7, None)
    ]

    results = []

    for label, minimum_exp, maximum_exp in experience_groups:

        if maximum_exp is None:

            group = jobs[
                jobs["maximumExperience"]
                >= minimum_exp
            ]

        else:

            group = jobs[
                (
                    jobs["maximumExperience"]
                    >= minimum_exp
                )
                &
                (
                    jobs["minimumExperience"]
                    <= maximum_exp
                )
            ]

        salary_group = group[
            group["minimumSalary"].notna()
            |
            group["maximumSalary"].notna()
        ]

        if salary_group.empty:

            results.append(
                {
                    "Experience": label,
                    "Minimum Salary": None,
                    "Maximum Salary": None,
                    "Salary Range": "Not disclosed"
                }
            )

            continue

        minimum_values = (
            salary_group["minimumSalary"]
            .dropna()
        )

        maximum_values = (
            salary_group["maximumSalary"]
            .dropna()
        )

        minimum_salary = (
            minimum_values.min()
            if not minimum_values.empty
            else None
        )

        maximum_salary = (
            maximum_values.max()
            if not maximum_values.empty
            else None
        )

        results.append(
            {
                "Experience": label,
                "Minimum Salary": minimum_salary,
                "Maximum Salary": maximum_salary,
                "Salary Range": format_salary_range(
                    minimum_salary,
                    maximum_salary
                )
            }
        )

    return pd.DataFrame(
        results
    )


# ==========================================================
# TOP LOCATIONS BY SALARY
# ==========================================================

def calculate_top_locations_by_salary(
    jobs,
    top_n=5,
    minimum_jobs=10
):
    """
    Calculate salary ranges by location.

    Locations with fewer than minimum_jobs postings
    are excluded to avoid misleading results from
    very small samples.
    """

    salary_jobs = jobs[
        jobs["minimumSalary"].notna()
        |
        jobs["maximumSalary"].notna()
    ].copy()

    if salary_jobs.empty:
        return pd.DataFrame(
            columns=[
                "Location",
                "Minimum Salary",
                "Maximum Salary",
                "Salary Range",
                "Job Count"
            ]
        )

    grouped = (
        salary_jobs
        .groupby("location")
        .agg(
            Minimum_Salary=(
                "minimumSalary",
                "min"
            ),
            Maximum_Salary=(
                "maximumSalary",
                "max"
            ),
            Job_Count=(
                "title",
                "count"
            )
        )
        .reset_index()
    )

    grouped = grouped[
        grouped["Job_Count"]
        >= minimum_jobs
    ]

    grouped = grouped.sort_values(
        by="Maximum_Salary",
        ascending=False
    )

    grouped = grouped.head(
        top_n
    )

    grouped["Salary Range"] = grouped.apply(
        lambda row: format_salary_range(
            row["Minimum_Salary"],
            row["Maximum_Salary"]
        ),
        axis=1
    )

    grouped = grouped.rename(
        columns={
            "Minimum_Salary": "Minimum Salary",
            "Maximum_Salary": "Maximum Salary",
            "Job_Count": "Job Count"
        }
    )

    return grouped[
        [
            "location",
            "Minimum Salary",
            "Maximum Salary",
            "Salary Range",
            "Job Count"
        ]
    ].rename(
        columns={
            "location": "Location"
        }
    )


# ==========================================================
# TOP IN-DEMAND SKILLS
# ==========================================================

def calculate_top_skills(
    jobs,
    top_n=10
):
    """
    Calculate the most frequently occurring skills
    in tagsAndSkills.
    """

    skill_counts = {}

    for skills in jobs["tagsAndSkills"].dropna():

        skills_text = str(
            skills
        )

        split_skills = re.split(
            r"[,;|]",
            skills_text
        )

        for skill in split_skills:

            skill = skill.strip()

            if not skill:
                continue

            skill_key = skill.lower()

            if skill_key not in skill_counts:
                skill_counts[skill_key] = {
                    "display": skill,
                    "count": 0
                }

            skill_counts[
                skill_key
            ]["count"] += 1

    results = []

    for skill_data in skill_counts.values():

        results.append(
            {
                "Skill": skill_data["display"],
                "Demand": skill_data["count"]
            }
        )

    result_df = pd.DataFrame(
        results
    )

    if result_df.empty:
        return result_df

    result_df = result_df.sort_values(
        by="Demand",
        ascending=False
    )

    return result_df.head(
        top_n
    ).reset_index(
        drop=True
    )


# ==========================================================
# INDUSTRY CLASSIFICATION
# ==========================================================

def classify_industry(row):
    """
    Derive a broad industry category from available
    job information.

    The original dataset does not contain an explicit
    industry column.
    """

    title = str(
        row.get("title", "")
    ).lower()

    description = str(
        row.get("jobDescription", "")
    ).lower()

    skills = str(
        row.get("tagsAndSkills", "")
    ).lower()

    text = (
        title
        + " "
        + description
        + " "
        + skills
    )

    # ------------------------------------------------------
    # Finance
    # ------------------------------------------------------

    finance_keywords = [
        "bank",
        "banking",
        "finance",
        "financial",
        "fintech",
        "insurance",
        "accounting",
        "investment",
        "credit",
        "loan",
        "wealth",
        "risk analyst",
        "financial analyst"
    ]

    if any(
        keyword in text
        for keyword in finance_keywords
    ):
        return "Finance"

    # ------------------------------------------------------
    # Healthcare
    # ------------------------------------------------------

    healthcare_keywords = [
        "hospital",
        "healthcare",
        "health care",
        "medical",
        "doctor",
        "physician",
        "nurse",
        "clinical",
        "pharma",
        "pharmaceutical",
        "oncologist",
        "radiologist",
        "diagnostic"
    ]

    if any(
        keyword in text
        for keyword in healthcare_keywords
    ):
        return "Healthcare"

    # ------------------------------------------------------
    # E-commerce
    # ------------------------------------------------------

    ecommerce_keywords = [
        "ecommerce",
        "e-commerce",
        "online shopping",
        "marketplace",
        "retail",
        "digital commerce"
    ]

    if any(
        keyword in text
        for keyword in ecommerce_keywords
    ):
        return "E-commerce"

    # ------------------------------------------------------
    # IT Services
    # ------------------------------------------------------

    it_keywords = [
        "software",
        "developer",
        "development",
        "programmer",
        "technology",
        "it services",
        "information technology",
        "application developer",
        "web developer",
        "java",
        "python",
        "cloud",
        "devops",
        "database",
        "network",
        "cybersecurity"
    ]

    if any(
        keyword in text
        for keyword in it_keywords
    ):
        return "IT Services"

    # ------------------------------------------------------
    # Product
    # ------------------------------------------------------

    product_keywords = [
        "product manager",
        "product management",
        "product development",
        "product engineer",
        "product company"
    ]

    if any(
        keyword in text
        for keyword in product_keywords
    ):
        return "Product"

    return "Others"


# ==========================================================
# INDUSTRY DISTRIBUTION
# ==========================================================

def calculate_industry_distribution(jobs):
    """
    Calculate the distribution of derived industries.
    """

    industry_jobs = jobs.copy()

    industry_jobs["Industry"] = industry_jobs.apply(
        classify_industry,
        axis=1
    )

    result = (
        industry_jobs[
            "Industry"
        ]
        .value_counts()
        .reset_index()
    )

    result.columns = [
        "Industry",
        "Jobs"
    ]

    return result


# ==========================================================
# TOP JOB ROLES BY SALARY
# ==========================================================

def calculate_top_roles_by_salary(
    jobs,
    top_n=6,
    minimum_jobs=10
):
    """
    Calculate salary ranges for the highest-paying
    job roles.

    Roles with fewer than minimum_jobs postings
    are excluded to reduce the impact of outliers.
    """

    salary_jobs = jobs[
        jobs["minimumSalary"].notna()
        |
        jobs["maximumSalary"].notna()
    ].copy()

    if salary_jobs.empty:
        return pd.DataFrame(
            columns=[
                "Job Role",
                "Minimum Salary",
                "Maximum Salary",
                "Salary Range",
                "Job Count"
            ]
        )

    grouped = (
        salary_jobs
        .groupby("title")
        .agg(
            Minimum_Salary=(
                "minimumSalary",
                "min"
            ),
            Maximum_Salary=(
                "maximumSalary",
                "max"
            ),
            Job_Count=(
                "jobId",
                "count"
            )
        )
        .reset_index()
    )

    grouped = grouped[
        grouped["Job_Count"]
        >= minimum_jobs
    ]

    grouped = grouped.sort_values(
        by="Maximum_Salary",
        ascending=False
    )

    grouped = grouped.head(
        top_n
    )

    grouped["Salary Range"] = grouped.apply(
        lambda row: format_salary_range(
            row["Minimum_Salary"],
            row["Maximum_Salary"]
        ),
        axis=1
    )

    grouped = grouped.rename(
        columns={
            "title": "Job Role",
            "Minimum_Salary": "Minimum Salary",
            "Maximum_Salary": "Maximum Salary",
            "Job_Count": "Job Count"
        }
    )

    return grouped[
        [
            "Job Role",
            "Minimum Salary",
            "Maximum Salary",
            "Salary Range",
            "Job Count"
        ]
    ]


# ==========================================================
# TOP HIRING ROLE
# ==========================================================

def calculate_top_hiring_role(jobs):
    """
    Find the most frequently occurring job title.
    """

    titles = (
        jobs["title"]
        .dropna()
        .astype(str)
        .str.strip()
    )

    titles = titles[
        titles != ""
    ]

    if titles.empty:
        return "Not available"

    return titles.value_counts().index[0]


# ==========================================================
# SIX-MONTH JOB CHANGE
# ==========================================================

def calculate_six_month_change(jobs):
    """
    Compare job-posting volume between the current
    six-month period and the preceding six-month period.

    Returns None when either period has no usable data.
    """

    dated_jobs = jobs[
        jobs["job_date"].notna()
    ].copy()

    if dated_jobs.empty:
        return None

    latest_date = dated_jobs[
        "job_date"
    ].max()

    current_start = (
        latest_date
        - pd.DateOffset(months=6)
    )

    previous_start = (
        latest_date
        - pd.DateOffset(months=12)
    )

    current_jobs = dated_jobs[
        (
            dated_jobs["job_date"]
            > current_start
        )
        &
        (
            dated_jobs["job_date"]
            <= latest_date
        )
    ]

    previous_jobs = dated_jobs[
        (
            dated_jobs["job_date"]
            > previous_start
        )
        &
        (
            dated_jobs["job_date"]
            <= current_start
        )
    ]

    current_count = len(
        current_jobs
    )

    previous_count = len(
        previous_jobs
    )

    if previous_count == 0:
        return None

    change = (
        (
            current_count
            - previous_count
        )
        / previous_count
    ) * 100

    return change


# ==========================================================
# SIX-MONTH REMOTE CHANGE
# ==========================================================

def calculate_remote_six_month_change(jobs):
    """
    Compare remote-job percentage between the current
    and preceding six-month periods.

    Returns None when either period has no usable data.
    """

    dated_jobs = jobs[
        jobs["job_date"].notna()
    ].copy()

    if dated_jobs.empty:
        return None

    latest_date = dated_jobs[
        "job_date"
    ].max()

    current_start = (
        latest_date
        - pd.DateOffset(months=6)
    )

    previous_start = (
        latest_date
        - pd.DateOffset(months=12)
    )

    current_jobs = dated_jobs[
        (
            dated_jobs["job_date"]
            > current_start
        )
        &
        (
            dated_jobs["job_date"]
            <= latest_date
        )
    ]

    previous_jobs = dated_jobs[
        (
            dated_jobs["job_date"]
            > previous_start
        )
        &
        (
            dated_jobs["job_date"]
            <= current_start
        )
    ]

    if (
        current_jobs.empty
        or previous_jobs.empty
    ):
        return None

    current_remote = (
        current_jobs["location"]
        .fillna("")
        .astype(str)
        .str.lower()
        .str.contains(
            r"\bremote\b",
            regex=True,
            na=False
        )
        .mean()
        * 100
    )

    previous_remote = (
        previous_jobs["location"]
        .fillna("")
        .astype(str)
        .str.lower()
        .str.contains(
            r"\bremote\b",
            regex=True,
            na=False
        )
        .mean()
        * 100
    )

    return (
        current_remote
        - previous_remote
    )


# ==========================================================
# MAIN MARKET INSIGHTS FUNCTION
# ==========================================================

def generate_market_insights(
    jobs,
    job_role=None,
    location=None,
    experience_level=None
):
    """
    Generate filtered KPI metrics and comparison datasets.

    KPI values use all selected filters. Comparison charts relax the
    dimension being compared so that the charts remain meaningful.
    """
    prepared_jobs = prepare_market_data(jobs)

    # All selected filters: used by the KPI cards.
    filtered_jobs = filter_jobs(
        prepared_jobs,
        job_role=job_role,
        location=location,
        experience_level=experience_level
    )

    # Salary by experience: keep role/location, relax experience.
    experience_jobs = filter_jobs(
        prepared_jobs,
        job_role=job_role,
        location=location,
        experience_level=None
    )

    # Locations comparison: keep role/experience, relax location.
    location_jobs = filter_jobs(
        prepared_jobs,
        job_role=job_role,
        location=None,
        experience_level=experience_level
    )

    # Skills and industry: keep role/location, relax experience.
    skills_industry_jobs = experience_jobs

    # Role comparison: keep location/experience, relax role.
    role_jobs = filter_jobs(
        prepared_jobs,
        job_role=None,
        location=location,
        experience_level=experience_level
    )

    insights = {
        "jobs": filtered_jobs,
        "total_jobs": calculate_total_jobs(filtered_jobs),
        "remote_percentage": calculate_remote_percentage(filtered_jobs),
        "salary_range": calculate_salary_range(filtered_jobs),
        "top_hiring_role": calculate_top_hiring_role(filtered_jobs),

        "salary_by_experience": calculate_salary_by_experience(
            experience_jobs
        ),
        "top_locations_by_salary": calculate_top_locations_by_salary(
            location_jobs
        ),
        "top_skills": calculate_top_skills(
            skills_industry_jobs
        ),
        "industry_distribution": calculate_industry_distribution(
            skills_industry_jobs
        ),
        "top_roles_by_salary": calculate_top_roles_by_salary(
            role_jobs
        ),

        "six_month_job_change": calculate_six_month_change(
            experience_jobs
        ),
        "six_month_remote_change": calculate_remote_six_month_change(
            experience_jobs
        )
    }

    return insights


# ==========================================================
# TEST
# ==========================================================

if __name__ == "__main__":

    print(
        "========================================"
    )

    print(
        "   CAREERSENSE MARKET INSIGHTS TEST"
    )

    print(
        "========================================"
    )

    jobs = load_market_data()

    print(
        f"\nJobs loaded: {len(jobs):,}"
    )

    jobs = prepare_market_data(
        jobs
    )

    # ------------------------------------------------------
    # Basic metrics
    # ------------------------------------------------------

    print(
        f"\nTotal Jobs: "
        f"{calculate_total_jobs(jobs)}"
    )

    print(
        f"Remote Jobs: "
        f"{calculate_remote_percentage(jobs):.1f}%"
    )

    # ------------------------------------------------------
    # Salary range
    # ------------------------------------------------------

    salary_range = calculate_salary_range(
        jobs
    )

    print(
        f"Salary Range: "
        f"{salary_range['display']}"
    )

    # ------------------------------------------------------
    # Top hiring role
    # ------------------------------------------------------

    print(
        f"Top Hiring Role: "
        f"{calculate_top_hiring_role(jobs)}"
    )

    # ------------------------------------------------------
    # Salary by experience
    # ------------------------------------------------------

    print(
        "\nSalary by Experience:"
    )

    print(
        calculate_salary_by_experience(
            jobs
        )[
            [
                "Experience",
                "Salary Range"
            ]
        ].to_string(
            index=False
        )
    )

    # ------------------------------------------------------
    # Top locations
    # ------------------------------------------------------

    print(
        "\nTop Locations by Salary:"
    )

    print(
        calculate_top_locations_by_salary(
            jobs
        )[
            [
                "Location",
                "Salary Range",
                "Job Count"
            ]
        ].to_string(
            index=False
        )
    )

    # ------------------------------------------------------
    # Top skills
    # ------------------------------------------------------

    print(
        "\nTop Skills:"
    )

    print(
        calculate_top_skills(
            jobs
        ).to_string(
            index=False
        )
    )

    # ------------------------------------------------------
    # Industry
    # ------------------------------------------------------

    print(
        "\nIndustry Distribution:"
    )

    print(
        calculate_industry_distribution(
            jobs
        ).to_string(
            index=False
        )
    )

    # ------------------------------------------------------
    # Top roles
    # ------------------------------------------------------

    print(
        "\nTop Roles by Salary:"
    )

    print(
        calculate_top_roles_by_salary(
            jobs
        )[
            [
                "Job Role",
                "Salary Range",
                "Job Count"
            ]
        ].to_string(
            index=False
        )
    )

    # ------------------------------------------------------
    # Six-month changes
    # ------------------------------------------------------

    six_month_change = (
        calculate_six_month_change(
            jobs
        )
    )

    remote_change = (
        calculate_remote_six_month_change(
            jobs
        )
    )

    print(
        f"\nSix-Month Job Change: "
        f"{six_month_change}"
    )

    print(
        f"Six-Month Remote Change: "
        f"{remote_change}"
    )