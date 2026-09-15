import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ==========================================================
# ROLE DEFINITIONS
# ==========================================================

ROLE_FAMILIES = {

    "machine_learning": {
        "machine learning",
        "machine learning engineer",
        "ml engineer",
        "ml",
        "ai engineer",
        "artificial intelligence",
        "deep learning",
        "nlp engineer",
        "natural language processing",
        "generative ai",
        "computer vision",
        "data scientist"
    },

    "data_science": {
        "data scientist",
        "data science",
        "machine learning",
        "machine learning engineer",
        "ml engineer",
        "ai engineer",
        "deep learning",
        "data analytics"
    },

    "data_analysis": {
        "data analyst",
        "data analysis",
        "business analyst",
        "business intelligence",
        "bi analyst",
        "reporting analyst",
        "data analytics"
    },

    "python": {
        "python developer",
        "python",
        "django developer",
        "flask developer",
        "fastapi developer",
        "backend python developer"
    },

    "backend": {
        "backend developer",
        "back end developer",
        "backend engineer",
        "back end engineer",
        "software engineer",
        "software developer",
        "python developer",
        "java developer",
        "api developer",
        "web developer"
    },

    "frontend": {
        "frontend developer",
        "front end developer",
        "frontend engineer",
        "front end engineer",
        "react developer",
        "angular developer",
        "vue developer",
        "ui developer"
    },

    "full_stack": {
        "full stack developer",
        "full-stack developer",
        "full stack engineer",
        "full-stack engineer"
    },

    "java": {
        "java developer",
        "java engineer",
        "spring developer",
        "spring boot developer",
        "software engineer",
        "software developer"
    },

    "devops": {
        "devops engineer",
        "devops",
        "site reliability engineer",
        "sre",
        "platform engineer",
        "cloud engineer",
        "infrastructure engineer"
    },

    "cloud": {
        "cloud engineer",
        "cloud developer",
        "devops engineer",
        "devops",
        "platform engineer",
        "infrastructure engineer"
    },

    "database": {
        "database administrator",
        "database engineer",
        "database developer",
        "sql developer",
        "data engineer",
        "database administrator"
    },

    "data_engineering": {
        "data engineer",
        "data engineering",
        "big data engineer",
        "etl developer",
        "database engineer"
    },

    "cybersecurity": {
        "cyber security",
        "cybersecurity",
        "security engineer",
        "security analyst",
        "information security",
        "soc analyst"
    },

    "testing": {
        "test engineer",
        "qa engineer",
        "quality assurance",
        "software tester",
        "automation tester",
        "test automation engineer"
    },

    "project_management": {
        "project manager",
        "project management",
        "technical project manager",
        "program manager"
    },

    "product_management": {
        "product manager",
        "product management",
        "technical product manager"
    },

    "system_administration": {
        "system administrator",
        "systems administrator",
        "system engineer",
        "linux administrator",
        "windows administrator"
    },

    "networking": {
        "network engineer",
        "network administrator",
        "network security",
        "networking engineer"
    },

    "software_engineering": {
        "software engineer",
        "software developer",
        "software development",
        "application developer",
        "application engineer"
    }
}


# ==========================================================
# KNOWN ROLE PHRASES
# ==========================================================

ROLE_KEYWORDS = [

    # Software
    "software engineer",
    "software developer",
    "software development",
    "application developer",
    "application engineer",

    # Python
    "python developer",
    "python engineer",

    # Java
    "java developer",
    "java engineer",

    # Data
    "data analyst",
    "data scientist",
    "data science",
    "data engineer",
    "data engineering",
    "data analysis",
    "data analytics",
    "business analyst",
    "business intelligence",

    # ML / AI
    "machine learning engineer",
    "machine learning",
    "ml engineer",
    "ai engineer",
    "artificial intelligence",
    "deep learning",
    "nlp engineer",
    "natural language processing",
    "generative ai",
    "computer vision",

    # Development
    "backend developer",
    "back end developer",
    "backend engineer",
    "back end engineer",
    "frontend developer",
    "front end developer",
    "frontend engineer",
    "front end engineer",
    "full stack developer",
    "full-stack developer",
    "full stack engineer",
    "web developer",

    # DevOps / Cloud
    "devops engineer",
    "devops",
    "cloud engineer",
    "cloud developer",
    "site reliability engineer",
    "platform engineer",
    "infrastructure engineer",

    # Database
    "database administrator",
    "database engineer",
    "database developer",
    "sql developer",

    # Security
    "cyber security",
    "cybersecurity",
    "security engineer",
    "security analyst",

    # Testing
    "test engineer",
    "qa engineer",
    "quality assurance",
    "software tester",
    "automation tester",

    # Management
    "project manager",
    "project management",
    "product manager",
    "product management",
    "technical project manager",

    # Systems / Network
    "system administrator",
    "systems administrator",
    "system engineer",
    "network engineer",
    "network administrator",

    # General
    "technical lead",
    "engineering manager",
    "consultant",
    "developer",
    "engineer",
    "analyst"
]


