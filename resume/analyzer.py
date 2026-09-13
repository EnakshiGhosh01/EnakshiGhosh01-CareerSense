from resume.skill_extractor import (
    extract_skills,
    extract_skills_by_category
)
from resume.experience_extractor import extract_experience
from resume.education_extractor import extract_education
from resume.resume_score import calculate_resume_score


def analyze_resume(text):
    """
    Analyze a resume and return a structured resume profile.

    Extracts:
    - Skills
    - Skills grouped by category
    - Years of experience
    - Education
    - Resume score
    """

    # Handle empty resume text
    if not text or not text.strip():
        empty_score = calculate_resume_score(
            skills=[],
            experience=0.0,
            education=[],
            resume_text=""
        )

        return {
            "skills": [],
            "skills_by_category": {},
            "experience": 0.0,
            "education": [],
            "score": empty_score
        }

    # -------------------------
    # Extract resume information
    # -------------------------

    skills = extract_skills(text)

    skills_by_category = extract_skills_by_category(text)

    experience = extract_experience(text)

    education = extract_education(text)

    # -------------------------
    # Calculate resume score
    # -------------------------

    score = calculate_resume_score(
        skills=skills,
        experience=experience,
        education=education,
        resume_text=text
    )

    # -------------------------
    # Return complete profile
    # -------------------------

    return {
        "skills": skills,
        "skills_by_category": skills_by_category,
        "experience": experience,
        "education": education,
        "score": score
    }


# ==========================================================
# TEST
# ==========================================================

if __name__ == "__main__":

    sample_resume = """
    Software Engineer with 3 years of experience.

    Email: example@gmail.com
    Phone: 9876543210
    LinkedIn: linkedin.com/example
    GitHub: github.com/example

    Education:
    B.Tech in Computer Science.

    Skills:
    Python, Java, SQL, MySQL, Pandas, NumPy,
    Machine Learning, Scikit-learn, Git, Docker.

    Experience:
    Software Engineer at ABC Company.

    Projects:
    Machine Learning Career Prediction System.
    """

    result = analyze_resume(sample_resume)

    print("\n========================================")
    print("        CAREERSENSE RESUME ANALYSIS")
    print("========================================")

    # -------------------------
    # Skills
    # -------------------------

    print("\nSkills:")

    for skill in result["skills"]:
        print(f"- {skill}")

    # -------------------------
    # Skills by category
    # -------------------------

    print("\nSkills by Category:")

    for category, skills in result["skills_by_category"].items():
        print(f"\n{category}:")

        for skill in skills:
            print(f"  - {skill}")

    # -------------------------
    # Experience
    # -------------------------

    print("\nExperience:")
    print(f"{result['experience']} years")

    # -------------------------
    # Education
    # -------------------------

    print("\nEducation:")

    for education in result["education"]:
        print(f"- {education}")

    # -------------------------
    # Resume Score
    # -------------------------

    score = result["score"]

    print("\nResume Score:")
    print(f"Overall Score: {score['total_score']}/100")

    print("\nScore Breakdown:")
    print(f"Skills: {score['skill_score']}/40")
    print(f"Experience: {score['experience_score']}/25")
    print(f"Education: {score['education_score']}/20")
    print(f"Completeness: {score['completeness_score']}/15")

    print("\n========================================")