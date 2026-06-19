import logging

from langchain_groq import ChatGroq

from app.agent.state import AgentState
from app.core.config import get_settings


logger = logging.getLogger(__name__)


settings = get_settings()


llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=settings.GROQ_API_KEY,
)


async def router_node(
    state: AgentState,
) -> AgentState:
    """
    Classify user message intent.
    """

    user_message = state["messages"][-1].content


    prompt = f"""
You are an intent classifier for DentalMind.

Classify the message into exactly one:

faq
book
cancel
chat

Rules:
- Reply only one word
- No explanation


Message:

{user_message}
"""


    response = await llm.ainvoke(prompt)


    intent = response.content.strip().lower()


    if intent not in [
        "faq",
        "book",
        "cancel",
        "chat",
    ]:
        intent = "chat"


    # save intent into state
    state["intent"] = intent


    # logging
    logger.info(
        f"Intent detected: {intent} "
        f"for message: {user_message[:50]}"
    )


    return state