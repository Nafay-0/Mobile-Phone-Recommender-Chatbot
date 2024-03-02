from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader, CSVLoader, TextLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.llms import HuggingFaceHub
import json

"""
This code returns the appropriate LLM object based on input
:Parameters:
    model_name : (str) - The name of the LLM.
    type : (str) - The type of LLM. (openai, huggingface_hub,)
    kwargs : (dict) - The arguments for the LLM.
:return: (LLM) - The LLM object.

"""


def get_llm(model_name, type, kwargs):
    load_dotenv()
    if type == "openai":
        llm = ChatOpenAI(model_name=model_name, **kwargs)
    elif type == "huggingface_hub":
        # parse kwargs for model_kwargs
        model_kwargs = {}
        for key, value in kwargs.items():
            if "model_" in key:
                model_kwargs[key[6:]] = value
        llm = HuggingFaceHub(repo_id=model_name)
    else:
        raise ValueError("Invalid LLM type")
    return llm


def load_embeddings(type, kwargs=None):
    if type == "openai":
        return OpenAIEmbeddings(model="text-embedding-3-large")
    elif type == "hugging_face":
        model_name = "sentence-transformers/all-mpnet-base-v2"
        model_kwargs = {'device': 'cpu'}
        encode_kwargs = {'normalize_embeddings': True}
        return HuggingFaceEmbeddings(model_name=model_name,
                                     model_kwargs=model_kwargs,
                                     encode_kwargs=encode_kwargs)


def get_latest_history(chatbotHistory):
    history = []
    if chatbotHistory is not None:
        chatbotHistory = json.loads(chatbotHistory)
        # Take the last 5 conversations
        for h in chatbotHistory[-5:]:
            # print(h)
            human = h[0]
            ai = h[1]
            history.append((human, ai))

    return history

import sys
import csv

def load_document(fileName, path):
    csv.field_size_limit(sys.maxsize)
    load_dotenv()  # load environment variables from .env file
    # Check file type
    file = path + fileName
    if file.endswith(".pdf"):
        loader = PyPDFLoader(file)
    elif file.endswith(".csv"):
        loader = CSVLoader(file,
                           csv_args={
        "delimiter": "|"
        })


    elif file.endswith(".txt"):
        loader = TextLoader(file)
    else:
        raise Exception("File type not supported")
    # Load documents
    documents = loader.load_and_split()
    return documents