# ==========================================================
# TEXT CLEANING
# ==========================================================

def clean_text(text):
    """
    Normalize text before similarity calculation.
    """

    if text is None:
        return ""

    text = str(text).lower()

    # Preserve useful technical characters.
    text = re.sub(
        r"[^a-zA-Z0-9+#./\- ]+",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ==========================================================
# ROLE PHRASE EXTRACTION
# ==========================================================

def extract_role_keywords(text):
    """
    Extract recognized role phrases from text.
    """

    text = clean_text(text)

    if not text:
        return []

    found = []

    for role in ROLE_KEYWORDS:

        if role in text:
            found.append(role)

    return found


# ==========================================================
# ROLE FAMILY EXTRACTION
# ==========================================================

def extract_role_families(text):
    """
    Determine which professional role families are
    represented in the text.
    """

    text = clean_text(text)

    if not text:
        return set()

    families = set()

    for family, keywords in ROLE_FAMILIES.items():

        for keyword in keywords:

            if keyword in text:

                families.add(
                    family
                )

                break

    return families


# ==========================================================
# ROLE-FOCUSED TEXT EXTRACTION
# ==========================================================

def extract_role_text(text):
    """
    Extract sentences containing role-related information.

    This prevents unrelated resume/job-description content
    from dominating the role similarity calculation.
    """

    text = clean_text(text)

    if not text:
        return ""

    sentences = re.split(
        r"[.\n;]+",
        text
    )

    role_indicators = [

        # Roles
        "engineer",
        "developer",
        "analyst",
        "scientist",
        "manager",
        "architect",
        "administrator",
        "consultant",
        "specialist",
        "programmer",
        "lead",

        # Technical domains
        "machine learning",
        "deep learning",
        "artificial intelligence",
        "data science",
        "data engineering",
        "data analysis",
        "software",
        "python",
        "java",
        "backend",
        "frontend",
        "full stack",
        "cloud",
        "devops",
        "security",
        "testing",
        "database",
        "sql"
    ]

    role_sentences = []

    for sentence in sentences:

        sentence = sentence.strip()

        if not sentence:
            continue

        if any(
            indicator in sentence
            for indicator in role_indicators
        ):

            role_sentences.append(
                sentence
            )

    if role_sentences:

        return " ".join(
            role_sentences
        )

    return text


# ==========================================================
# GENERIC TF-IDF SIMILARITY
# ==========================================================

def calculate_text_similarity(
    text1,
    text2
):
    """
    Generic TF-IDF cosine similarity.

    Returns a value between 0 and 1.
    """

    text1 = clean_text(text1)
    text2 = clean_text(text2)

    if not text1 or not text2:
        return 0.0

    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2),
        min_df=1,
        sublinear_tf=True,
        max_features=30000
    )

    matrix = vectorizer.fit_transform(
        [
            text1,
            text2
        ]
    )

    similarity = cosine_similarity(
        matrix[0:1],
        matrix[1:2]
    )[0][0]

    return float(
        similarity
    )


# ==========================================================
# TITLE SIMILARITY
# ==========================================================

def calculate_title_similarity(
    resume_text,
    job_title
):
    """
    Calculate TF-IDF similarity between the candidate's
    role-focused resume text and the job title.
    """

    resume_role_text = extract_role_text(
        resume_text
    )

    job_title = clean_text(
        job_title
    )

    if not resume_role_text or not job_title:
        return 0.0

    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2),
        min_df=1,
        sublinear_tf=True
    )

    matrix = vectorizer.fit_transform(
        [
            resume_role_text,
            job_title
        ]
    )

    score = cosine_similarity(
        matrix[0:1],
        matrix[1:2]
    )[0][0]

    return float(
        score
    )


# ==========================================================
# ROLE FAMILY COMPATIBILITY
# ==========================================================

