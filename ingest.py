"""
ingest.py
Handles PDF loading, text extraction, chunking, and metadata enrichment.
"""

import os
import re
from pathlib import Path
from typing import List, Tuple

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

from vectorstore import add_documents_to_vectorstore, get_embeddings


PDF_DIR = "./data/pdfs"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 100


def extract_lead_name(text: str, filename: str) -> str:
    """
    Attempt to infer the lead's name from transcript text.
    Looks for patterns like 'Lead:', 'Client:', 'Customer:', or 'with [Name]'.
    Falls back to the PDF filename stem.
    """
    patterns = [
        r"(?:Lead|Client|Customer|Prospect)\s*[:\-]\s*([A-Z][a-z]+ [A-Z][a-z]+)",
        r"(?:speaking with|call with|meeting with)\s+([A-Z][a-z]+ [A-Z][a-z]+)",
        r"^([A-Z][a-z]+ [A-Z][a-z]+)\s*[:\-]",  # Name at line start
    ]
    for pattern in patterns:
        match = re.search(pattern, text[:2000], re.MULTILINE)
        if match:
            return match.group(1).strip()

    # Fall back to filename without extension, cleaned up
    stem = Path(filename).stem.replace("_", " ").replace("-", " ").title()
    return stem


def load_pdfs(pdf_dir: str = PDF_DIR) -> List[Tuple[str, str, str]]:
    """
    Load all PDFs from a directory.
    Returns a list of (filename, full_text, lead_name) tuples.
    """
    pdf_path = Path(pdf_dir)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF directory not found: {pdf_dir}")

    pdf_files = list(pdf_path.glob("*.pdf"))
    if not pdf_files:
        raise ValueError(f"No PDF files found in {pdf_dir}")

    loaded = []
    for pdf_file in pdf_files:
        loader = PyPDFLoader(str(pdf_file))
        pages = loader.load()
        full_text = "\n".join(page.page_content for page in pages)
        lead_name = extract_lead_name(full_text, pdf_file.name)
        loaded.append((pdf_file.name, full_text, lead_name))
        print(f"  ✓ Loaded: {pdf_file.name} → Lead: {lead_name}")

    return loaded


def chunk_documents(
    loaded_docs: List[Tuple[str, str, str]],
) -> List[Document]:
    """
    Split loaded PDF texts into overlapping chunks with metadata.
    Each chunk stores: lead_name, source_pdf, chunk_id.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    all_chunks: List[Document] = []
    for filename, text, lead_name in loaded_docs:
        chunks = splitter.split_text(text)
        for idx, chunk_text in enumerate(chunks):
            doc = Document(
                page_content=chunk_text,
                metadata={
                    "lead_name": lead_name,
                    "source_pdf": filename,
                    "chunk_id": f"{Path(filename).stem}_{idx}",
                },
            )
            all_chunks.append(doc)

    print(f"  ✓ Created {len(all_chunks)} chunks from {len(loaded_docs)} PDFs")
    return all_chunks


def ingest_pdfs(pdf_dir: str = PDF_DIR) -> int:
    """
    Full pipeline: load PDFs → chunk → embed → store in ChromaDB.
    Returns the number of chunks stored.
    """
    print("📂 Loading PDFs...")
    loaded = load_pdfs(pdf_dir)

    print("✂️  Chunking documents...")
    chunks = chunk_documents(loaded)

    print("🔢 Embedding and storing in ChromaDB...")
    embeddings = get_embeddings()
    add_documents_to_vectorstore(chunks, embeddings)

    print(f"✅ Ingestion complete. {len(chunks)} chunks stored.")
    return len(chunks)


if __name__ == "__main__":
    ingest_pdfs()
