from typing import Annotated, TypedDict, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from core.config import settings
from core.db import engine
from sqlalchemy import text

class State(TypedDict):
    messages: Annotated[list, add_messages]
    is_valid_topic: bool
    sql_query: str
    sql_result: str

# Initialize the model with the API key from settings
llm = ChatOpenAI(api_key=settings.openai_api_key, model="gpt-4o-mini", temperature=0) if settings.openai_api_key else None

class TopicCheck(BaseModel):
    is_valid: bool = Field(description="True se a pergunta for sobre licitações, contratos públicos e respeitar os direitos humanos. False caso contrário.")

def check_topic(state: State):
    if not llm:
        return {"messages": [AIMessage(content="OpenAI API Key is not configured.")]}
    
    last_message = state["messages"][-1].content
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Você é um classificador. Analise se a pergunta do usuário é sobre licitações, contratos e compras públicas. Além disso, verifique se a pergunta respeita os direitos humanos (sem conteúdo de ódio ou preconceito). Retorne is_valid=True se a pergunta for relevante sobre o tema e ética. Retorne False caso a pergunta seja sobre qualquer outro assunto, como 'Qual é o atual presidente?'."),
        ("human", "{question}")
    ])
    
    checker_llm = llm.with_structured_output(TopicCheck)
    result = checker_llm.invoke(prompt.format(question=last_message))
    
    if not result.is_valid:
        return {
            "is_valid_topic": False, 
            "messages": [AIMessage(content="Por favor, faça perguntas focadas em licitações e contratos públicos. Assuntos fora desse escopo ou que não respeitem as diretrizes não podem ser respondidos.")]
        }
    
    return {"is_valid_topic": True}

def router_topic(state: State) -> Literal["generate_sql", "__end__"]:
    if not state.get("is_valid_topic", False):
        return "__end__"
    return "generate_sql"

class SQLQuery(BaseModel):
    query: str = Field(description="A instrução de consulta SQL para executar.")

def generate_sql(state: State):
    last_message = state["messages"][-1].content
    
    # Load docs/db.md
    schema_info = ""
    try:
        with open("docs/db.md", "r", encoding="utf-8") as f:
            schema_info = f.read()
    except Exception:
        schema_info = "Documentação do schema não encontrada."

    prompt = ChatPromptTemplate.from_messages([
        ("system", "Você é um especialista em SQL (SQLite). Com base no schema abaixo, gere a consulta SQL correta para responder a pergunta do usuário. Retorne APENAS a query na estrutura pedida.\n\nSchema:\n{schema}"),
        ("human", "{question}")
    ])
    
    sql_llm = llm.with_structured_output(SQLQuery)
    result = sql_llm.invoke(prompt.format(schema=schema_info, question=last_message))
    
    return {"sql_query": result.query}

def execute_sql(state: State):
    query = state.get("sql_query", "")
    if not query:
        return {"sql_result": "Nenhuma consulta gerada."}
    
    try:
        with engine.connect() as conn:
            result = conn.execute(text(query))
            rows = result.fetchall()
            str_rows = [str(dict(row._mapping)) for row in rows]
            res_str = "\n".join(str_rows) if str_rows else "A consulta não retornou dados."
            if len(res_str) > 2000:
                res_str = res_str[:2000] + "\n... (resultados truncados)"
            return {"sql_result": res_str}
    except Exception as e:
        return {"sql_result": f"Erro na execução da consulta: {str(e)}"}

def generate_answer(state: State):
    last_message = state["messages"][-1].content
    sql_result = state.get("sql_result", "")
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Você é um assistente focado em transparência de dados do governo. Baseado nos resultados extraídos do banco de dados abaixo, responda à dúvida do usuário de forma clara e amigável.\n\nResultados do BD:\n{sql_result}"),
        ("human", "{question}")
    ])
    
    result = llm.invoke(prompt.format(sql_result=sql_result, question=last_message))
    
    return {"messages": [result]}

graph_builder = StateGraph(State)
graph_builder.add_node("check_topic", check_topic)
graph_builder.add_node("generate_sql", generate_sql)
graph_builder.add_node("execute_sql", execute_sql)
graph_builder.add_node("generate_answer", generate_answer)

graph_builder.add_edge(START, "check_topic")
graph_builder.add_conditional_edges("check_topic", router_topic)
graph_builder.add_edge("generate_sql", "execute_sql")
graph_builder.add_edge("execute_sql", "generate_answer")
graph_builder.add_edge("generate_answer", END)

app_graph = graph_builder.compile()
