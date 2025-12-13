import io
import os
import re
from typing import Dict

from pypdf import PdfReader


def load_city_pdfs(data_dir = "data/sources"):
    cities = {
        "paris": os.path.join(data_dir, "paris.pdf"),
        "tokyo": os.path.join(data_dir, "tokyo.pdf"),
        "new_york": os.path.join(data_dir, "new_york.pdf"),
    }

    pdf_streams= {}
    for city, path in cities.items():
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Missing PDF for {city} at {path}")
        with open(path, "rb") as f:
            pdf_streams[city] = f.read()
    return pdf_streams


def extract_pdf_text(pdf_streams):
    extracted: Dict[str, str] = {}
    for city, stream in pdf_streams.items():
        reader = PdfReader(io.BytesIO(stream))
        pages = []
        for page in reader.pages:
            page_text = page.extract_text() or ""
            pages.append(page_text)
        extracted[city] = "\n".join(pages)
    return extracted


def clean_city_text(raw_city_text):
    cleaned: Dict[str, str] = {}
    for city, text in raw_city_text.items():
        normalized = text.replace("\r", "\n")
        normalized = re.sub(r"\s+", " ", normalized)
        normalized = re.sub(r"(\w)-\s+(\w)", r"\1\2", normalized)
        normalized = re.sub(r"[^\x09\x0A\x0D\x20-\x7E]", " ", normalized)
        normalized = normalized.strip()
        cleaned[city] = normalized
    return cleaned

