import os
import re
from pypdf import PdfReader
from docx import Document


def extract_text_from_pdf(file_path: str) -> str:
    # Extract readable text from a PDF file.
    text = ""

    try:
        reader = PdfReader(file_path)
        for page in reader.pages:
            text += page.extract_text() or ""
    except Exception:
        return ""

    return text

 
def extract_text_from_docx(file_path: str) -> str:
    # Extract readable text from a DOCX file.
    try:
        document = Document(file_path)
        return "\n".join(paragraph.text for paragraph in document.paragraphs)
    except Exception:
        return ""


def extract_file_text(file_path: str) -> str:
    # Extract text based on file extension.
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        return extract_text_from_pdf(file_path)

    if ext == ".docx":
        return extract_text_from_docx(file_path)

    return ""


def normalize_text(text: str) -> str:
    # Normalize text for simple keyword matching.
    text = text.lower()
    text = re.sub(r"[^a-z0-9\u0600-\u06FF\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def review_file_content(file_path: str, course_name: str):
    # Review the uploaded file and decide if it should be approved, rejected, or sent to admin review.
    text = extract_file_text(file_path)

    # If the system cannot read the file content, send it to admin review.
    if not text or len(text.strip()) < 30:
        return "pending_review", "Could not read enough file content"

    clean_text = normalize_text(text)
    clean_course = normalize_text(course_name)

    # Split course name into useful keywords.
    course_words = [
        word for word in clean_course.split()
        if len(word) >= 3
    ]

    # If the full course name appears in the file, approve it.
    if clean_course and clean_course in clean_text:
        return "approved", "File content matches the course name"

    # Count matched course keywords.
    matched_words = [
        word for word in course_words
        if word in clean_text
    ]

    if not course_words:
        return "pending_review", "Course keywords are not clear"

    score = len(matched_words) / len(course_words)

    # Strong match: approve automatically.
    if score >= 0.7:
        return "approved", "File content strongly matches the course"

    # Weak match: reject automatically.
    if score <= 0.2:
        return "rejected", "File content does not match the selected course"

    # Medium match: send to admin review.
    return "pending_review", "File content partially matches the course"