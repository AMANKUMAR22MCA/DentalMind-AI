import json

from typing import Any

from redis.asyncio import Redis

from langchain_core.messages import (
    messages_from_dict,
    messages_to_dict,
)

from app.agent.state import AgentState
from app.core.config import get_settings


settings = get_settings()


# -----------------------------
# Redis connection
# -----------------------------

redis_client = Redis.from_url(
    settings.REDIS_URL,
    decode_responses=True,
)


# -----------------------------
# Save conversation state
# -----------------------------

async def save_state(
    session_id: str,
    state: AgentState,
) -> None:
    """
    Save LangGraph state into Redis.
    """


    # Convert LangChain messages
    # HumanMessage / AIMessage
    # into JSON serializable dict

    state_data: dict[str, Any] = dict(state)


    state_data["messages"] = messages_to_dict(
        state["messages"]
    )


    await redis_client.set(

        name=session_id,

        value=json.dumps(
            state_data,
            default=str,
        ),

        ex=3600,   # 1 hour expiry

    )



# -----------------------------
# Load conversation state
# -----------------------------

async def load_state(
    session_id: str,
) -> AgentState | None:
    """
    Load previous conversation state.
    """


    data = await redis_client.get(
        session_id
    )


    if data is None:

        return None


    state_data = json.loads(
        data
    )


    # Convert dict back into:
    # HumanMessage
    # AIMessage

    state_data["messages"] = messages_from_dict(

        state_data["messages"]

    )


    return state_data