import pandas as pd

from matching.similarity import calculate_text_similarity
from resume.skill_extractor import (
    extract_job_skills,
    normalize_skill,
    RELATED_SKILLS
)


# ==========================================================
# CONFIGURATION
# ==========================================================

DATASET_PATH = "data/processed/jobs_cleaned.csv"

# Final matching weights
SKILL_WEIGHT = 0.50
EXPERIENCE_WEIGHT = 0.25
EDUCATION_WEIGHT = 0.10
ROLE_WEIGHT = 0.15

# Related skill receives partial credit
RELATED_SKILL_CREDIT = 0.50

# Number of jobs on which expensive TF-IDF similarity
# will be calculated.
CANDIDATE_LIMIT = 500


# ==========================================================
# LOAD JOB DATA
# ==========================================================

def load_jobs():
    """
    Load the cleaned job dataset.
    """
    return pd.read_csv(DATASET_PATH)


# ==========================================================
# SKILL MATCHING
# ==========================================================

def calculate_skill_match(resume_skills, job_skills):
    """
    Compare resume skills against job-required skills.

    Exact match:
        1.0 credit

    Related match:
        0.5 credit

    Missing:
        0.0 credit
    """

    resume_set = {
        normalize_skill(skill)
        for skill in resume_skills
        if normalize_skill(skill)
    }

    job_set = {
        normalize_skill(skill)
        for skill in job_skills
        if normalize_skill(skill)
    }

    if not job_set:
        return {
            "score": 0.0,
            "exact_matches": [],
            "related_matches": [],
            "matched_skills": [],
            "missing_skills": []
        }

    exact_matches = []
    related_matches = []
    matched_skills = []

    matched_job_skills = set()
    used_resume_skills = set()

    # ======================================================
    # EXACT MATCH
    # ======================================================

    for job_skill in sorted(job_set):

        if job_skill in resume_set:

            exact_matches.append(
                f"{job_skill} (exact)"
            )

            matched_skills.append(
                f"{job_skill} (exact)"
            )

            matched_job_skills.add(job_skill)
            used_resume_skills.add(job_skill)

    # ======================================================
    # RELATED MATCH
    # ======================================================

    for job_skill in sorted(job_set):

        if job_skill in matched_job_skills:
            continue

        for resume_skill in sorted(resume_set):

            if resume_skill in used_resume_skills:
                continue

            related = False

            if job_skill in RELATED_SKILLS.get(
                resume_skill,
                set()
            ):
                related = True

            elif resume_skill in RELATED_SKILLS.get(
                job_skill,
                set()
            ):
                related = True

            if related:

                match_text = (
                    f"{resume_skill} -> "
                    f"{job_skill} (related)"
                )

                related_matches.append(match_text)
                matched_skills.append(match_text)

                matched_job_skills.add(job_skill)
                used_resume_skills.add(resume_skill)

                break

    # ======================================================
    # MISSING SKILLS
    # ======================================================

    missing_skills = [
        skill
        for skill in sorted(job_set)
        if skill not in matched_job_skills
    ]

    # ======================================================
    # SCORE
    # ======================================================

    exact_count = len(exact_matches)
    related_count = len(related_matches)

    total_points = (
        exact_count
        + related_count * RELATED_SKILL_CREDIT
    )

    skill_score = (
        total_points / len(job_set)
    )

    skill_score = min(
        max(skill_score, 0.0),
        1.0
    )

    return {
        "score": round(skill_score, 4),
        "exact_matches": exact_matches,
        "related_matches": related_matches,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills
    }


# ==========================================================
# EXPERIENCE MATCHING
# ==========================================================

def calculate_experience_match(
    resume_experience,
    minimum_experience,
    maximum_experience
):
    """
    Compare candidate experience with job requirement.
    """

    try:
        resume_experience = float(resume_experience)
    except (ValueError, TypeError):
        resume_experience = 0.0

    try:
        minimum_experience = float(minimum_experience)
    except (ValueError, TypeError):
        minimum_experience = 0.0

    try:
        maximum_experience = float(maximum_experience)
    except (ValueError, TypeError):
        maximum_experience = minimum_experience

    if maximum_experience < minimum_experience:
        maximum_experience = minimum_experience

    # Candidate is within required range
    if (
        minimum_experience
        <= resume_experience
        <= maximum_experience
    ):
        return 1.0

    # Candidate has less experience
    if resume_experience < minimum_experience:

        difference = (
            minimum_experience
            - resume_experience
        )

        score = max(
            0.0,
            1.0 - difference / 5.0
        )

        return round(score, 4)

    # Candidate has more experience
    difference = (
        resume_experience
        - maximum_experience
    )

    score = max(
        0.5,
        1.0 - difference / 10.0
    )

    return round(score, 4)


