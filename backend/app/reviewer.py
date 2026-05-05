import os
import re
import math
from collections import Counter

from pypdf import PdfReader
from docx import Document


STOP_WORDS = {
    "the", "and", "for", "with", "from", "this", "that", "into", "are", "was",
    "were", "been", "have", "has", "had", "will", "shall", "can", "could",
    "file", "chapter", "lecture", "notes", "summary", "assignment", "midterm",
    "final", "project", "course", "student", "university", "page", "example",
    "introduction", "definition", "overview", "topic", "topics", "section"
}


def extract_text_from_pdf(file_path: str) -> str:
    # Extract readable text from the first pages of a PDF file.
    text = ""

    try:
        reader = PdfReader(file_path)
        for page in reader.pages[:10]:
            text += page.extract_text() or ""
            text += "\n"
    except Exception:
        return ""

    return text


def extract_text_from_docx(file_path: str) -> str:
    # Extract readable text from DOCX paragraphs.
    try:
        document = Document(file_path)
        paragraphs = [p.text for p in document.paragraphs[:100]]
        return "\n".join(paragraphs)
    except Exception:
        return ""


def extract_file_text(file_path: str) -> str:
    # Choose extraction method by file type.
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        return extract_text_from_pdf(file_path)

    if ext == ".docx":
        return extract_text_from_docx(file_path)

    return ""


def normalize_text(text: str) -> str:
    # Normalize text before analysis.
    text = text.lower()
    text = re.sub(r"[_\-]+", " ", text)
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def tokenize(text: str) -> list:
    # Convert text into useful keywords.
    words = normalize_text(text).split()

    return [
        word for word in words
        if len(word) >= 3 and word not in STOP_WORDS
    ]


def cosine_similarity(counter_a: Counter, counter_b: Counter) -> float:
    # Calculate cosine similarity between two word frequency vectors.
    common_words = set(counter_a.keys()).intersection(counter_b.keys())

    dot_product = sum(counter_a[word] * counter_b[word] for word in common_words)

    norm_a = math.sqrt(sum(value * value for value in counter_a.values()))
    norm_b = math.sqrt(sum(value * value for value in counter_b.values()))

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot_product / (norm_a * norm_b)


def build_course_profile(course_name: str) -> Counter:
    # Build a small dynamic profile from the course name only.
    course_words = tokenize(course_name)

    profile = Counter()

    for word in course_words:
        # Give course title words a strong weight.
        profile[word] += 5

        # Add simple singular/plural support.
        if word.endswith("s") and len(word) > 4:
            profile[word[:-1]] += 3
        else:
            profile[word + "s"] += 2

    return profile


def build_file_profile(file_text: str, file_path: str) -> Counter:
    # Build profile from file content first, then filename as small support.
    content_words = tokenize(file_text)

    # Limit repeated words so one repeated word does not dominate the decision.
    content_counter = Counter(content_words)
    profile = Counter()

    for word, count in content_counter.items():
        profile[word] += min(count, 8)

    # Filename is only a helper.
    filename = os.path.splitext(os.path.basename(file_path))[0]
    filename_words = tokenize(filename)

    for word in filename_words:
        profile[word] += 2

    return profile


def get_direct_matches(course_name: str, file_text: str, file_path: str) -> list:
    # Get direct keyword matches between course title and file content/name.
    course_words = set(tokenize(course_name))

    file_words = set(tokenize(file_text))
    filename = os.path.splitext(os.path.basename(file_path))[0]
    filename_words = set(tokenize(filename))

    return sorted(course_words.intersection(file_words.union(filename_words)))


def review_file_content(file_path: str, course_name: str):
    """
    Dynamic content-based review algorithm.

    It does not require manual keywords for each course.

    It checks:
    1. Readable file content.
    2. Similarity between course name and file content.
    3. Direct keyword matches.
    4. Filename as a small helper only.
    """

    file_text = extract_file_text(file_path)

    if not file_text or len(file_text.strip()) < 80:
        return "pending_review", "Could not read enough file content"

    course_profile = build_course_profile(course_name)
    file_profile = build_file_profile(file_text, file_path)

    if not course_profile:
        return "pending_review", "Course name is not clear"

    similarity = cosine_similarity(course_profile, file_profile)
    direct_matches = get_direct_matches(course_name, file_text, file_path)

    # Exact course name inside content is a very strong signal.
    clean_course = normalize_text(course_name)
    clean_text = normalize_text(file_text)

    exact_course_found = clean_course and clean_course in clean_text

    if exact_course_found:
        return (
            "approved",
            f"File content contains the exact course name. Similarity: {similarity:.2f}"
        )

    # Strong approval:
    # Similarity is enough and at least one direct course keyword appears.
    if similarity >= 0.18 and len(direct_matches) >= 1:
        return (
            "approved",
            f"File content matches the course. Similarity: {similarity:.2f}. Matches: {', '.join(direct_matches)}"
        )

    # Medium case: send to admin.
    if similarity >= 0.08 or len(direct_matches) == 1:
        return (
            "pending_review",
            f"File partially matches the course. Similarity: {similarity:.2f}. Matches: {', '.join(direct_matches) or 'None'}"
        )

    # Weak relation: reject.
    return (
        "rejected",
        f"File content does not match the selected course. Similarity: {similarity:.2f}"
    )