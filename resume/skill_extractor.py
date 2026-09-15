import re


# ==========================================================
# CONTROLLED SKILL VOCABULARY
# ==========================================================

SKILL_CATEGORIES = {

    # ------------------------------------------------------
    # Programming Languages
    # ------------------------------------------------------

    "programming": {
        "python",
        "java",
        "c",
        "c++",
        "c#",
        "javascript",
        "typescript",
        "scala",
        "kotlin",
        "swift",
        "go",
        "golang",
        "rust",
        "php",
        "ruby",
        "r",
        "matlab",
        "perl",
        "shell scripting",
        "bash",
        "powershell",
        "sql",
        "pl/sql",
        "rpg",
        "rpgle",
        "clp",
        "clle",
        "cobol",
        "fortran",
    },


    # ------------------------------------------------------
    # Data Science / Machine Learning / AI
    # ------------------------------------------------------

    "data_science": {
        "machine learning",
        "machine learning algorithms",
        "deep learning",
        "artificial intelligence",
        "generative ai",
        "generative artificial intelligence",
        "natural language processing",
        "computer vision",
        "reinforcement learning",
        "data science",
        "statistics",
        "statistical analysis",
        "linear algebra",
        "calculus",
        "algorithms",
        "data structures",
        "model development",
        "model deployment",
        "mlops",
        "ml ops",
        "ml flow",
        "ml pipelines",
        "ai techniques",
        "large language model",
        "llm",
        "open ai",
        "openai",
        "openai apis",
        "cognitive services",
        "asr",
        "ivR",
        "jax",
        "tensorflow",
        "tensor flow",
        "pytorch",
        "keras",
        "scikit-learn",
        "xgboost",
    },


    # ------------------------------------------------------
    # Data Analysis / BI
    # ------------------------------------------------------

    "data_analysis": {
        "data analysis",
        "data analytics",
        "data analytics",
        "data visualization",
        "business intelligence",
        "business analytics",
        "power bi",
        "tableau",
        "excel",
        "advanced excel",
        "pandas",
        "numpy",
        "matplotlib",
        "seaborn",
        "power query",
        "power pivot",
        "qlikview",
        "qlik sense",
        "looker",
        "sas",
        "spss",
    },


    # ------------------------------------------------------
    # Databases
    # ------------------------------------------------------

    "databases": {
        "sql",
        "mysql",
        "postgresql",
        "postgres",
        "oracle",
        "oracle database",
        "mongodb",
        "redis",
        "sqlite",
        "database management",
        "dbms",
        "db2",
        "ibm db2",
        "pl/sql",
        "stored procedures",
        "query writing",
        "database design",
        "database administration",
        "hive",
        "presto",
        "snowflake",
    },


    # ------------------------------------------------------
    # Web Development
    # ------------------------------------------------------

    "web_development": {
        "html",
        "html5",
        "css",
        "css3",
        "javascript",
        "typescript",
        "react",
        "react.js",
        "reactjs",
        "angular",
        "vue",
        "vue.js",
        "node.js",
        "nodejs",
        "express",
        "express.js",
        "django",
        "flask",
        "fastapi",
        "spring",
        "spring boot",
        "rest",
        "rest api",
        "restful api",
        "api development",
    },


    # ------------------------------------------------------
    # Cloud
    # ------------------------------------------------------

    "cloud": {
        "aws",
        "amazon web services",
        "azure",
        "microsoft azure",
        "gcp",
        "google cloud",
        "google cloud platform",
        "azure kubernetes services",
        "aks",
        "cognitive services",
        "cloud computing",
        "cloud architecture",
        "cloud security",
        "cloud deployment",
    },


    # ------------------------------------------------------
    # DevOps
    # ------------------------------------------------------

    "devops": {
        "devops",
        "devops tools",
        "docker",
        "kubernetes",
        "jenkins",
        "terraform",
        "ansible",
        "ci/cd",
        "ci cd",
        "continuous integration",
        "continuous delivery",
        "continuous deployment",
        "azure devops",
        "git",
        "github",
        "gitlab",
        "bitbucket",
        "linux",
        "unix",
        "sre",
        "site reliability engineering",
        "monitoring",
        "deployment",
    },


    # ------------------------------------------------------
    # Software Engineering
    # ------------------------------------------------------

    "software_engineering": {
        "software engineering",
        "software development",
        "software design",
        "system design",
        "technical design",
        "object oriented programming",
        "oop",
        "design patterns",
        "unit testing",
        "tdd",
        "debugging",
        "agile",
        "scrum",
        "jira",
        "version control",
        "github",
        "git",
        "architecture",
        "system architecture",
        "microservices",
        "testing",
        "automation",
    },


    # ------------------------------------------------------
    # Signal Processing / Embedded / Electronics
    # ------------------------------------------------------

    "signal_processing": {
        "signal processing",
        "digital signal processing",
        "dsp",
        "matlab",
        "hdl",
        "verilog",
        "vhdl",
        "radar",
        "embedded systems",
        "embedded c",
        "fpga",
        "microcontrollers",
        "electronics",
        "image processing",
        "audio processing",
    },


    # ------------------------------------------------------
    # IBM / AS400 / Mainframe
    # ------------------------------------------------------

    "enterprise_systems": {
        "as400",
        "ibm as400",
        "iseries",
        "ibm i",
        "rpg",
        "rpgle",
        "rpg iv",
        "clp",
        "clle",
        "ile",
        "ile rpg",
        "sqlrpgle",
        "seu",
        "db2",
        "ibm db2",
        "cobol",
        "mainframe",
        "z/os",
        "jcl",
    },


    # ------------------------------------------------------
    # Business / Management
    # ------------------------------------------------------

    "business": {
        "business analysis",
        "business analyst",
        "business analytics",
        "requirements analysis",
        "requirements gathering",
        "stakeholder management",
        "project management",
        "product management",
        "group product management",
        "process management",
        "operations",
        "sales",
        "customer service",
        "consulting",
        "erp",
        "sap",
        "supply chain",
        "insurance",
    },


    # ------------------------------------------------------
    # Marketing
    # ------------------------------------------------------

    "marketing": {
        "digital marketing",
        "performance marketing",
        "paid marketing",
        "growth marketing",
        "user acquisition",
        "acquisition",
        "seo",
        "sem",
        "social media marketing",
        "content marketing",
        "marketing analytics",
    },


    # ------------------------------------------------------
    # Office / Productivity
    # ------------------------------------------------------

    "office_tools": {
        "microsoft office",
        "ms office",
        "microsoft excel",
        "excel",
        "powerpoint",
        "word",
        "outlook",
        "access",
    },


    # ------------------------------------------------------
    # Languages / Communication
    # ------------------------------------------------------

    "languages": {
        "english",
        "hindi",
        "bengali",
        "communication",
        "english communication",
    },
}


