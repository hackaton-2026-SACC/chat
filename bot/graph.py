from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from typing import Annotated, TypedDict
from core.config import settings

class State(TypedDict):
    messages: Annotated[list, add_messages]

# Initialize the model with the API key from settings
llm = ChatOpenAI(api_key=settings.openai_api_key, model="gpt-4o-mini") if settings.openai_api_key else None

def chatbot(state: State):
    if not llm:
        return {"messages": [{"role": "ai", "content": "OpenAI API Key is not configured."}]}
    return {"messages": [llm.invoke(state["messages"])]}

graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)

app_graph = graph_builder.compile()
