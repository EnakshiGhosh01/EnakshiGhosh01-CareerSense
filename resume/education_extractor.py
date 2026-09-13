import re


def extract_education(text):
    if not text:
        return []   # empty list if no text

    text = text.lower()

    education_keywords = {
        "phd": [
            "ph.d",
            "phd",
            "doctor of philosophy"
        ],
        "masters": [
            "m.tech",
            "mtech",
            "m.e",
            "master of engineering",
            "master of technology",
            "m.sc",
            "msc",
            "master of science",
            "mba",
            "master of business administration",
            "mca",
            "master of computer applications"
        ],
        "bachelors": [
            "b.tech",
            "btech",
            "b.e",
            "bachelor of engineering",
            "bachelor of technology",
            "b.sc",
            "bsc",
            "bachelor of science",
            "bca",
            "bachelor of computer applications",
            "bba",
            "bachelor of business administration"
        ],
        "diploma": [
            "diploma",
            "polytechnic"
        ],
        "higher_secondary": [
            "12th",
            "class 12",
            "higher secondary",
            "hsc"
        ],
        "secondary": [
            "10th",
            "class 10",
            "secondary school",
            "ssc"
        ]
    }

    detected = []

    for level, keywords in education_keywords.items():
        for keyword in keywords:
            # Escape keyword so special characters like "." are handled safely
            pattern = r"(?<!\w)" + re.escape(keyword) + r"(?!\w)"

            if re.search(pattern, text):
                detected.append(level)
                break

    return detected


if __name__ == "__main__":

    test_resumes = [
        "B.Tech in Computer Science from ABC University.",
        "Completed M.Tech in Artificial Intelligence.",
        "MBA graduate with 2 years of experience.",
        "Bachelor of Science in Mathematics.",
        "Diploma in Computer Engineering.",
        "Class 12 from XYZ School.",
        "B.Tech in CSE and MBA in Business Administration."
    ]

    print("\n===== EDUCATION EXTRACTION TEST =====")

    for resume in test_resumes:
        education = extract_education(resume)

        print(f"\nResume: {resume}")
        print(f"Detected education: {education}")