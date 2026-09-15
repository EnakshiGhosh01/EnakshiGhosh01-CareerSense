import pandas as pd

from matching.similarity import calculate_role_similarity

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

# Expensive role similarity is calculated only for
# the strongest candidates.
CANDIDATE_LIMIT = 500

# When a job has only a very small number of extracted
# skills, don't allow one matching skill to automatically
# become a perfect overall skill score.
MIN_EXTRACTED_JOB_SKILLS_FOR_FULL_CONFIDENCE = 3

# Clearly unrelated roles receive a conservative penalty.
# This does NOT remove the job completely.
ROLE_FAMILY_PENALTY_THRESHOLD = 0.05


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
    Compare candidate skills with job skills.

    Exact match:
        1.0 credit

    Related match:
        0.5 credit

    Missing:
        0.0 credit

    The score considers:

        1. Job skill coverage
        2. Candidate skill relevance

    This prevents a job with only one extracted skill
    from automatically receiving 100%.
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
    # JOB-SIDE COVERAGE
    # ======================================================

    exact_count = len(exact_matches)
    related_count = len(related_matches)

    total_points = (
        exact_count
        + related_count * RELATED_SKILL_CREDIT
    )

    job_coverage = (
        total_points / len(job_set)
    )

    # ======================================================
    # CANDIDATE-SIDE RELEVANCE
    # ======================================================

    candidate_relevant_count = (
        exact_count + related_count
    )

    if resume_set:

        candidate_relevance = (
            candidate_relevant_count
            / len(resume_set)
        )

    else:
        candidate_relevance = 0.0

    # ======================================================
    # COMBINED SKILL SCORE
    # ======================================================

    skill_score = (
        0.75 * job_coverage
        + 0.25 * candidate_relevance
    )

    # ======================================================
    # LOW-INFORMATION JOB PENALTY
    # ======================================================

    if len(job_set) < MIN_EXTRACTED_JOB_SKILLS_FOR_FULL_CONFIDENCE:

        confidence_factor = (
            len(job_set)
            / MIN_EXTRACTED_JOB_SKILLS_FOR_FULL_CONFIDENCE
        )

        skill_score *= (
            0.75
            + 0.25 * confidence_factor
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

    Candidate inside required range:
        1.0

    Candidate below minimum:
        gradual penalty

    Candidate above maximum:
        small penalty, but still receives credit

    Experience is treated as numeric information,
    NOT TF-IDF text similarity.
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

    # ------------------------------------------------------
    # Handle invalid ranges
    # ------------------------------------------------------

    if maximum_experience < minimum_experience:
        maximum_experience = minimum_experience

    # ------------------------------------------------------
    # No meaningful experience requirement
    # ------------------------------------------------------

    if (
        minimum_experience == 0
        and maximum_experience == 0
    ):
        return 0.5

    # ------------------------------------------------------
    # Candidate is inside required range
    # ------------------------------------------------------

    if (
        minimum_experience
        <= resume_experience
        <= maximum_experience
    ):
        return 1.0

    # ------------------------------------------------------
    # Candidate has less experience
    # ------------------------------------------------------

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

    # ------------------------------------------------------
    # Candidate has more experience
    # ------------------------------------------------------

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
    requirement column, so education requirements are
    inferred from the job title and description.

    Generic "degree" alone is NOT treated as an
    explicit education requirement.

    Scores:

        PhD requirement:
            PhD       -> 1.0
            Masters   -> 0.9
            Bachelors -> 0.7

        Masters requirement:
            PhD       -> 1.0
            Masters   -> 1.0
            Bachelors -> 0.7

        Bachelors requirement:
            PhD       -> 1.0
            Masters   -> 1.0
            Bachelors -> 1.0
            Diploma   -> 0.6

        Diploma requirement:
            Diploma   -> 1.0
            Degree     -> 0.7

        Higher-secondary requirement:
            Higher secondary -> 1.0

        No explicit requirement:
            0.5
    """

    if not resume_education:
        return 0.0

    # ------------------------------------------------------
    # Normalize resume education
    # ------------------------------------------------------

    resume_education = {
        str(item).lower().strip()
        for item in resume_education
        if str(item).strip()
    }

    if not resume_education:
        return 0.0

    # ------------------------------------------------------
    # Combine job title + description
    # ------------------------------------------------------

    job_text = (
        str(job_title)
        + " "
        + str(job_description)
    ).lower()

    # ------------------------------------------------------
    # Detect explicit education requirements
    # ------------------------------------------------------

    phd_required = any(
        phrase in job_text
        for phrase in [
            "phd",
            "ph.d",
            "doctorate",
            "doctoral degree"
        ]
    )

    masters_required = any(
        phrase in job_text
        for phrase in [
            "master's degree",
            "masters degree",
            "master degree",
            "m.tech",
            "mtech",
            "m.e degree",
            "m.e.",
            "m.sc",
            "msc",
            "mba",
            "mca",
            "post graduate",
            "postgraduate"
        ]
    )

    bachelors_required = any(
        phrase in job_text
        for phrase in [
            "bachelor's degree",
            "bachelors degree",
            "bachelor degree",
            "bachelor's",
            "bachelors",
            "b.tech",
            "btech",
            "b.e degree",
            "b.e.",
            "b.sc",
            "bsc",
            "bca",
            "graduation",
            "undergraduate degree"
        ]
    )

    diploma_required = any(
        phrase in job_text
        for phrase in [
            "diploma",
            "polytechnic"
        ]
    )

    higher_secondary_required = any(
        phrase in job_text
        for phrase in [
            "12th",
            "class 12",
            "higher secondary",
            "10+2",
            "intermediate"
        ]
    )

    # ------------------------------------------------------
    # Generic "degree" is intentionally ignored
    # ------------------------------------------------------

    has_explicit_requirement = (
        phd_required
        or masters_required
        or bachelors_required
        or diploma_required
        or higher_secondary_required
    )

    if not has_explicit_requirement:
        return 0.5

    # ------------------------------------------------------
    # Candidate education
    # ------------------------------------------------------

    has_phd = "phd" in resume_education
    has_masters = "masters" in resume_education
    has_bachelors = "bachelors" in resume_education
    has_diploma = "diploma" in resume_education
    has_higher_secondary = (
        "higher_secondary" in resume_education
    )

    # ------------------------------------------------------
    # PHD REQUIREMENT
    # ------------------------------------------------------

    if phd_required:

        if has_phd:
            return 1.0

        if has_masters:
            return 0.9

        if has_bachelors:
            return 0.7

        if has_diploma:
            return 0.4

        if has_higher_secondary:
            return 0.2

    # ------------------------------------------------------
    # MASTERS REQUIREMENT
    # ------------------------------------------------------

    if masters_required:

        if has_phd:
            return 1.0

        if has_masters:
            return 1.0

        if has_bachelors:
            return 0.7

        if has_diploma:
            return 0.4

        if has_higher_secondary:
            return 0.2

    # ------------------------------------------------------
    # BACHELORS REQUIREMENT
    # ------------------------------------------------------

    if bachelors_required:

        if has_phd:
            return 1.0

        if has_masters:
            return 1.0

        if has_bachelors:
            return 1.0

        if has_diploma:
            return 0.6

        if has_higher_secondary:
            return 0.3

    # ------------------------------------------------------
    # DIPLOMA REQUIREMENT
    # ------------------------------------------------------

    if diploma_required:

        if has_phd:
            return 0.7

        if has_masters:
            return 0.7

        if has_bachelors:
            return 0.7

        if has_diploma:
            return 1.0

        if has_higher_secondary:
            return 0.5

    # ------------------------------------------------------
    # HIGHER SECONDARY REQUIREMENT
    # ------------------------------------------------------

    if higher_secondary_required:

        if (
            has_phd
            or has_masters
            or has_bachelors
        ):
            return 1.0

        if has_diploma:
            return 0.9

        if has_higher_secondary:
            return 1.0

    return 0.5


# ==========================================================
# ROLE / SEMANTIC SIMILARITY
# ==========================================================

def calculate_role_match(
    resume_text,
    job_title,
    job_description
):
    """
    Use the improved role similarity system.

    The similarity module combines:

        50% title similarity
        30% role-focused TF-IDF + role keywords
        20% role-family compatibility

    This is much more appropriate for career-role
    matching than generic full-text TF-IDF.
    """

    return calculate_role_similarity(
        resume_text,
        job_title,
        job_description
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

        # Kept internally for future job-detail /
        # skill-gap pages.

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

    This allows candidate jobs to be found without
    calculating every job individually.
    """

    print(
        "\nBuilding job skill index..."
    )

    skill_index = {}

    exploded = (
        jobs[
            ["tagsAndSkills"]
        ]
        .fillna("")
        ["tagsAndSkills"]
        .str.split(",")
        .explode()
    )

    normalized_skills = exploded.map(
        normalize_skill
    )

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
    Efficient multi-stage job ranking.

    Stage 1:
        Build skill index.

    Stage 2:
        Find relevant candidate jobs.

    Stage 3:
        Calculate skill/experience/education scores.

    Stage 4:
        Keep strongest candidates.

    Stage 5:
        Calculate improved role similarity.

    Stage 6:
        Return final Top N.
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

        # Preliminary score without role similarity
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
    # STAGE 2 — IMPROVED ROLE SIMILARITY
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

        # ==================================================
        # ROLE COMPATIBILITY SAFETY CHECK
        # ==================================================

        # If role similarity is extremely low, we don't
        # completely discard the job because the candidate
        # may still possess useful transferable skills.
        #
        # Instead, apply a modest penalty to the role
        # contribution.

        if role_score < ROLE_FAMILY_PENALTY_THRESHOLD:

            role_score *= 0.50

        # ==================================================
        # FINAL SCORE
        # ==================================================

        final_score = (
            SKILL_WEIGHT
            * skill_score

            + EXPERIENCE_WEIGHT
            * experience_score

            + EDUCATION_WEIGHT
            * education_score

            + ROLE_WEIGHT
            * role_score
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

            # Kept internally for future
            # skill-gap / job-detail pages.

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

    print(
        "\n========================================"
    )

    print(
        "      CAREERSENSE JOB MATCHING TEST"
    )

    print(
        "========================================"
    )

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

    Machine Learning Career Prediction System.
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

    print(
        "\n===== RESUME PROFILE ====="
    )

    print(
        "Skills: "
        + ", ".join(resume_skills)
    )

    print(
        f"Experience: {resume_experience}"
    )

    print(
        f"Education: {resume_education}"
    )

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