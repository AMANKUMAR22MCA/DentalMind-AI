from langchain_core.messages import AIMessage
from langchain_groq import ChatGroq

from app.agent.state import AgentState
from app.core.config import get_settings


settings = get_settings()


# Load once at module level
llm = ChatGroq(
    model=settings.GROQ_MODEL,
    api_key=settings.GROQ_API_KEY,
)


async def chat_node(
    state: AgentState,
) -> AgentState:
    """
    Handles normal friendly conversation.
    Example:
    hello, thanks, who are you
    """


    # -----------------------------
    # 1. Get latest user message
    # -----------------------------

    user_message = (
        state["messages"][-1].content
    )


    # -----------------------------
    # 2. Create chat prompt
    # -----------------------------

    prompt = f"""
You are DentalMind, a friendly dental clinic assistant.

Rules:
- Reply naturally and politely
- Keep answers short
- Help users with clinic related conversations
- If they need appointments, tell them you can help book one


User message:
{user_message}
"""


    # -----------------------------
    # 3. Call Groq
    # -----------------------------

    response = await llm.ainvoke(
        prompt
    )


    # -----------------------------
    # 4. Save AI reply into state
    # -----------------------------

    state["messages"].append(

        AIMessage(
            content=response.content
        )

    )


    return state