def calculate_role_family_score(
    resume_text,
    job_text
):
    """
    Calculate compatibility between the candidate's
    role families and the job's role families.

    Exact family overlap:
        strong score

    Related families:
        partial score

    Completely different families:
        low score
    """

    resume_families = extract_role_families(
        resume_text
    )

    job_families = extract_role_families(
        job_text
    )

    if not resume_families or not job_families:
        return 0.0

    overlap = (
        resume_families
        .intersection(job_families)
    )

    if not overlap:
        return 0.0

    # Jaccard-style compatibility.
    score = (
        len(overlap)
        / len(
            resume_families
            .union(job_families)
        )
    )

    return float(
        min(score, 1.0)
    )


# ==========================================================
# ROLE KEYWORD COMPATIBILITY
# ==========================================================

def calculate_role_keyword_score(
    resume_text,
    job_text
):
    """
    Compare recognized role phrases.

    Longer/more specific role phrases receive more
    importance than generic words.
    """

    resume_roles = set(
        extract_role_keywords(
            resume_text
        )
    )

    job_roles = set(
        extract_role_keywords(
            job_text
        )
    )

    if not resume_roles or not job_roles:
        return 0.0

    common_roles = (
        resume_roles
        .intersection(job_roles)
    )

    if not common_roles:
        return 0.0

    # Give specific multi-word role names more importance.
    weighted_common = 0.0
    weighted_total = 0.0

    for role in resume_roles:

        weight = (
            2.0
            if len(role.split()) >= 2
            else 1.0
        )

        weighted_total += weight

        if role in common_roles:
            weighted_common += weight

    if weighted_total == 0:
        return 0.0

    return float(
        weighted_common
        / weighted_total
    )


# ==========================================================
# FINAL ROLE SIMILARITY
# ==========================================================

def calculate_role_similarity(
    resume_text,
    job_title,
    job_description
):
    """
    Calculate role similarity.

    Final role score:

        50% Job title similarity
        30% Role-focused TF-IDF
        20% Role-family compatibility

    Role keyword matching is incorporated into the
    role-focused component.
    """

    resume_text = clean_text(
        resume_text
    )

    job_title = clean_text(
        job_title
    )

    job_description = clean_text(
        job_description
    )

    if not resume_text or not job_title:
        return 0.0

    # ------------------------------------------------------
    # Resume role text
    # ------------------------------------------------------

    resume_role_text = extract_role_text(
        resume_text
    )

    # ------------------------------------------------------
    # Complete job text
    # ------------------------------------------------------

    job_text = (
        job_title
        + " "
        + job_description
    )

    job_role_text = extract_role_text(
        job_text
    )

    # ------------------------------------------------------
    # 1. TITLE SIMILARITY
    # ------------------------------------------------------

    title_score = calculate_title_similarity(
        resume_role_text,
        job_title
    )

    # ------------------------------------------------------
    # 2. ROLE-FOCUSED TF-IDF
    # ------------------------------------------------------

    tfidf_score = calculate_text_similarity(
        resume_role_text,
        job_role_text
    )

    # ------------------------------------------------------
    # 3. ROLE-FAMILY COMPATIBILITY
    # ------------------------------------------------------

    family_score = calculate_role_family_score(
        resume_text,
        job_text
    )

    # ------------------------------------------------------
    # 4. ROLE KEYWORD COMPATIBILITY
    # ------------------------------------------------------

    keyword_score = calculate_role_keyword_score(
        resume_text,
        job_text
    )

    # ------------------------------------------------------
    # Combine keyword and TF-IDF into role-text score
    # ------------------------------------------------------

    role_text_score = (
        0.75 * tfidf_score
        + 0.25 * keyword_score
    )

    # ------------------------------------------------------
    # FINAL ROLE SCORE
    # ------------------------------------------------------

    role_score = (
        0.50 * title_score
        + 0.30 * role_text_score
        + 0.20 * family_score
    )

    role_score = min(
        max(role_score, 0.0),
        1.0
    )

    return round(
        float(role_score),
        4
    )


# ==========================================================
# BATCH ROLE SIMILARITY
# ==========================================================

