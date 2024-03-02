import re
import json
import tiktoken
import os
from typing import Optional, Type, List

from langchain.tools.retriever import create_retriever_tool
from langchain_community.vectorstores.chroma import Chroma
from pydantic import BaseModel, Field
from langchain.prompts import PromptTemplate
from langchain.tools import BaseTool
from langchain_community.vectorstores import FAISS
from langchain.schema import SystemMessage
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from datetime import datetime, timedelta
from ..utils import load_embeddings, get_llm
from ..constants import PRODUCT_TOOL_PROMPT


def load_existing_DB(DB_PATH, embeddings):
    db = Chroma(persist_directory=DB_PATH,
                embedding_function=embeddings)
    if db is None:
        raise Exception("Vector database not found")
    return db


def lookup_product(lookup_string: str, history: List[str]) -> str:
    """
    This function looks up a product in the database
    :param lookup_string: The string about product to look up in the database
    :return: The product details
    """
    embeddings = load_embeddings("openai")
    llm = get_llm("gpt-3.5-turbo", "openai", {"temperature": 0.2})
    DB_PATH = "../Chroma"
    embeddings = load_embeddings("openai")
    vecDB = load_existing_DB(DB_PATH, embeddings)
    retrieval_tool = create_retriever_tool(
        retriever=vecDB.as_retriever(),
        name="product_detail_tool",
        description="Searches and returns documents regarding the query",
    )


class LookUpProduct(BaseModel):
    """Input for looking up a product"""
    lookup_string: str = Field(..., title="The string to look up",
                               description="The string about product to look up in the database")
    history: List[str] = Field(..., title="The conversation history",
                               description="The conversation history")

class LookUpProductTool(BaseTool):
    """Tool for looking up a product"""
    async def run(self, input: str, history: List[str]) -> str:
        return lookup_product(input,history)

