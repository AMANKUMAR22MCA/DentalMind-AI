from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from langchain_core.messages import HumanMessage

from app.agent.graph import dental_graph


router = APIRouter()


# -----------------------------
# Request / Response Models
# -----------------------------

class ChatRequest(BaseModel):
    message: str
    session_id: str


class ChatResponse(BaseModel):
    session_id: str
    intent: str
    response: str


# -----------------------------
# Chat Endpoint
# -----------------------------

@router.post(
    "/chat",
    response_model=ChatResponse,
)
async def chat(
    request: ChatRequest,
) -> ChatResponse:

    try:

        # 1. Create initial AgentState

        state = {
            "messages": [
                HumanMessage(
                    content=request.message
                )
            ],

            "intent": "",
        }


        # 2. Run LangGraph

        result = await dental_graph.ainvoke(state)


        # 3. Get latest message

        last_message = (
            result["messages"][-1].content
        )


        # 4. Return response

        return ChatResponse(
            session_id=request.session_id,
            intent=result["intent"],
            response=last_message,
        )


    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error),
        )