
from Nodes.graph_state import AgentState
from langgraph.types import interrupt


def hitl_node(state: AgentState):

    # Execution pauses here
    user_approval = interrupt(
        {
            "message": "Human approval required.",
            "query": state["user_input"],
            "question": "Do you want me to continue?"
        }
    )

    # Execution resumes after Command(resume=...)
    if user_approval == "yes":
        response = "Human approved. Continuing the workflow."

    else:
        response = "Human rejected the request."

    return {
        "response": response
    }