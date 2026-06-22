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

    current_intent = state.get("intent", "")

    # check if user wants to exit current flow
    exit_phrases = ["cancel", "stop", "exit", "quit", "never mind", "actually"]

    user_wants_to_exit = any(
        phrase in user_message.lower()
        for phrase in exit_phrases
    )

    # if mid-booking flow — continue booking UNLESS user wants to exit
    if current_intent == "book" and not user_wants_to_exit and (
        "appointment_date" not in state or
        "available_slots" not in state or
        "selected_slot" not in state or
        "patient_name" not in state or
        "user_email" not in state
    ):
        state["intent"] = "book"
        return state

    # if mid-cancel flow — continue cancel UNLESS user wants to exit
    if current_intent == "cancel" and not user_wants_to_exit and (
        "cancel_booking_id" not in state
    ):
        state["intent"] = "cancel"
        return state

    # # if mid-booking flow — continue booking
    # if current_intent == "book" and (
    #     "appointment_date" not in state or
    #     "available_slots" not in state or
    #     "selected_slot" not in state or
    #     "patient_name" not in state or
    #     "user_email" not in state
    # ):
    #     state["intent"] = "book"
    #     return state

    # # if mid-cancel flow — continue cancel
    # if current_intent == "cancel" and (
    #     "cancel_booking_id" not in state
    # ):
    #     state["intent"] = "cancel"
    #     return state


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

    # -----------------------------
    # Reset old workflow if changed
    # -----------------------------

    if intent != current_intent:


        state.pop("appointment_date", None)

        state.pop("available_slots", None)

        state.pop("selected_slot", None)

        state.pop("patient_name", None)

        state.pop("user_email", None)

        state.pop(
            "cancel_booking_id",
            None,
        )

        state.pop(
            "appointment_cancelled",
            None,
        )    


    # save intent into state
    state["intent"] = intent


    # logging
    logger.info(
        f"Intent detected: {intent} "
        f"for message: {user_message[:50]}"
    )


    return state