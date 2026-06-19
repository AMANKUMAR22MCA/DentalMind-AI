# app/ingest.py

from pathlib import Path
import hashlib

from sqlalchemy import select

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings

from app.core.database import AsyncSessionLocal
from app.models import ClinicDoc


BASE_DIR = Path(__file__).resolve().parent.parent


# load once
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


def calculate_file_hash(path: Path) -> str:
    """
    Generate SHA256 hash based on file content.
    Same content = same hash
    """

    file_bytes = path.read_bytes()

    return hashlib.sha256(
        file_bytes
    ).hexdigest()


async def ingest_documents(file_path: str) -> int:
    """
    Read file,
    avoid duplicate content,
    split chunks,
    generate embeddings,
    save vectors.
    """

    path = BASE_DIR / file_path


    # --------------------------------
    # 1. Calculate file hash
    # --------------------------------

    file_hash = calculate_file_hash(path)


    async with AsyncSessionLocal() as session:


        # --------------------------------
        # 2. Duplicate check by CONTENT
        # --------------------------------

        existing = await session.execute(

            select(ClinicDoc)
            .where(
                ClinicDoc.file_hash == file_hash
            )
            .limit(1)

        )


        if existing.scalars().first():

            print(
                f"{path.name} already ingested — skipping"
            )

            return 0


        # --------------------------------
        # 3. Read file
        # --------------------------------

        with open(
            path,
            "r",
            encoding="utf-8",
        ) as f:

            text = f.read()


        # --------------------------------
        # 4. Split chunks
        # --------------------------------

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            length_function=len,
        )


        chunks = splitter.split_text(
            text
        )


        if not chunks:

            print(
                "No chunks generated."
            )

            return 0


        # --------------------------------
        # 5. Embeddings
        # --------------------------------

        vectors = embeddings.embed_documents(
            chunks
        )


        if len(chunks) != len(vectors):

            raise ValueError(
                "Chunks and vectors mismatch"
            )


        # --------------------------------
        # 6. Insert chunks
        # --------------------------------

        docs = [

            ClinicDoc(

                content=chunk,

                source=path.name,

                file_hash=file_hash,

                embedding=vector,

            )

            for chunk, vector in zip(
                chunks,
                vectors,
            )

        ]


        session.add_all(
            docs
        )


        await session.commit()


    print(
        f"Inserted {len(chunks)} chunks from {path.name}"
    )


    return len(chunks)