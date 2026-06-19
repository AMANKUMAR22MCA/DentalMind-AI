from sqlalchemy import select

from langchain_core.messages import AIMessage
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq

from app.agent.state import AgentState
from app.models import ClinicDoc
from app.core.database import AsyncSessionLocal
from app.core.config import get_settings


settings = get_settings()


# Load embedding model once
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


# Load LLM client once
llm = ChatGroq(
    model=settings.GROQ_MODEL,
    api_key=settings.GROQ_API_KEY,
)


async def rag_node(
    state: AgentState,
) -> AgentState:


    # ---------------------------
    # 1. Get user question
    # ---------------------------

    question = (
        state["messages"][-1].content
    )


    # ---------------------------
    # 2. Embed question
    # ---------------------------

    query_vector = embeddings.embed_query(
        question
    )


    # ---------------------------
    # 3. Search pgvector DB
    # ---------------------------

    async with AsyncSessionLocal() as session:

        stmt = (
            select(ClinicDoc)
            .order_by(
                ClinicDoc.embedding.op("<->")(
                    query_vector
                )
            )
            .limit(3)
        )


        result = await session.execute(
            stmt
        )


        docs = (
            result.scalars().all()
        )


    # ---------------------------
    # 4. Handle no docs
    # ---------------------------

    if not docs:

        state["messages"].append(
            AIMessage(
                content="I don't have enough clinic information."
            )
        )

        return state


    # ---------------------------
    # 5. Create context
    # ---------------------------

    context = "\n\n".join(
        doc.content
        for doc in docs
    )


    # ---------------------------
    # 6. Strict RAG prompt
    # ---------------------------

    prompt = f"""
You are DentalMind clinic assistant.

Answer ONLY using the context below.
Do not use your own knowledge.

If the answer is not in context, say:
"I don't have enough clinic information."


Context:
{context}


Question:
{question}
"""


    # ---------------------------
    # 7. Call Groq
    # ---------------------------

    response = await llm.ainvoke(
        prompt
    )


    answer = response.content


    # ---------------------------
    # 8. Save AI answer in memory
    # ---------------------------

    state["messages"].append(

        AIMessage(
            content=answer
        )

    )


    return state