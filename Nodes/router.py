

from Nodes.graph_state import AgentState
from langchain_core.prompts import ChatPromptTemplate
from datetime import datetime
from Nodes.llm_ import llm
import os
import json
from dotenv import load_dotenv
load_dotenv()



def router_node(state: AgentState):
    
    print("\n ------------------------------------------------      In classifier_node")
    user_question = state["user_input"].lower()
    user_name = state.get("user_name", "Nagesh")
    conversation_history = state.get("conversation_history", [])
    conversation_history_json = json.dumps(
                                                conversation_history,
                                                indent=2,
                                                ensure_ascii=False
                                            )
    print("\n\n--------------------History- In Classifier----------------------------")
    print(conversation_history_json)
    print("\n\n-------------------------------------------------")



    ESTATEMIND_PROMPT = """
    You are an intent classifier for a Real Estate AI Assistant.

    Classify the CURRENT USER MESSAGE into exactly ONE of:

    greet
    query
    hitl


    RULES:

    1. GREET
    Return `greet` if the user is:
    - Greeting
    - Having casual/friendly conversation
    - Saying thanks or goodbye
    - Asking a general question about the assistant
    - Not asking for a real-estate operation

    Examples:
    "Hi" → greet
    "How are you?" → greet
    "Who created you?" → greet
    "Thanks" → greet


    2. QUERY
    Return `query` if the user has a real-estate-related request AND
    the required information is available either:

    - In the current user message, OR
    - In the previous conversation history.

    The required information may include:
    - Location/locality
    - Budget
    - Property type
    - BHK
    - Metro station
    - IT hub
    - RERA approval
    - Project name
    - Area
    - Or any other information necessary to understand the user's request.

    A follow-up question is `query` if its missing information can be
    clearly understood from the conversation history.

    Example:

    History:
    User: "Show me properties in Gachibowli."
    Assistant: "Here are the properties."

    Current:
    "Under 80 lakhs"

    → query


    3. HITL
    Return `hitl` if the user has a real-estate-related request BUT
    the request is incomplete or ambiguous AND the missing information
    cannot be obtained from the conversation history.

    Examples:

    "Show me properties in my budget"
    → hitl

    "Find properties near a metro"
    → hitl

    "Show me apartments"
    → hitl

    "Find something affordable"
    → hitl

    "Show me properties"
    → hitl

    "What is the price?"
    → hitl


    IMPORTANT:

    - Always check the conversation history before deciding `hitl`.
    - If the current message depends on previous conversation information
    and that information exists in the history → `query`.
    - If the required information does not exist in either the current
    message or history → `hitl`.
    - Do not invent or assume missing information.
    - If the user changes the topic, do not incorrectly reuse unrelated
    information from the history.
    - A greeting combined with a complete real-estate request should be
    classified based on the real-estate request.

    Example:
    "Hi, show me properties in Gachibowli under 80 lakhs"
    → query


    CONVERSATION HISTORY:
    {conversation_history}


    CURRENT USER MESSAGE:
    {user_message}


    OUTPUT:
    Return ONLY ONE exact value:

    greet
    query
    hitl

    Do not provide explanations, reasoning, JSON, markdown, or any other text.
    """



    prompt = ChatPromptTemplate.from_template(
                                                    ESTATEMIND_PROMPT
                                                )


    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    prompt = prompt.partial(
                                user_name=user_name,
                                current_time=current_time,
                                conversation_history = conversation_history_json
                            )



    chain = prompt | llm

    response = chain.invoke(
                                {
                                    "user_message": user_question,
                                }
                            )

    print("-------------------------------------------------\n\n")
    print(response.content)
    print(response.response_metadata)
    print("\n\n-------------------------------------------------")
    # print(response.content)
    

    


    return {
        "route": response.content
        # "route": "query"
    }