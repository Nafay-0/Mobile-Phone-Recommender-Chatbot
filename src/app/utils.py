from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
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

