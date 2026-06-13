from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq

from app.core.config import get_settings
from app.core.database import get_db
from app.models import ClinicDoc


router = APIRouter()

settings = get_settings()


# -----------------------------
# Pydantic Models
# -----------------------------

class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    answer: str
    sources: List[str]


# -----------------------------
# Embedding Model
# -----------------------------

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


# -----------------------------
# Groq LLM
# -----------------------------

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=settings.GROQ_API_KEY,
)


# -----------------------------
# ASK Endpoint
# -----------------------------

@router.post(
    "/ask",
    response_model=AskResponse,
)
async def ask_question(
    request: AskRequest,
    db: AsyncSession = Depends(get_db),
) -> AskResponse:

    try:
        # 1. Convert user question into vector

        query_vector = embeddings.embed_query(
            request.question
        )


        # 2. Search similar chunks from pgvector

        stmt = (
            select(ClinicDoc)
            .order_by(
                ClinicDoc.embedding.op("<->")(
                    query_vector
                )
            )
            .limit(3)
        )


        result = await db.execute(stmt)

        docs = result.scalars().all()


        if not docs:
            return AskResponse(
                answer="I don't have enough clinic information.",
                sources=[]
            )


        # 3. Create context from database chunks

        context = "\n\n".join(
            doc.content for doc in docs
        )


        sources = list(
            {
                doc.source
                for doc in docs
            }
        )


        # 4. Create strict RAG prompt

        prompt = f"""
You are a dental clinic assistant.

Answer ONLY using the clinic information below.
Do not use outside knowledge.
Do not guess prices, doctors, timings, or services.

If answer is not available say:
"I don't have enough clinic information."


Clinic information:

{context}


Question:

{request.question}
"""


        # 5. Send to Groq LLM

        response = await llm.ainvoke(prompt)


        # 6. Return response

        return AskResponse(
            answer=response.content,
            sources=sources,
        )


    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )