import re


# ==========================================================
# SKILL CATEGORIES
# ==========================================================

SKILL_CATEGORIES = {

    "programming": [
        "python",
        "java",
        "c",
        "c++",
        "c#",
        "javascript",
        "typescript",
        "go",
        "ruby",
        "php",
        "kotlin",
        "swift",
    ],

    "data_science": [
        "machine learning",
        "deep learning",
        "artificial intelligence",
        "data science",
        "natural language processing",
        "nlp",
        "computer vision",
        "tensorflow",
        "pytorch",
        "scikit-learn",
        "keras",
        "xgboost",
    ],

    "data_analysis": [
        "data analysis",
        "data analytics",
        "pandas",
        "numpy",
        "matplotlib",
        "seaborn",
        "excel",
        "power bi",
        "tableau",
        "data visualization",
    ],

    "databases": [
        "sql",
        "mysql",
        "postgresql",
        "oracle",
        "mongodb",
        "sqlite",
        "redis",
        "database management",
    ],

    "web_development": [
        "html",
        "css",
        "react",
        "angular",
        "vue",
        "node.js",
        "nodejs",
        "express",
        "django",
        "flask",
        "spring",
        "spring boot",
        "rest api",
        "restful api",
    ],

    "cloud": [
        "aws",
        "amazon web services",
        "azure",
        "microsoft azure",
        "google cloud",
        "gcp",
        "docker",
        "kubernetes",
        "terraform",
        "azure devops",
    ],

    "devops": [
        "git",
        "github",
        "gitlab",
        "jenkins",
        "ci/cd",
        "linux",
        "bash",
        "devops",
        "site reliability engineering",
        "sre",
        "monitoring tools",
    ],

    "software_engineering": [
        "data structures",
        "algorithms",
        "object oriented programming",
        "oop",
        "software development",
        "software engineering",
        "debugging",
        "unit testing",
        "api development",
        "design patterns",
    ],

    "business": [
        "business analysis",
        "business intelligence",
        "requirements gathering",
        "project management",
        "agile",
        "scrum",
        "jira",
        "stakeholder management",

        "product management",
        "product marketing",
        "group product management",
        "brand management",
        "brand marketing",

        "performance marketing",
        "growth marketing",
        "digital marketing",
        "paid marketing",
        "user acquisition",
        "acquisition",

        "recruitment",
        "staffing",
        "hiring",
        "manpower",
        "communication",
        "communication skills",

        "medical billing",
        "billing",

        "fire safety",
        "fire protection",
        "fire engineering",
        "fire prevention",
        "safety management",
        "fire management",
        "hazard analysis",
        "safety officer activities",

        "sap",

        "tds filing",
        "itr",
        "gst filing",
        "tax audit",
        "return filing",
        "accounts finalisation",
        "balance sheet finalisation",
        "e way bill",

        "preventive maintenance",
        "utility maintenance",
        "powder coating",
        "conveyor",

        "laboratory",
        "laboratory knowledge",
        "lab",
    ],

    "office_tools": [
        "microsoft office",
        "ms office",
        "m.s office",
        "computer skills",
        "computer knowledge",
    ],

    "languages": [
        "english",
        "spoken english",
        "fluent english",
        "good english communication",
    ],
}


# ==========================================================
# GENERIC / NOISY JOB TAGS
# ==========================================================

GENERIC_JOB_TAGS = {
    "sr",
    "senior",
    "junior",
    "site",
    "technical",
    "performance",
    "usage",
    "marketing",
    "medical",
    "fluent",
    "english",
    "computer",
    "office",
    "microsoft",
    "m.s",
    "ms",
    "skills",
    "knowledge",
    "activities",
    "special process",
    "booth",
    "reliability",
    "monitoring",
    "safety officer",
    "safety",
}


# ==========================================================
# SKILL ALIASES
# ==========================================================

SKILL_ALIASES = {

    "nodejs": "node.js",
    "node js": "node.js",

    "nlp": "natural language processing",

    "oop": "object oriented programming",

    "sre": "site reliability engineering",

    "amazon web services": "aws",

    "google cloud": "gcp",

    "microsoft azure": "azure",

    "ms office": "microsoft office",
    "m.s office": "microsoft office",

    "scikit learn": "scikit-learn",

    "fastapi": "fast api",

    "spoken english": "english",
    "fluent english": "english",
    "good english communication": "communication",
}


