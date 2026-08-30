from Nodes.graph_state import AgentState
from Nodes.cond_edge import classifier_cond_edge
from Nodes.router import router_node as query_classifier
from Nodes.query_data import query_node
from Nodes.hitl import hitl_node
from Nodes.greet import greet_node

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver


def create_graph():
    """
    Creates and returns the compiled LangGraph.
    """


    builder = StateGraph(AgentState)


    builder.add_node("classifier", query_classifier)
    builder.add_node("get_data", query_node)
    builder.add_node("hitl", hitl_node)
    builder.add_node("greet", greet_node)

    builder.add_edge(START,"classifier")


    builder.add_conditional_edges(
                                    "classifier",
                                    classifier_cond_edge,
                                    {
                                        "query": "get_data",
                                        "hitl": "hitl",
                                        "greet": "greet",
                                    }
                                )


    builder.add_edge("get_data", END)
    builder.add_edge("hitl", END)
    builder.add_edge("greet", END)



    memory = MemorySaver()


    graph = builder.compile(
        checkpointer=memory
    )

    return graph