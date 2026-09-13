def calculate_resume_score(
    skills,
    experience,
    education,
    resume_text
):
    """
    Calculate an explainable resume score out of 100.

    Experience is NOT used in the score.

    Components:
    - Skills: 40 points
    - Education: 20 points
    - Projects: 15 points
    - Certifications: 10 points
    - Resume completeness: 15 points
    """

    # ==========================================================
    # 1. SKILLS SCORE — 40 POINTS
    # ==========================================================

    skill_count = len(skills)

    if skill_count >= 10:
        skill_score = 40
    elif skill_count >= 7:
        skill_score = 32
    elif skill_count >= 5:
        skill_score = 25
    elif skill_count >= 3:
        skill_score = 18
    elif skill_count >= 1:
        skill_score = 10
    else:
        skill_score = 0

    # ==========================================================
    # 2. EDUCATION SCORE — 20 POINTS
    # ==========================================================

    education_score = 0

    if "phd" in education:
        education_score = 20

    elif "masters" in education:
        education_score = 18

    elif "bachelors" in education:
        education_score = 15

    elif "diploma" in education:
        education_score = 10

    elif "higher_secondary" in education:
        education_score = 5

    # ==========================================================
    # PREPARE RESUME TEXT
    # ==========================================================

    text = resume_text.lower()

    # ==========================================================
    # 3. PROJECT SCORE — 15 POINTS
    # ==========================================================

    project_keywords = [
        "projects",
        "project",
        "academic projects",
        "personal projects",
        "major project",
        "minor project"
    ]

    has_projects = any(
        keyword in text
        for keyword in project_keywords
    )

    if has_projects:
        project_score = 15
    else:
        project_score = 0

    # ==========================================================
    # 4. CERTIFICATION SCORE — 10 POINTS
    # ==========================================================

    certification_keywords = [
        "certifications",
        "certification",
        "certificates",
        "certificate",
        "certified"
    ]

    has_certifications = any(
        keyword in text
        for keyword in certification_keywords
    )

    if has_certifications:
        certification_score = 10
    else:
        certification_score = 0

    # ==========================================================
    # 5. RESUME COMPLETENESS — 15 POINTS
    # ==========================================================

    sections = {
        "skills": [
            "skills",
            "technical skills"
        ],

        "education": [
            "education",
            "academic background"
        ],

        "projects": [
            "projects",
            "academic projects",
            "personal projects"
        ],

        "contact": [
            "email",
            "phone",
            "linkedin",
            "github"
        ],

        "summary": [
            "summary",
            "objective",
            "profile"
        ]
    }

    section_count = 0

    for keywords in sections.values():

        if any(keyword in text for keyword in keywords):
            section_count += 1

    # 5 sections × 3 points = 15
    completeness_score = section_count * 3

    # ==========================================================
    # FINAL SCORE
    # ==========================================================

    total_score = (
        skill_score
        + education_score
        + project_score
        + certification_score
        + completeness_score
    )

    total_score = min(total_score, 100)

    return {
        "total_score": total_score,

        "skill_score": skill_score,

        "education_score": education_score,

        "project_score": project_score,

        "certification_score": certification_score,

        "completeness_score": completeness_score
    }


# ==========================================================
# TEST
# ==========================================================

if __name__ == "__main__":

    sample_resume = """
    Software Engineer.

    Email: example@gmail.com
    Phone: 9876543210
    LinkedIn: linkedin.com/example
    GitHub: github.com/example

    Education:
    B.Tech in Computer Science.

    Skills:
    Python, Java, SQL, MySQL, Pandas, NumPy,
    Machine Learning, Scikit-learn, Git, Docker.

    Projects:
    Machine Learning Career Prediction System.

    Certifications:
    NPTEL Certification in Java.
    """

    skills = [
        "docker",
        "git",
        "java",
        "machine learning",
        "mysql",
        "numpy",
        "pandas",
        "python",
        "scikit-learn",
        "sql"
    ]

    # Experience is deliberately supplied but NOT used
    # to calculate the score.
    experience = 3.0

    education = ["bachelors"]

    result = calculate_resume_score(
        skills=skills,
        experience=experience,
        education=education,
        resume_text=sample_resume
    )

    print("\n========================================")
    print("       CAREERSENSE RESUME SCORE")
    print("========================================")

    print(f"\nOverall Score: {result['total_score']}/100")

    print("\nScore Breakdown:")
    print(f"Skills: {result['skill_score']}/40")
    print(f"Education: {result['education_score']}/20")
    print(f"Projects: {result['project_score']}/15")
    print(f"Certifications: {result['certification_score']}/10")
    print(f"Completeness: {result['completeness_score']}/15")

    print("\nExperience:")
    print(f"{experience} years")
    print("(Not included in Resume Score)")

    print("\n========================================")