# ==========================================================
# RELATED SKILLS
# ==========================================================
#
# These are NOT exact matches.
# They provide partial credit only.
#
# Example:
#
# Resume: Docker
# Job: DevOps
#
# Docker is related to DevOps, but Docker != DevOps.
#
# Therefore:
#
# Exact match  = 1.0
# Related      = 0.5
#
# ==========================================================
# ============================================================
# RELATED SKILLS
# ============================================================
# These are strong relationships where one skill reasonably
# indicates exposure to the other.
#
# IMPORTANT:
# Do NOT add broad relationships such as:
#   Python -> Machine Learning
#   Python -> Data Science
#   NumPy -> Data Analysis
#   Git -> Software Development
#
# Those technologies may be used together, but possessing one
# does not prove possession of the other.
# ============================================================

RELATED_SKILLS = {

    # -------------------------
    # DevOps
    # -------------------------
    "devops": {
        "docker",
        "kubernetes",
        "jenkins",
        "terraform",
        "ci/cd",
        "linux",
        "azure devops",
    },

    "docker": {
        "devops",
        "kubernetes",
    },

    "kubernetes": {
        "devops",
        "docker",
    },

    "jenkins": {
        "devops",
        "ci/cd",
    },

    "terraform": {
        "devops",
    },

    "ci/cd": {
        "devops",
        "jenkins",
    },

    "azure devops": {
        "devops",
        "azure",
    },

    # -------------------------
    # Cloud
    # -------------------------
    "aws": {
        "amazon web services",
    },

    "azure": {
        "microsoft azure",
        "azure devops",
    },

    "gcp": {
        "google cloud",
    },

    # -------------------------
    # Databases
    # -------------------------
    "sql": {
        "mysql",
        "postgresql",
        "oracle",
    },

    "mysql": {
        "sql",
        "database management",
    },

    "postgresql": {
        "sql",
        "database management",
    },

    "oracle": {
        "sql",
        "database management",
    },

    "database management": {
        "sql",
        "mysql",
        "postgresql",
        "oracle",
    },

    # -------------------------
    # Web Development
    # -------------------------
    "node.js": {
        "nodejs",
        "javascript",
    },

    "nodejs": {
        "node.js",
        "javascript",
    },

    "react": {
        "javascript",
    },

    "angular": {
        "javascript",
        "typescript",
    },

    "vue": {
        "javascript",
    },

    "django": {
        "python",
    },

    "flask": {
        "python",
    },

    "spring": {
        "java",
        "spring boot",
    },

    "spring boot": {
        "java",
        "spring",
    },

    # -------------------------
    # Programming
    # -------------------------
    "c++": {
        "c",
    },

    "c#": {
        "c",
    },

    "typescript": {
        "javascript",
    },

    "javascript": {
        "typescript",
    },

    # -------------------------
    # Software Engineering
    # -------------------------
    "object oriented programming": {
        "oop",
    },

    "oop": {
        "object oriented programming",
    },

    "software engineering": {
        "software development",
    },

    "software development": {
        "software engineering",
    },

    "design patterns": {
        "software engineering",
        "object oriented programming",
    },

    "unit testing": {
        "software engineering",
    },

    # -------------------------
    # Data Analysis
    # -------------------------
    # Only closely equivalent concepts are related.
    # Python/NumPy/Pandas are NOT automatically treated as
    # "Data Analysis".
    "data analytics": {
        "data analysis",
    },

    "data analysis": {
        "data analytics",
    },

    # -------------------------
    # Machine Learning
    # -------------------------
    # ML-related technologies can be related to ML,
    # but general programming languages are NOT.
    "machine learning": {
        "scikit-learn",
        "xgboost",
    },

    "scikit-learn": {
        "machine learning",
    },

    "xgboost": {
        "machine learning",
    },

    # -------------------------
    # Deep Learning
    # -------------------------
    "deep learning": {
        "tensorflow",
        "pytorch",
    },

    "tensorflow": {
        "deep learning",
    },

    "pytorch": {
        "deep learning",
    },

    # -------------------------
    # AI
    # -------------------------
    "artificial intelligence": {
        "ai",
    },

    "ai": {
        "artificial intelligence",
    },

    # -------------------------
    # Product Management
    # -------------------------
    "product management": {
        "group product management",
    },

    "group product management": {
        "product management",
    },

    # -------------------------
    # Marketing
    # -------------------------
    "performance marketing": {
        "paid marketing",
    },

    "paid marketing": {
        "performance marketing",
    },

    "growth marketing": {
        "user acquisition",
        "acquisition",
    },

    "user acquisition": {
        "growth marketing",
        "acquisition",
    },

    # -------------------------
    # Microsoft Office
    # -------------------------
    "microsoft office": {
        "ms office",
    },

    "ms office": {
        "microsoft office",
    },
}


# ==========================================================
# NORMALIZE SKILL
# ==========================================================

def normalize_skill(skill):
    """
    Convert a skill to a consistent canonical representation.
    """

    if not skill:
        return ""

    skill = str(skill).strip().lower()

    skill = re.sub(r"\s+", " ", skill)

    skill = skill.strip(" ,.;:-")

    return SKILL_ALIASES.get(skill, skill)


# ==========================================================
# CHECK WHETHER SKILL EXISTS IN TEXT
# ==========================================================

def skill_exists(text, skill):
    """
    Check whether a skill appears in text.
    """

    if not text or not skill:
        return False

    text = str(text).lower()

    skill = normalize_skill(skill)

    if not skill:
        return False

    pattern = (
        r"(?<![a-z0-9])"
        + re.escape(skill)
        + r"(?![a-z0-9])"
    )

    return re.search(pattern, text) is not None


# ==========================================================
# EXTRACT RESUME SKILLS
# ==========================================================

def extract_skills(text):
    """
    Extract recognized skills from resume text.
    """

    if not text:
        return []

    detected = set()

    for category_skills in SKILL_CATEGORIES.values():

        for skill in category_skills:

            normalized = normalize_skill(skill)

            if not normalized:
                continue

            if normalized in GENERIC_JOB_TAGS:
                continue

            if skill_exists(text, skill):
                detected.add(normalized)

    return sorted(detected)


# ==========================================================
# EXTRACT RESUME SKILLS BY CATEGORY
# ==========================================================

def extract_skills_by_category(text):
    """
    Return detected skills grouped by category.
    """

    if not text:
        return {}

    result = {}

    for category, category_skills in SKILL_CATEGORIES.items():

        detected = set()

        for skill in category_skills:

            normalized = normalize_skill(skill)

            if not normalized:
                continue

            if normalized in GENERIC_JOB_TAGS:
                continue

            if skill_exists(text, skill):
                detected.add(normalized)

        if detected:
            result[category] = sorted(detected)

    return result


# ==========================================================
# EXTRACT JOB SKILLS
# ==========================================================

def extract_job_skills(tags_and_skills):
    """
    Extract meaningful skills from the dataset's
    comma-separated tagsAndSkills field.
    """

    if not tags_and_skills:
        return []

    raw_tags = str(tags_and_skills).split(",")

    job_skills = set()

    controlled_skills = set()

    for category_skills in SKILL_CATEGORIES.values():

        for skill in category_skills:
            controlled_skills.add(
                normalize_skill(skill)
            )

    for raw_tag in raw_tags:

        tag = raw_tag.strip().lower()

        if not tag:
            continue

        tag = re.sub(r"\s+", " ", tag)

        tag = tag.strip(" ,.;:-")

        normalized = normalize_skill(tag)

        if not normalized:
            continue

        # Remove obvious noise.
        if normalized in GENERIC_JOB_TAGS:
            continue

        # Known controlled skill.
        if normalized in controlled_skills:
            job_skills.add(normalized)
            continue

        # Keep meaningful multi-word domain-specific tags.
        if len(normalized.split()) >= 2:
            job_skills.add(normalized)

    return sorted(job_skills)


# ==========================================================
# TEST
# ==========================================================

if __name__ == "__main__":

    resume = """
    Software Engineer with Python, Java, SQL, MySQL,
    Pandas, NumPy, Machine Learning, Git, GitHub and Docker.
    """

    job = """
    Python, SQL, Machine Learning, Tableau,
    Power BI, Git, Docker
    """

    print("\n========================================")
    print("       CAREERSENSE SKILL EXTRACTOR")
    print("========================================")

    print("\nResume Skills:")

    for skill in extract_skills(resume):
        print("-", skill)

    print("\nJob Skills:")

    for skill in extract_job_skills(job):
        print("-", skill)

    print("\n========================================")