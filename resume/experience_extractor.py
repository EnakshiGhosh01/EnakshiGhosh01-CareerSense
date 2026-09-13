import re


# ============================================================
# EXPERIENCE EXTRACTION
# ============================================================

def extract_experience(text):

    if not text:
        return 0.0

    text = text.lower()

    # --------------------------------------------------------
    # Patterns such as:
    # "3 years experience"
    # "3+ years of experience"
    # "3 yrs experience"
    # "3 years in software development"
    # --------------------------------------------------------

    patterns = [

        r"(\d+(?:\.\d+)?)\s*\+?\s*years?\s*(?:of\s*)?experience",

        r"experience\s*(?:of\s*)?(\d+(?:\.\d+)?)\s*\+?\s*years?",

        r"(\d+(?:\.\d+)?)\s*\+?\s*yrs?\s*(?:of\s*)?experience",

        r"(\d+(?:\.\d+)?)\s*\+?\s*years?\s*(?:in|with)"
    ]

    matches = []

    for pattern in patterns:

        found = re.findall(
            pattern,
            text
        )

        for value in found:

            try:

                years = float(value)

                if 0 <= years <= 50:

                    matches.append(
                        years
                    )

            except ValueError:
                continue

    # --------------------------------------------------------
    # Handle ranges such as:
    # "3-5 years experience"
    # "2 to 4 years experience"
    # --------------------------------------------------------

    range_patterns = [

        r"(\d+(?:\.\d+)?)\s*[-–]\s*(\d+(?:\.\d+)?)\s*years?",

        r"(\d+(?:\.\d+)?)\s+to\s+(\d+(?:\.\d+)?)\s*years?"
    ]

    range_matches = []

    for pattern in range_patterns:

        found = re.findall(
            pattern,
            text
        )

        for low, high in found:

            try:

                low = float(low)
                high = float(high)

                if (
                    0 <= low <= 50
                    and 0 <= high <= 50
                    and high >= low
                ):

                    midpoint = (
                        low + high
                    ) / 2

                    range_matches.append(
                        midpoint
                    )

            except ValueError:
                continue

    # --------------------------------------------------------
    # Prefer explicit "X years experience"
    # over unrelated ranges.
    # --------------------------------------------------------

    if matches:

        return round(
            max(matches),
            1
        )

    if range_matches:

        return round(
            max(range_matches),
            1
        )

    # --------------------------------------------------------
    # Detect fresher / entry-level
    # --------------------------------------------------------

    fresher_patterns = [
        "fresher",
        "freshers",
        "entry level",
        "entry-level",
        "no experience",
        "0 years experience"
    ]

    for pattern in fresher_patterns:

        if pattern in text:

            return 0.0

    return 0.0


# ============================================================
# MAIN TEST
# ============================================================

if __name__ == "__main__":

    test_resumes = [

        "Software Engineer with 3 years of experience.",

        "Python Developer with 3+ years experience.",

        "Data Analyst with 2-4 years of experience.",

        "Java Developer having 5 yrs experience.",

        "Machine Learning Engineer with 1.5 years of experience.",

        "Recent computer science graduate and fresher."
    ]

    print(
        "\n===== EXPERIENCE EXTRACTION TEST ====="
    )

    for resume in test_resumes:

        experience = extract_experience(
            resume
        )

        print(
            f"\nResume: {resume}"
        )

        print(
            f"Detected experience: "
            f"{experience} years"
        )