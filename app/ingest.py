# app/ingest.py

from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings

from app.core.database import AsyncSessionLocal
from app.models import ClinicDoc

BASE_DIR = Path(__file__).resolve().parent.parent

async def ingest_documents(file_path: str) -> int:
    """
    Read a text file, split into chunks,
    generate embeddings, and store in PostgreSQL.
    """

    # Resolve path relative to project root
    path = BASE_DIR / file_path

    # 1. Read file
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    # 2. Split into chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        length_function=len,
    )

    chunks = splitter.split_text(text)

    if not chunks:
        print("No chunks generated.")
        return 0

    # 3. Generate embeddings
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vectors = embeddings.embed_documents(chunks)

    # Validate counts
    if len(chunks) != len(vectors):
        raise ValueError(
            f"Chunk count ({len(chunks)}) "
            f"does not match vector count ({len(vectors)})"
        )

    # 4. Store in PostgreSQL
    async with AsyncSessionLocal() as session:
        docs = [
            ClinicDoc(
                content=chunk,
                source=path.name,
                embedding=vector,
            )
            for chunk, vector in zip(chunks, vectors)
        ]

        session.add_all(docs)
        await session.commit()

    print(f"Inserted {len(chunks)} chunks from {path.name}")
    return len(chunks) 