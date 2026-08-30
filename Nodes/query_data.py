
from Nodes.graph_state import AgentState
from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient

from Nodes.llm_ import llm
from dotenv import load_dotenv
import os
import json
load_dotenv()
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL")


async def query_node(state: AgentState):
    print("\n ------------------------------------------------      In query_node")
    user_question = state["user_input"]
    conversation_history = state.get("conversation_history",[])

    conversation_history_json = json.dumps(
                                                    conversation_history,
                                                    indent=2,
                                                    ensure_ascii=False
                                                )
    print("\n\n--------------------History-----------------------------")
    print(conversation_history_json)
    print("\n\n-------------------------------------------------")
        
    SYSTEM_PROMPT = """
You are EstateMind, an AI-powered real estate assistant for
Reddy Real Estate.

You have access to real estate data through MCP tools.

Your job is to understand the CURRENT USER MESSAGE using the
previous conversation when necessary, call the appropriate MCP
tool, and provide a clear answer based only on the tool results.

========================
CONVERSATION HISTORY
========================

The following is the previous conversation between the user
and EstateMind.

{conversation_history}


========================
CONVERSATION RULES
========================

1. Always consider the previous conversation when understanding
   the current user message.

2. The current user message may be a follow-up question.

3. If the current message is incomplete by itself but its meaning
   can be determined from the conversation history, use the
   information from the history.

Example:

Previous:
User: Show me properties in Gachibowli.
Assistant: Here are some properties.

Current:
User: Under 80 lakhs.

Understand this as:

"Show me properties in Gachibowli under 80 lakhs."

4. If the user changes the topic, do not reuse unrelated information
   from the previous conversation.

5. Never invent or assume missing information.


========================
MCP TOOL RULES
========================

1. Use MCP tools whenever the user asks for real-estate data.

2. Select the most appropriate tool for the user's request.

3. Use the actual tool results to answer the user.

4. Never invent properties, prices, locations, BHKs, projects,
   RERA status, or availability.

5. If a tool returns no matching properties, clearly tell the user
   that no matching properties were found.

6. If a required parameter is missing and cannot be determined
   from the conversation history, ask the user for that information.

7. Do not expose MCP implementation details or internal reasoning.

8. Do not mention tool names to the user.

9. Keep the final answer clear and concise.


========================
REAL ESTATE CONTEXT
========================

Real-estate requests may involve:

- Location / locality
- Budget
- Property type
- BHK
- Area
- Pincode
- Metro station
- IT hub
- RERA approval
- Project name
- Property prices
- Market value
- EMI
- Nearby properties
- Property availability


========================
FINAL RESPONSE
========================

After using the required MCP tools, provide a natural-language
answer to the CURRENT USER.

Do not return JSON unless the user explicitly asks for JSON.
"""


    system_prompt = SYSTEM_PROMPT.format(
                                            conversation_history=conversation_history_json
                                        )

    client = MultiServerMCPClient(
                                    {
                                        "real_estate": {
                                            "transport": "http",
                                            "url": MCP_SERVER_URL,
                                        }
                                    }
                                )
    tools = await client.get_tools()
    agent = create_agent(
                            model=llm,
                            tools=tools,
                            system_prompt=system_prompt
                        )

    result = await agent.ainvoke(
                                    {
                                        "messages": [
                                            {
                                                "role": "user",
                                                "content": user_question
                                            }
                                        ]
                                    }
                                )


    for i, message in enumerate(result["messages"]):

        print("\n" + "=" * 80)
        print(f"MESSAGE {i}")
        print("=" * 80)

        print("TYPE:", type(message).__name__)

        # -------------------------------------
        # Agent -> Tool
        # -------------------------------------

        if hasattr(message, "tool_calls") and message.tool_calls:

            print("\n🔧 TOOL CALL")

            for tool_call in message.tool_calls:

                print("Tool Name:")
                print(tool_call.get("name"))

                print("\nTool Arguments:")
                print(tool_call.get("args"))

                print("\nTool Call ID:")
                print(tool_call.get("id"))

        # -------------------------------------
        # Tool -> Agent
        # -------------------------------------

        if type(message).__name__ == "ToolMessage":

            print("\n📥 TOOL RESULT")

            print("Tool Name:")
            print(getattr(message, "name", None))

            print("\nTool Call ID:")
            print(getattr(message, "tool_call_id", None))

            print("\nTool Output:")
            print(message.content)

        # -------------------------------------
        # Normal AI response
        # -------------------------------------

        if type(message).__name__ == "AIMessage":

            print("\n🤖 AI MESSAGE")

            print("Content:")
            print(message.content)




    # response = result["messages"][-1].content
    final_message = result["messages"][-1]

    content = final_message.content

    if isinstance(content, list):
        response = "".join(
            item.get("text", "")
            for item in content
            if item.get("type") == "text"
        )
    else:
        response = content

    updated_history = list(conversation_history)
    
    updated_history.append(
                                {
                                    "role": "user",
                                    "content": user_question
                                }
                            )

    updated_history.append(
                                {
                                    "role": "assistant",
                                    "content": response
                                }
                            )
    updated_history = updated_history[-10:]


    return {
        "response": response,
        "conversation_history": updated_history
    }