# ==========================================================
# EDUCATION MATCHING
# ==========================================================

def calculate_education_match(
    resume_education,
    job_title,
    job_description
):
    """
    Estimate education compatibility.

    The dataset does not contain a dedicated education
    requirement column.
    """

    if not resume_education:
        return 0.0

    job_text = (
        str(job_title)
        + " "
        + str(job_description)
    ).lower()

    degree_keywords = [
        "b.tech",
        "btech",
        "bachelor",
        "b.sc",
        "bsc",
        "bca",
        "b.e",
        "m.tech",
        "mtech",
        "m.e",
        "master",
        "m.sc",
        "msc",
        "mba",
        "mca",
        "phd",
        "doctorate",
        "degree"
    ]

    # No explicit education requirement
    if not any(
        keyword in job_text
        for keyword in degree_keywords
    ):
        return 1.0

    if "phd" in resume_education:
        return 1.0

    if "masters" in resume_education:
        return 1.0

    if "bachelors" in resume_education:
        return 0.9

    if "diploma" in resume_education:
        return 0.7

    if "higher_secondary" in resume_education:
        return 0.5

    return 0.5


# ==========================================================
# ROLE / TEXT SIMILARITY
# ==========================================================

def calculate_role_match(
    resume_text,
    job_title,
    job_description
):
    """
    Calculate TF-IDF cosine similarity.
    """

    job_text = (
        str(job_title)
        + " "
        + str(job_description)
    )

    return calculate_text_similarity(
        resume_text,
        job_text
    )


# ==========================================================
# COMPLETE JOB MATCH
# ==========================================================

def calculate_job_match(
    resume_text,
    resume_skills,
    resume_experience,
    resume_education,
    job
):
    """
    Calculate compatibility for one job.

    Location is NOT part of the score.
    """

    job_skills = extract_job_skills(
        job["tagsAndSkills"]
    )

    skill_result = calculate_skill_match(
        resume_skills,
        job_skills
    )

    skill_score = skill_result["score"]

    experience_score = calculate_experience_match(
        resume_experience,
        job["minimumExperience"],
        job["maximumExperience"]
    )

    education_score = calculate_education_match(
        resume_education,
        job["title"],
        job["jobDescription"]
    )

    role_score = calculate_role_match(
        resume_text,
        job["title"],
        job["jobDescription"]
    )

    # ======================================================
    # FINAL SCORE
    # ======================================================

    final_score = (
        SKILL_WEIGHT * skill_score
        + EXPERIENCE_WEIGHT * experience_score
        + EDUCATION_WEIGHT * education_score
        + ROLE_WEIGHT * role_score
    )

    final_score = min(
        max(final_score, 0.0),
        1.0
    )

    return {
        "match_score": round(
            final_score * 100,
            2
        ),

        "skill_score": round(
            skill_score * 100,
            2
        ),

        "experience_score": round(
            experience_score * 100,
            2
        ),

        "education_score": round(
            education_score * 100,
            2
        ),

        "role_score": round(
            role_score * 100,
            2
        ),

        "exact_matches": skill_result[
            "exact_matches"
        ],

        "related_matches": skill_result[
            "related_matches"
        ],

        "matched_skills": skill_result[
            "matched_skills"
        ],

        "missing_skills": skill_result[
            "missing_skills"
        ]
    }


# ==========================================================
# BUILD FAST SKILL INDEX
# ==========================================================

