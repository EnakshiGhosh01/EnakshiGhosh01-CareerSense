import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def clean_text(text):
    """
    Basic text cleaning for similarity calculation.
    """

    if not text:
        return ""

    text = str(text).lower()

    # Replace non-alphanumeric characters with spaces
    text = re.sub(r"[^a-z0-9+#.\s]", " ", text)

    # Remove extra spaces
    text = re.sub(r"\s+", " ", text).strip()

    return text


def calculate_text_similarity(resume_text, job_text):
    """
    Calculate TF-IDF cosine similarity between
    resume text and job text.

    Returns a value between 0 and 1.
    """

    resume_text = clean_text(resume_text)
    job_text = clean_text(job_text)

    if not resume_text or not job_text:
        return 0.0

    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2)
    )

    try:

        tfidf_matrix = vectorizer.fit_transform(
            [resume_text, job_text]
        )

        similarity = cosine_similarity(
            tfidf_matrix[0:1],
            tfidf_matrix[1:2]
        )[0][0]

        return round(float(similarity), 4)

    except ValueError:

        return 0.0


if __name__ == "__main__":

    resume = """
    Python developer with experience in machine learning,
    pandas, numpy, SQL and data analysis.
    """

    job = """
    We are looking for a Python developer with knowledge
    of machine learning, SQL, pandas and data analysis.
    """

    similarity = calculate_text_similarity(
        resume,
        job
    )

    print("\n===== TEXT SIMILARITY TEST =====")

    print(f"Similarity Score: {similarity}")

    print(
        f"Similarity Percentage: "
        f"{similarity * 100:.2f}%"
    )