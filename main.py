# from Nodes.graph import create_graph

# graph = create_graph()
# print(graph.get_graph().draw_ascii())
# config = {
#     "configurable": {
#         "thread_id": "user-123"
#     }
# }

# result = graph.invoke(
#     {
#         "user_input": "yes",
#         "query_type": "",
#         "response": "",
#         "messages": []
#     },
#     config=config
# )

# print(result)





from fastapi import FastAPI
from pydantic import BaseModel
# from Nodes.graph_state import AgentState
from Nodes.graph import create_graph 


app = FastAPI(
                title="EstateMind Real Estate Agent",
                version="1.0.0"
            )




class ChatRequest(BaseModel):

    user_name: str
    user_question: str




class ChatResponse(BaseModel):

    response: str


# graph = graph()
graph = create_graph()
print(graph.get_graph().draw_ascii())



@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    {
  "user_name": "Nagesh",\n
  "user_question": "properties in Yapral"\n
  "user_question": "within budget of 10 crore"
}
"""

    config = {
                "configurable": {
                    "thread_id": request.user_name
                }
            }
    
    snapshot = graph.get_state(config)
    previous_state = snapshot.values
    conversation_history = previous_state.get("conversation_history", [])


    state = {
                "user_name": request.user_name,
                "user_input": request.user_question,
                "route": "",
                "response": "",
                "conversation_history": conversation_history
            }



    # result = await graph().ainvoke(state, config=config)
    result = await graph.ainvoke(state, config=config)


    return {
        "response": result["response"]
    }

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
                    "main:app",
                    host="0.0.0.0",
                    port=8000,
                    reload=True
                )