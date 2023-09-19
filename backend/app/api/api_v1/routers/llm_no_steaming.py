#working version for friday

from typing import Any
from app import schemas
from fastapi import APIRouter, Depends, HTTPException, Security, status
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.encoders import jsonable_encoder
from app.core.config import settings
import pickle
import os

from langchain.schema import Document
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain.chains.query_constructor.base import AttributeInfo
from langchain.schema import SystemMessage
from langchain.agents import OpenAIFunctionsAgent, Tool, AgentExecutor, create_pandas_dataframe_agent
from langchain.memory.chat_message_histories import RedisChatMessageHistory
from langchain.memory import ConversationBufferMemory
from langchain.prompts import MessagesPlaceholder
import pandas as pd


file_path = str(
     os.path.abspath(
     os.path.join(
     __file__,
     '../../../../final_docs.pkl')))

with open(file_path,'rb') as file:
            docs = pickle.load(file)

embeddings = OpenAIEmbeddings()       
vectorstore = Chroma.from_documents(docs, embeddings)
learners_df = pd.DataFrame()
router = APIRouter(prefix="/openai", tags=["openai"])
@router.post("/chat-ai", response_model=Any)
async def llmchat(
    *,    
    chat_request: schemas.ChatAIRequest   
) -> Any:
    """
    Generate a response based on the question
    """   
    try:  
        memory, _ = get_memory_and_history(chat_request.session_id)

        system_message = SystemMessage(content="You are very good getting using tools about opinions, but bad answering about opinions yourself. That's why you prefer to use a tool to answer about opinions. Your name is Vector Bot")
        prompt = OpenAIFunctionsAgent.create_prompt(system_message=system_message)    
        agent = OpenAIFunctionsAgent(llm=ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo-16k-0613"), tools=toolsRetrival(), prompt=prompt)       
        agent_executor = AgentExecutor(agent=agent, tools=toolsRetrival(), verbose=True)
        return PlainTextResponse(agent_executor.run(chat_request.question))
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) from e

def sentimentQA(text: str):
    
    #retriever = vectorstore.as_retriever(search_kwargs={'k': 1})
    
    #qa = RetrievalQA.from_chain_type(llm=OpenAI(temperature=0), chain_type="refine", retriever=retriever)
    metadata_field_info = [
        AttributeInfo(
            name="label",
            description="Sentiment of the document content as positive, negative and neutral",
            type="string",
        ),
        AttributeInfo(
            name="count",
            description="Use when asked for count positives, negatives and neutrals opinions",
            type="integer",
        ),
        AttributeInfo(
            name="survey",
            description="Title of the survey for the opinion",
            type="string",
        ),
        AttributeInfo(
            name="context",
            description="context of the survey for the opinion",
            type="string",
        ),
        AttributeInfo(
            name="question",
            description="question of the survey relate to opinions.",
            type="string",
        )
    ]

    document_content_description = "Opinion mining responses from learners surveys"

    retriever = SelfQueryRetriever.from_llm(
        OpenAI(temperature=0), vectorstore, document_content_description, metadata_field_info, enable_limit=True, verbose=True
    )

    response = retriever.get_relevant_documents(text)
    
    return response

def toolsRetrival():
      tools = [
            Tool(
                name="Survey",
                func=sentimentQA,
                description="Use this tool to answer question about opinion mining. Pass the text requesting, positive, negative or neutral documents."
            )
      ]
      return tools


@router.get("/chat-ai-history", response_model=Any)
async def get_chat_ai_history(
    *,   
    session_id: str
) -> Any:
    """
    Retrieve the chat history based on the session_id
    """
    try:
        return chat_ai_history(session_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) from e
    
@router.get("/chat-ai-reset", response_model=Any)
async def get_chat_ai_reset(
    *,   
    session_id: str  
) -> Any:
    """
    Reset the chat history based on the session_id
    """
    try:
        chat_ai_reset(session_id)
        return {"status": "Chat history reset successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) from e
    
# @router.post("/completion", response_model=Any)
# def generate_completion(
#     *
#     completion_in: schemas.Completion
# ) -> Any:
#     """
#     Generate a text completion using OpenAI's models
#     """   
#     try:
#         response = openai.Completion.create(
#             model=completion_in.model,
#             prompt=completion_in.prompt,
#             temperature=completion_in.temperature,
#             max_tokens=completion_in.max_tokens,
#             top_p=completion_in.top_p,
#             frequency_penalty=completion_in.frequency_penalty,
#             presence_penalty=completion_in.presence_penalty,
#             stop=completion_in.stop
#         )
#         return response
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=str(e)
#         ) from e

def chat_ai_history(session_id: str):       
    _, message_history = get_memory_and_history(session_id)
    result = message_history.messages
    return result
def chat_ai_reset(session_id: str):       
    _, message_history = get_memory_and_history(session_id)
    message_history.clear()
def get_memory_and_history(session_id: str):
    message_history = RedisChatMessageHistory(
        url=settings.BROKER_URL, ttl=600, session_id=session_id
    )
    memory = ConversationBufferMemory(
        memory_key="memory", return_messages=True, chat_memory=message_history
    )
    return memory, message_history