def calculate_role_similarity_batch(
    resume_text,
    job_titles,
    job_descriptions
):
    """
    Calculate role similarity for multiple jobs.

    This version uses shared TF-IDF matrices so that
    multiple jobs can be processed efficiently.

    The function is kept available for future optimization
    of job_matcher.py.
    """

    resume_text = clean_text(
        resume_text
    )

    if not resume_text:
        return [
            0.0
            for _ in job_titles
        ]

    resume_role_text = extract_role_text(
        resume_text
    )

    # ------------------------------------------------------
    # Prepare jobs
    # ------------------------------------------------------

    job_titles_cleaned = [
        clean_text(title)
        for title in job_titles
    ]

    job_texts = []

    for title, description in zip(
        job_titles,
        job_descriptions
    ):

        title = clean_text(
            title
        )

        description = clean_text(
            description
        )

        combined = (
            title
            + " "
            + description
        )

        job_texts.append(
            extract_role_text(
                combined
            )
        )

    # ======================================================
    # TITLE TF-IDF
    # ======================================================

    title_vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2),
        min_df=1,
        sublinear_tf=True
    )

    title_documents = [
        resume_role_text
    ] + job_titles_cleaned

    title_matrix = title_vectorizer.fit_transform(
        title_documents
    )

    title_scores = cosine_similarity(
        title_matrix[0:1],
        title_matrix[1:]
    )[0]

    # ======================================================
    # ROLE-TEXT TF-IDF
    # ======================================================

    role_vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2),
        min_df=1,
        sublinear_tf=True,
        max_features=30000
    )

    role_documents = [
        resume_role_text
    ] + job_texts

    role_matrix = role_vectorizer.fit_transform(
        role_documents
    )

    tfidf_scores = cosine_similarity(
        role_matrix[0:1],
        role_matrix[1:]
    )[0]

    # ======================================================
    # FINAL SCORES
    # ======================================================

    results = []

    for index in range(
        len(job_titles)
    ):

        job_text = (
            job_titles_cleaned[index]
            + " "
            + job_texts[index]
        )

        family_score = calculate_role_family_score(
            resume_text,
            job_text
        )

        keyword_score = calculate_role_keyword_score(
            resume_text,
            job_text
        )

        role_text_score = (
            0.75 * tfidf_scores[index]
            + 0.25 * keyword_score
        )

        role_score = (
            0.50 * title_scores[index]
            + 0.30 * role_text_score
            + 0.20 * family_score
        )

        role_score = min(
            max(role_score, 0.0),
            1.0
        )

        results.append(
            round(
                float(role_score),
                4
            )
        )

    return results


# ==========================================================
# TEST
# ==========================================================

if __name__ == "__main__":

    resume = """
    Software Engineer with 3 years of experience.
    B.Tech in Computer Science.

    Python, Java, SQL, MySQL, Pandas, NumPy,
    Machine Learning, Scikit-learn, Git, GitHub, Docker.

    Machine Learning Career Prediction System.
    """

    jobs = [

        (
            "Senior Python Developer",
            """
            Looking for a Python developer with experience
            in backend development, APIs and software
            engineering.
            """
        ),

        (
            "Data Scientist",
            """
            Looking for a data scientist with machine
            learning and Python experience.
            Work on predictive models and data analysis.
            """
        ),

        (
            "Machine Learning Engineer",
            """
            Build machine learning models using Python,
            scikit-learn and machine learning techniques.
            Develop and deploy predictive models.
            """
        ),

        (
            "Fraud Analyst",
            """
            Analyze financial transactions and identify
            fraudulent activities. Investigate suspicious
            transactions and prepare reports.
            """
        ),

        (
            "Frontend Developer",
            """
            Develop web applications using React,
            JavaScript, HTML and CSS.
            """
        ),

        (
            "IT Support Engineer",
            """
            Provide technical support to users.
            Troubleshoot hardware, software, operating
            systems and network issues.
            """
        ),

        (
            "Data Engineer",
            """
            Build data pipelines and ETL systems.
            Work with databases, SQL and large datasets.
            """
        )
    ]

    print(
        "\n========================================"
    )

    print(
        "       ROLE SIMILARITY TEST"
    )

    print(
        "========================================"
    )

    titles = [
        job[0]
        for job in jobs
    ]

    descriptions = [
        job[1]
        for job in jobs
    ]

    scores = calculate_role_similarity_batch(
        resume,
        titles,
        descriptions
    )

    for title, score in zip(
        titles,
        scores
    ):

        print(
            f"{title:<30}"
            f"{score * 100:.2f}%"
        )

    print(
        "\n========================================"
    )

    print(
        "       GENERIC TF-IDF TEST"
    )

    print(
        "========================================"
    )

    similarity = calculate_text_similarity(
        resume,
        jobs[0][1]
    )

    print(
        f"Similarity Score: "
        f"{similarity:.4f}"
    )

    print(
        f"Similarity Percentage: "
        f"{similarity * 100:.2f}%"
    )