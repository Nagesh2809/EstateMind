

from Nodes.graph_state import AgentState
from typing import Literal


def classifier_cond_edge(state: AgentState) -> Literal["query", "hitl", "greet"]:

    route = state["route"]

    if route == "query":
        return "query"

    elif route == "hitl":
        return "hitl"

    elif route == "greet":
        return "greet"

    else:
        raise ValueError(f"Unknown route: {route}")