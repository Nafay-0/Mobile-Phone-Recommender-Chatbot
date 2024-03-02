import json
import os
import uuid
from typing import List

from fastapi import HTTPException, UploadFile, File
from langchain_community.vectorstores.chroma import Chroma
from constants import AGENT_PROMPT, PRODUCT_TOOL_PROMPT
from utils import get_llm, get_latest_history, load_embeddings, load_document
from Database import crud, models
from datetime import datetime as dt
from langchain.agents import AgentExecutor, OpenAIFunctionsAgent, create_openai_functions_agent
from langchain.agents.openai_functions_agent.agent_token_buffer_memory import AgentTokenBufferMemory
from langchain.tools.retriever import create_retriever_tool
from langchain_core.documents import Document
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage
from langchain_core.prompts import MessagesPlaceholder, PromptTemplate


def load_existing_DB(DB_PATH, embeddings):
    db = Chroma(persist_directory=DB_PATH,
                embedding_function=embeddings)
    if db is None:
        raise Exception("Vector database not found")
    return db


async def chat_response(message: str, sessionId: str, db):
    embeddings = load_embeddings("openai")
    llm = get_llm("gpt-3.5-turbo", "openai", {"temperature": 0.2})
    DB_PATH = "./Chroma"
    embeddings = load_embeddings("openai")
    vecDB = load_existing_DB(DB_PATH, embeddings)
    retrieval_tool = create_retriever_tool(
        retriever=vecDB.as_retriever(),
        name="product_detail_tool",
        document_prompt=PromptTemplate.from_template(PRODUCT_TOOL_PROMPT),
        description="Searches and return details about a particular product",
    )

    history = get_latest_history(crud.get_user_history(db, sessionId))
    tools = [retrieval_tool]
    system_message = SystemMessage(
        content=(
            AGENT_PROMPT
        )
    )
    memory_key = "history"
    memory = AgentTokenBufferMemory(memory_key=memory_key, llm=llm, max_token_limit=2000)
    prompt = OpenAIFunctionsAgent.create_prompt(
        system_message=system_message,
        extra_prompt_messages=[MessagesPlaceholder(variable_name=memory_key)],
    )
    for hist in history:
        memory.save_context({"input": hist[0]}, {"output": hist[1], "intermediate_steps": []})

    agent = create_openai_functions_agent(llm=llm, tools=tools, prompt=prompt)
    # Create Agent Executor
    AGENT_EXECUTER = AgentExecutor(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=True,
        return_intermediate_steps=True,
        handle_parsing_errors=True,
    )
    try:
        result = AGENT_EXECUTER.invoke({"input": message})
        answer = result["output"]
        history.append(
            (message, answer)
        )
        crud.add_chat_history(db, sessionId, history)
        return {"answer": answer}
    except Exception as e:
        print(e)
        return {"message": "Sorry, Something went wrong"}

    return {'response': response.content}


def add_docs_to_existing_db(path, docs, embeddings):
    # Load vector database
    db = Chroma(persist_directory=path, embedding_function=embeddings)
    if db is None:
        raise Exception("Vector database not found")
    db.add_documents(docs)
    db.persist()
    return db


async def create_upload_files(files):
    if not files:
        raise HTTPException(status_code=400, detail="No files to upload")
    docs_to_add = []
    try:
        for file in files:
            print(file.filename)

            if file.content_type in ["application/pdf", "application/csv", "text/plain"]:
                # upload to a folder 'temp_uploads'
                with open(f"temp_uploads/{file.filename}", "wb") as buffer:
                    buffer.write(await file.read())

                file_docs = load_document(file.filename, path="temp_uploads/")
                file_id = str(uuid.uuid1())
                for doc in file_docs:
                    doc.metadata["file_id"] = file_id
                    doc.metadata["date_added"] = str(dt.now())
                    doc.metadata["document_name"] = file.filename
                    docs_to_add.append(doc)
                os.remove(f"temp_uploads/{file.filename}")
            else:
                raise HTTPException(status_code=400, detail="File type not supported")
        print("Adding to DB", len(docs_to_add))
        # Add to vector db
        DB_PATH = "./Chroma"
        if not os.path.exists(DB_PATH):
            os.makedirs(DB_PATH)
        embeddings = load_embeddings("openai")

        db = add_docs_to_existing_db(DB_PATH, docs_to_add, embeddings)

        return {"message": "Files Uploaded Successfully"}

    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail="Error Uploading Files")
