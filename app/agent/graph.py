from langgraph.graph import StateGraph, END

from app.agent.state import AgentState
from app.agent.router import router_node
from app.agent.nodes.rag import rag_node

# -----------------------------
# Placeholder Nodes
# -----------------------------

# async def rag_node(
#     state: AgentState,
# ) -> AgentState:
#     print("RAG NODE CALLED")
#     return state


async def book_node(
    state: AgentState,
) -> AgentState:
    print("BOOK NODE CALLED")
    return state


async def cancel_node(
    state: AgentState,
) -> AgentState:
    print("CANCEL NODE CALLED")
    return state


async def chat_node(
    state: AgentState,
) -> AgentState:
    print("CHAT NODE CALLED")
    return state


# -----------------------------
# Router Decision
# -----------------------------

def decide_next_node(
    state: AgentState,
) -> str:
    return state["intent"]


# -----------------------------
# Build Graph
# -----------------------------

graph = StateGraph(
    AgentState
)


# add nodes

graph.add_node(
    "router",
    router_node
)

graph.add_node(
    "rag",
    rag_node
)

graph.add_node(
    "book",
    book_node
)

graph.add_node(
    "cancel",
    cancel_node
)

graph.add_node(
    "chat",
    chat_node
)


# starting point

graph.set_entry_point(
    "router"
)


# router decision

graph.add_conditional_edges(
    "router",
    decide_next_node,
    {
        "faq": "rag",
        "book": "book",
        "cancel": "cancel",
        "chat": "chat",
    }
)


# finish after each node

graph.add_edge(
    "rag",
    END
)

graph.add_edge(
    "book",
    END
)

graph.add_edge(
    "cancel",
    END
)

graph.add_edge(
    "chat",
    END
)


# compile

dental_graph = graph.compile()