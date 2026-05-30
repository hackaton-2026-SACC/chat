from fastapi import FastAPI
from pydantic import BaseModel
from bot.graph import app_graph
from langchain_core.messages import HumanMessage

app = FastAPI(title="Chatbot API")

class ChatRequest(BaseModel):
    request_id: str
    text: str

class ChatResponse(BaseModel):
    request_id: str
    response: str

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    # Pass the user's text to LangGraph
    state = {"messages": [HumanMessage(content=request.text)]}
    final_state = app_graph.invoke(state)
    
    # Extract the last message from the chatbot
    response_message = final_state["messages"][-1]
    
    # Handle dict (when API key is missing) or AIMessage
    if isinstance(response_message, dict):
        response_text = response_message.get("content", "")
    else:
        response_text = response_message.content
    
    return ChatResponse(
        request_id=request.request_id,
        response=response_text
    )
