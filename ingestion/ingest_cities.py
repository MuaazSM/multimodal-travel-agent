import io
import os
import re
from typing import Dict
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
import chromadb

#function to load pdfs
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

#extracting text from the pdfs
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

#cleaning the text using regex
def clean_city_text(raw_city_text):
    cleaned: Dict[str, str] = {}
    for city, text in raw_city_text.items():
        normalized = text.replace("\r", "\n")
        normalized = re.sub(r"\n{2,}", "\n\n", normalized)  # keeping paragraph breaks
        normalized = re.sub(r"[ \t]+", " ", normalized)
        normalized = re.sub(r"(\w)-\s+(\w)", r"\1\2", normalized)
        normalized = re.sub(r"[^\x09\x0A\x0D\x20-\x7E]", " ", normalized)
        normalized = normalized.strip()
        cleaned[city] = normalized
    return cleaned
#chunking the text to store in db with overlaps for each chunks
def chunk_city_text(cleaned_city_text):
    splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size = 500,
        chunk_overlap = 50,
    )
    chunked = {}
    for city, text in cleaned_city_text.items():
        chunks = splitter.split_text(text)
        chunked[city] = chunks
        print(f"{city.title()}: {len(chunks)} chunks")
    return chunked 

# creating the vector embeddings
def create_embeddings(chunks, model_name = "all-MiniLM-L6-v2"):
    model = SentenceTransformer(model_name)
    embedding_dict = {}
    for city, city_chunks in chunks.items():
        embeddings = model.encode(city_chunks, show_progress_bar = True)
        embedding_dict[city] = embeddings

    return embedding_dict, model

# storing the vector embeddings in chromadb
def store_in_chromadb(chunks, embedding_dict, persist_dir = "storage/chroma"):
    client = chromadb.PersistentClient(path = persist_dir)
    collection = client.get_or_create_collection(name = "cities")

    for city, city_chunks in chunks.items():
        city_embeddings = embedding_dict[city]
        ids = [f"{city}_{i}" for i in range(len(city_chunks))]
        metadatas = [{"city": city, "chunk_index": i} for i in range(len(city_chunks))]

        # ensure idempotent writes
        collection.delete(ids=ids)
        
        collection.add(
            ids=ids,
            embeddings= city_embeddings.tolist(),
            documents=city_chunks,
            metadatas=metadatas
        )
        print(f"{city.title()}: {len(city_chunks)} chunks stored")

    return collection

def ingest_pipeline(data_dir = "data/sources", persist_dir = "storage/chroma"):
    pdf_streams = load_city_pdfs(data_dir)  #load
    raw_text = extract_pdf_text(pdf_streams)    #extract raw text
    cleaned_text = clean_city_text(raw_text)    #clean the raw text
    chunks = chunk_city_text(cleaned_text)      #chunk the text
    embeddings_dict, model = create_embeddings(chunks)  #embed the text
    collection = store_in_chromadb(chunks, embeddings_dict, persist_dir)    #store in chroma db
    return collection, model

if __name__ == "__main__":
    collection, model = ingest_pipeline()