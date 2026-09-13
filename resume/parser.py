import io

from pypdf import PdfReader
from docx import Document


def extract_text_from_pdf(file_bytes):
    """
    Extract text from a PDF resume.
    """

    pdf_file = io.BytesIO(file_bytes)

    reader = PdfReader(pdf_file)

    text = []

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text.append(page_text)

    return "\n".join(text)


def extract_text_from_docx(file_bytes):
    """
    Extract text from a DOCX resume.
    """

    docx_file = io.BytesIO(file_bytes)

    document = Document(docx_file)

    paragraphs = []

    for paragraph in document.paragraphs:

        if paragraph.text.strip():
            paragraphs.append(
                paragraph.text.strip()
            )

    return "\n".join(paragraphs)


def extract_resume_text(uploaded_file):
    """
    Extract text from an uploaded PDF or DOCX resume.

    Parameters
    ----------
    uploaded_file :
        Streamlit UploadedFile object.

    Returns
    -------
    str
        Extracted resume text.
    """

    file_name = uploaded_file.name.lower()

    file_bytes = uploaded_file.getvalue()

    if file_name.endswith(".pdf"):

        return extract_text_from_pdf(
            file_bytes
        )

    elif file_name.endswith(".docx"):

        return extract_text_from_docx(
            file_bytes
        )

    else:

        raise ValueError(
            "Unsupported resume format. "
            "Please upload a PDF or DOCX file."
        )


if __name__ == "__main__":

    print(
        "Resume parser module loaded successfully."
    )