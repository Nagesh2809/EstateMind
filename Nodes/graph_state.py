from typing import TypedDict, Literal, List, Dict

class AgentState(TypedDict):
    user_name: str
    user_input: str
    route: str
    response: str
    conversation_history: List[Dict[str, str]]
