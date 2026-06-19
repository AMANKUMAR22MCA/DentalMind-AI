from typing import TypedDict, NotRequired
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    """
    Shared memory/state for the DentalMind agent conversation.

    Every graph node reads from and writes to this state.
    """

    # complete conversation history
    messages: list[BaseMessage]

    # user intent:
    # faq | book | cancel | chat
    intent: str

    # slots fetched from database
    available_slots: NotRequired[list]

    # appointment slot selected by user
    selected_slot: NotRequired[dict]

    # patient's email for confirmation
    user_email: NotRequired[str]

    # booking confirmation status
    confirmed: NotRequired[bool]