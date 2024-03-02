import json
import os
import uuid
from .utils import get_llm, get_latest_history
from .Database import crud, models
from datetime import datetime as dt
from langchain.agents import AgentExecutor, OpenAIFunctionsAgent, create_openai_functions_agent
from langchain.agents.openai_functions_agent.agent_token_buffer_memory import AgentTokenBufferMemory
from langchain.tools.retriever import create_retriever_tool
from langchain_core.documents import Document
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage
from langchain_core.prompts import MessagesPlaceholder


async def chat_response(message: str, sessionId: str, db):
    history = get_latest_history(crud.get_user_history(db, sessionId))
    print(history)
    llm = get_llm("gpt-3.5-turbo", "openai", {"temperature": 0.2})
    response = await llm.ainvoke(message)
    answer = response.content
    history.append(
        (message, answer)
    )
    crud.add_chat_history(db, sessionId, history)

    return {'response': response.content}