def build_skill_index(jobs):
    """
    Build an inverted index:

        skill -> job row indexes

    Example:

        python -> {12, 43, 105, 500, ...}
        sql    -> {4, 20, 88, 120, ...}

    This allows us to find relevant jobs without
    calculating every job individually.
    """

    print(
        "\nBuilding job skill index..."
    )

    skill_index = {}

    # Split the tags column into individual skills.
    exploded = (
        jobs[
            ["tagsAndSkills"]
        ]
        .fillna("")
        ["tagsAndSkills"]
        .str.split(",")
        .explode()
    )

    # Normalize every tag.
    normalized_skills = exploded.map(
        normalize_skill
    )

    # Build index
    for row_index, skill in normalized_skills.items():

        if not skill:
            continue

        if skill not in skill_index:
            skill_index[skill] = set()

        skill_index[skill].add(row_index)

    print(
        f"Indexed {len(skill_index):,} unique skills."
    )

    return skill_index


# ==========================================================
# FIND CANDIDATE JOBS
# ==========================================================

def find_candidate_jobs(
    jobs,
    resume_skills,
    skill_index
):
    """
    Find jobs that contain either:

    1. An exact resume skill
    2. A strongly related job skill

    This is the fast filtering stage.
    """

    resume_set = {
        normalize_skill(skill)
        for skill in resume_skills
        if normalize_skill(skill)
    }

    candidate_indexes = set()

    # ======================================================
    # EXACT + RELATED JOB SKILLS
    # ======================================================

    searchable_skills = set(
        resume_set
    )

    for resume_skill in resume_set:

        related = RELATED_SKILLS.get(
            resume_skill,
            set()
        )

        searchable_skills.update(
            related
        )

    # ======================================================
    # LOOK UP JOBS
    # ======================================================

    for skill in searchable_skills:

        indexes = skill_index.get(
            skill,
            set()
        )

        candidate_indexes.update(
            indexes
        )

    if not candidate_indexes:
        return jobs.iloc[0:0]

    candidate_jobs = jobs.loc[
        sorted(candidate_indexes)
    ].copy()

    return candidate_jobs


# ==========================================================
# JOB RANKING
# ==========================================================

def rank_jobs(
    resume_text,
    resume_skills,
    resume_experience,
    resume_education,
    jobs,
    top_n=10
):
    """
    Efficient two-stage job ranking.

    Stage 1:
        Use a skill index to identify relevant jobs.

    Stage 2:
        Calculate skill/experience/education scores
        for those candidates.

    Stage 3:
        Keep the best candidates.

    Stage 4:
        Run expensive TF-IDF role similarity only
        on those candidates.

    Stage 5:
        Return the final Top N jobs.
    """

    # ======================================================
    # BUILD INDEX
    # ======================================================

    skill_index = build_skill_index(
        jobs
    )

    # ======================================================
    # FAST CANDIDATE SEARCH
    # ======================================================

    print(
        "\nFinding jobs with relevant skills..."
    )

    candidate_jobs = find_candidate_jobs(
        jobs,
        resume_skills,
        skill_index
    )

    print(
        f"Candidate jobs found: "
        f"{len(candidate_jobs):,}"
    )

    if candidate_jobs.empty:
        return pd.DataFrame()

    # ======================================================
    # STAGE 1 — FAST SCORING
    # ======================================================

    print(
        "\nStage 1/2: Scoring candidate jobs..."
    )

    candidate_results = []

    for row_index, job in candidate_jobs.iterrows():

        job_skills = extract_job_skills(
            job["tagsAndSkills"]
        )

        skill_result = calculate_skill_match(
            resume_skills,
            job_skills
        )

        experience_score = calculate_experience_match(
            resume_experience,
            job["minimumExperience"],
            job["maximumExperience"]
        )

        education_score = calculate_education_match(
            resume_education,
            job["title"],
            job["jobDescription"]
        )

        # Preliminary score WITHOUT TF-IDF
        preliminary_score = (
            SKILL_WEIGHT
            * skill_result["score"]
            + EXPERIENCE_WEIGHT
            * experience_score
            + EDUCATION_WEIGHT
            * education_score
        )

        candidate_results.append({
            "row_index": row_index,
            "job": job,
            "skill_result": skill_result,
            "experience_score": experience_score,
            "education_score": education_score,
            "preliminary_score": preliminary_score
        })

    # ======================================================
    # SORT PRELIMINARY RESULTS
    # ======================================================

    candidate_results.sort(
        key=lambda x: x["preliminary_score"],
        reverse=True
    )

    # ======================================================
    # KEEP BEST CANDIDATES
    # ======================================================

    candidates = candidate_results[
        :CANDIDATE_LIMIT
    ]

    print(
        f"Detailed role matching on "
        f"{len(candidates):,} jobs..."
    )

    # ======================================================
    # STAGE 2 — ROLE SIMILARITY
    # ======================================================

    results = []

    for item in candidates:

        job = item["job"]

        role_score = calculate_role_match(
            resume_text,
            job["title"],
            job["jobDescription"]
        )

        skill_score = item[
            "skill_result"
        ]["score"]

        experience_score = item[
            "experience_score"
        ]

        education_score = item[
            "education_score"
        ]

        final_score = (
            SKILL_WEIGHT * skill_score
            + EXPERIENCE_WEIGHT * experience_score
            + EDUCATION_WEIGHT * education_score
            + ROLE_WEIGHT * role_score
        )

        final_score = min(
            max(final_score, 0.0),
            1.0
        )

        results.append({

            "job_id": job["jobId"],

            "title": job["title"],

            "company": job["companyName"],

            "location": job["location"],

            "match_score": round(
                final_score * 100,
                2
            ),

            "skill_score": round(
                skill_score * 100,
                2
            ),

            "experience_score": round(
                experience_score * 100,
                2
            ),

            "education_score": round(
                education_score * 100,
                2
            ),

            "role_score": round(
                role_score * 100,
                2
            ),

            # Kept internally for later
            # job-detail / skill-gap pages.
            "exact_matches": item[
                "skill_result"
            ]["exact_matches"],

            "related_matches": item[
                "skill_result"
            ]["related_matches"],

            "matched_skills": item[
                "skill_result"
            ]["matched_skills"],

            "missing_skills": item[
                "skill_result"
            ]["missing_skills"]
        })

    # ======================================================
    # FINAL SORT
    # ======================================================

    results_df = pd.DataFrame(
        results
    )

    if results_df.empty:
        return results_df

    results_df = results_df.sort_values(
        by="match_score",
        ascending=False
    )

    return results_df.head(
        top_n
    ).reset_index(drop=True)