# ==========================================================
# SKILL ALIASES
# ==========================================================

SKILL_ALIASES = {

    "nodejs": "node.js",
    "node js": "node.js",

    "reactjs": "react",
    "react.js": "react",

    "vuejs": "vue",
    "vue.js": "vue",

    "angularjs": "angular",
    "angular.js": "angular",

    "golang": "go",

    "scikit learn": "scikit-learn",
    "scikit_learn": "scikit-learn",

    "tensor flow": "tensorflow",

    "mlops": "mlops",
    "ml ops": "mlops",

    "generative artificial intelligence": "generative ai",

    "artificial intelligence": "artificial intelligence",

    "natural language processing": "natural language processing",

    "large language model": "large language model",

    "openai api": "openai apis",
    "openai apis": "openai apis",

    "amazon web services": "aws",

    "microsoft azure": "azure",

    "google cloud platform": "gcp",
    "google cloud": "gcp",

    "azure kubernetes services": "azure kubernetes services",

    "ci cd": "ci/cd",
    "continuous integration": "ci/cd",
    "continuous delivery": "ci/cd",
    "continuous deployment": "ci/cd",

    "site reliability engineering": "sre",

    "object oriented programming": "oop",

    "postgres": "postgresql",

    "ibm db2": "db2",

    "ibm as400": "as400",
    "iseries": "as400",
    "ibm i": "as400",

    "ile rpg": "rpgle",

    "digital signal processing": "dsp",

    "ms office": "microsoft office",

    "advanced excel": "excel",

    "english communication": "communication",
}


# ==========================================================
# RELATED SKILLS
# ==========================================================

# IMPORTANT:
# These relationships are intentionally conservative.
#
# We DO NOT consider:
# Python -> Machine Learning
# Python -> Data Science
# NumPy -> Data Analysis
# Git -> Software Development
#
# because those relationships are too broad to prove
# actual skill equivalence.