# ==========================================================
# TEST
# ==========================================================

if __name__ == "__main__":

    print("\n========================================")
    print("      CAREERSENSE JOB MATCHING TEST")
    print("========================================")

    # ======================================================
    # LOAD DATA
    # ======================================================

    jobs = load_jobs()

    print(
        f"\nJobs loaded: {len(jobs):,}"
    )

    # ======================================================
    # SAMPLE RESUME
    # ======================================================

    resume_text = """
    Software Engineer with 3 years of experience.

    B.Tech in Computer Science.

    Python, Java, SQL, MySQL, Pandas, NumPy,
    Machine Learning, Scikit-learn, Git, GitHub, Docker.
    """

    resume_skills = [
        "python",
        "java",
        "sql",
        "mysql",
        "pandas",
        "numpy",
        "machine learning",
        "scikit-learn",
        "git",
        "github",
        "docker"
    ]

    resume_experience = 3.0

    resume_education = [
        "bachelors"
    ]

    # ======================================================
    # RANK
    # ======================================================

    top_jobs = rank_jobs(
        resume_text=resume_text,
        resume_skills=resume_skills,
        resume_experience=resume_experience,
        resume_education=resume_education,
        jobs=jobs,
        top_n=10
    )

    # ======================================================
    # DISPLAY
    # ======================================================

    print(
        "\n========================================"
    )

    print(
        "          TOP JOB MATCHES FOR YOU"
    )

    print(
        "========================================"
    )

    if top_jobs.empty:

        print(
            "\nNo matching jobs found."
        )

    else:

        for rank, (_, job) in enumerate(
            top_jobs.iterrows(),
            start=1
        ):

            print(
                f"\n#{rank} {job['title']}"
            )

            print(
                f"Company: {job['company']}"
            )

            print(
                f"Location: {job['location']}"
            )

            print(
                f"Match Score: "
                f"{job['match_score']}%"
            )

            print(
                f"Skills: "
                f"{job['skill_score']}%"
            )

            print(
                f"Experience: "
                f"{job['experience_score']}%"
            )

            print(
                f"Education: "
                f"{job['education_score']}%"
            )

            print(
                f"Role Similarity: "
                f"{job['role_score']}%"
            )

    print(
        "\n========================================"
    )