RELATED_SKILLS = {

    # -------------------------
    # DevOps
    # -------------------------

    "devops": {
        "docker",
        "kubernetes",
        "jenkins",
        "terraform",
        "ansible",
        "ci/cd",
        "linux",
        "azure devops",
        "sre",
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

    "ansible": {
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

    "sre": {
        "devops",
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
        "azure kubernetes services",
    },

    "gcp": {
        "google cloud",
        "google cloud platform",
    },


    # -------------------------
    # Databases
    # -------------------------

    "sql": {
        "mysql",
        "postgresql",
        "oracle",
        "database management",
        "dbms",
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

    "db2": {
        "sql",
        "database management",
    },

    "database management": {
        "sql",
        "mysql",
        "postgresql",
        "oracle",
        "dbms",
    },

    "dbms": {
        "sql",
        "database management",
    },


    # -------------------------
    # Web
    # -------------------------

    "javascript": {
        "typescript",
        "react",
        "angular",
        "vue",
        "node.js",
    },

    "typescript": {
        "javascript",
        "react",
        "angular",
        "node.js",
    },

    "react": {
        "javascript",
        "typescript",
    },

    "angular": {
        "javascript",
        "typescript",
    },

    "vue": {
        "javascript",
        "typescript",
    },

    "node.js": {
        "javascript",
    },

    "django": {
        "python",
    },

    "flask": {
        "python",
    },

    "fastapi": {
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


    # -------------------------
    # Software Engineering
    # -------------------------

    "software engineering": {
        "software development",
    },

    "software development": {
        "software engineering",
    },

    "design patterns": {
        "software engineering",
        "oop",
    },

    "oop": {
        "object oriented programming",
    },

    "unit testing": {
        "software engineering",
    },

    "tdd": {
        "unit testing",
        "software engineering",
    },


    # -------------------------
    # Machine Learning
    # -------------------------

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

    "deep learning": {
        "tensorflow",
        "pytorch",
        "keras",
    },

    "tensorflow": {
        "deep learning",
    },

    "pytorch": {
        "deep learning",
    },

    "keras": {
        "deep learning",
    },


    # -------------------------
    # Signal Processing
    # -------------------------

    "dsp": {
        "signal processing",
        "digital signal processing",
    },

    "signal processing": {
        "dsp",
    },

    "matlab": {
        "signal processing",
        "dsp",
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
    # Product
    # -------------------------

    "product management": {
        "group product management",
    },

    "group product management": {
        "product management",
    },
}


# ==========================================================
# NORMALIZATION
# ==========================================================

def normalize_skill(skill):
    """
    Normalize a skill into a consistent representation.

    Examples:
        Python -> python
        NodeJS -> node.js
        Scikit Learn -> scikit-learn
        Amazon Web Services -> aws
    """

    if skill is None:
        return ""

    skill = str(skill).strip().lower()

    if not skill:
        return ""

    # Remove surrounding punctuation
    skill = skill.strip(".,;:|/-_")

    # Normalize whitespace
    skill = re.sub(r"\s+", " ", skill)

    # Normalize common separators
    skill = skill.replace(" / ", "/")
    skill = skill.replace(" - ", "-")

    # Apply aliases
    if skill in SKILL_ALIASES:
        skill = SKILL_ALIASES[skill]

    return skill


# ==========================================================
# BUILD CONTROLLED VOCABULARY
# ==========================================================

def _build_skill_vocabulary():
    """
    Build normalized skill vocabulary from all categories.
    """

    vocabulary = set()

    for skills in SKILL_CATEGORIES.values():
        for skill in skills:
            normalized = normalize_skill(skill)

            if normalized:
                vocabulary.add(normalized)

    # Include aliases
    for alias, canonical in SKILL_ALIASES.items():
        normalized_alias = normalize_skill(alias)
        normalized_canonical = normalize_skill(canonical)

        if normalized_alias:
            vocabulary.add(normalized_alias)

        if normalized_canonical:
            vocabulary.add(normalized_canonical)

    return vocabulary


SKILL_VOCABULARY = _build_skill_vocabulary()


# ==========================================================
# TEXT NORMALIZATION
# ==========================================================

def _normalize_text(text):
    """
    Normalize text while preserving useful technical symbols.
    """

    if not text:
        return ""

    text = str(text).lower()

    # Normalize common Unicode characters
    text = text.replace("–", "-")
    text = text.replace("—", "-")
    text = text.replace("’", "'")

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text)

    return text


# ==========================================================
# SKILL EXTRACTION FROM RESUME TEXT
# ==========================================================

def extract_skills(text):
    """
    Extract controlled skills from resume text.

    Only skills from SKILL_VOCABULARY are returned.
    This prevents random words such as:

        sr
        usage
        fluent
        hiring

    from being treated as skills.
    """

    if not text:
        return []

    normalized_text = _normalize_text(text)

    found_skills = set()

    # Longer skills first to avoid partial matches.
    skills_sorted = sorted(
        SKILL_VOCABULARY,
        key=len,
        reverse=True
    )

    for skill in skills_sorted:

        escaped_skill = re.escape(skill)

        # Allow spaces/hyphens/slashes in technical terms.
        pattern = r"(?<![a-z0-9])" + escaped_skill + r"(?![a-z0-9])"

        if re.search(pattern, normalized_text):

            canonical = normalize_skill(skill)

            if canonical:
                found_skills.add(canonical)

    return sorted(found_skills)


# ==========================================================
# SKILLS BY CATEGORY
# ==========================================================

def extract_skills_by_category(text):
    """
    Extract skills and group them by category.
    """

    normalized_text = _normalize_text(text)

    result = {}

    for category, skills in SKILL_CATEGORIES.items():

        found = set()

        for skill in skills:

            normalized_skill_name = normalize_skill(skill)

            if not normalized_skill_name:
                continue

            escaped_skill = re.escape(normalized_skill_name)

            pattern = (
                r"(?<![a-z0-9])"
                + escaped_skill
                + r"(?![a-z0-9])"
            )

            if re.search(pattern, normalized_text):

                canonical = normalize_skill(
                    SKILL_ALIASES.get(
                        normalized_skill_name,
                        normalized_skill_name
                    )
                )

                if canonical:
                    found.add(canonical)

        if found:
            result[category] = sorted(found)

    return result


# ==========================================================
# JOB SKILL EXTRACTION
# ==========================================================

def extract_job_skills(tags):
    """
    Extract recognized skills from the dataset's
    tagsAndSkills column.

    The dataset contains comma-separated tags such as:

        HDL,Coding,Radar,MATLAB,Python,DSP,Processing,Process

    Only controlled technical/business skills are retained.

    Result:

        ['dsp', 'hdl', 'matlab', 'python', 'radar']
    """

    if tags is None:
        return []

    if isinstance(tags, float):
        return []

    text = str(tags)

    if not text.strip():
        return []

    # Dataset tags are primarily comma-separated.
    raw_tags = re.split(r"[,;|]", text)

    extracted = set()

    for raw_tag in raw_tags:

        skill = normalize_skill(raw_tag)

        if not skill:
            continue

        # Direct vocabulary match
        if skill in SKILL_VOCABULARY:

            canonical = normalize_skill(
                SKILL_ALIASES.get(skill, skill)
            )

            if canonical:
                extracted.add(canonical)

            continue

        # Some tags contain phrases such as:
        # "Machine Learning Algorithms"
        # "Microsoft Azure"
        # "Object Oriented Programming"
        #
        # Check whether a known skill occurs inside
        # the complete tag.

        tag_text = _normalize_text(raw_tag)

        for known_skill in sorted(
            SKILL_VOCABULARY,
            key=len,
            reverse=True
        ):

            escaped_skill = re.escape(known_skill)

            pattern = (
                r"(?<![a-z0-9])"
                + escaped_skill
                + r"(?![a-z0-9])"
            )

            if re.search(pattern, tag_text):

                canonical = normalize_skill(
                    SKILL_ALIASES.get(
                        known_skill,
                        known_skill
                    )
                )

                if canonical:
                    extracted.add(canonical)

                break

    return sorted(extracted)


# ==========================================================
# TEST
# ==========================================================

if __name__ == "__main__":

    sample_resume = """
    Software Engineer with 3 years of experience.

    B.Tech in Computer Science.

    Skills:
    Python, Java, SQL, MySQL, Pandas, NumPy,
    Machine Learning, Scikit-learn, Git, GitHub,
    Docker, MATLAB, DSP.
    """

    print("\n========================================")
    print("        CAREERSENSE SKILL TEST")
    print("========================================")

    print("\nResume Skills:")

    skills = extract_skills(sample_resume)

    for skill in skills:
        print(f"- {skill}")

    print("\nSkills by Category:")

    skills_by_category = extract_skills_by_category(
        sample_resume
    )

    for category, category_skills in skills_by_category.items():

        print(f"\n{category}:")

        for skill in category_skills:
            print(f"  - {skill}")

    print("\n----------------------------------------")
    print("JOB SKILL EXTRACTION TEST")
    print("----------------------------------------")

    test_jobs = [

        "HDL,Coding,Radar,MATLAB,Python,DSP,Processing,Process",

        "clp,as400,dbms,sql,sqlrpgle,seu,ile,software development",

        "nas,vmware,nfs,cifs,unix,architecture,sql,itil",

        "Algorithms,Machine Learning,Deep Learning,Python,"
        "Model Development,Tensorflow,Data Structures,Pandas",

        "Machine Learning,Python,Tensorflow,Generative Ai,"
        "Natural Language Processing,LLM,Deep Learning,Pytorch",
    ]

    for tags in test_jobs:

        print("\nTAGS:")
        print(tags)

        print("\nEXTRACTED:")

        for skill in extract_job_skills(tags):
            print(f"- {skill}")

    print("\n========================================")