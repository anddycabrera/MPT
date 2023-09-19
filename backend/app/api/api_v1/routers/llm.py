from typing import Any
from app import schemas
from fastapi import APIRouter, Depends, HTTPException, Security, status
from fastapi.responses import JSONResponse, StreamingResponse, PlainTextResponse
from fastapi.encoders import jsonable_encoder
from app.core.config import settings
from typing import AsyncIterable
import asyncio

from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chat_models import ChatOpenAI
from langchain.llms import OpenAI
from langchain.chains import RetrievalQA, SequentialChain
from langchain.memory.chat_message_histories import RedisChatMessageHistory
from langchain.memory import ConversationBufferMemory
#from langchain.prompts import PromptTemplate
from langchain.callbacks import AsyncIteratorCallbackHandler
from langchain.vectorstores.redis import Redis
from langchain import PromptTemplate
from langchain.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.chains import LLMChain

from langchain.document_loaders import WebBaseLoader
from langchain.indexes import VectorstoreIndexCreator
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.agents.agent_toolkits import create_retriever_tool
from langchain.agents.agent_toolkits import create_conversational_retrieval_agent
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
import time

router = APIRouter(prefix="/openai", tags=["openai"])

async def send_message(chat_request, retriever) -> AsyncIterable[str]:
    callback = AsyncIteratorCallbackHandler()
    model = ChatOpenAI(
        model_name="gpt-3.5-turbo-16k", 
        temperature=0,
        streaming=True,
        verbose=True,
        
    )

    tool = create_retriever_tool(
        retriever, 
        "search_langchain_documentation",
        "Searches and returns documents regarding the langchain documentation."
    )
    tools = [tool]

    agent_executor = create_conversational_retrieval_agent(model, tools, verbose=True)
    
    task = asyncio.create_task(
        agent_executor.acall({"input": chat_request.question}, callbacks=[callback])
    )

    try:
        async for token in callback.aiter():
            yield token
    except Exception as e:
        print(f"Caught exception: {e}")
    finally:
        callback.done.set()

    await task

@router.post("/chat-ai", response_model=Any)
async def llmchat(
    *,    
    chat_request: schemas.ChatAIRequest   
) -> Any:
    """
    Generate a response based on the question
    """   
    try:  
        loader = WebBaseLoader("https://api.python.langchain.com/en/latest/agents/langchain.agents.agent.AgentExecutor.html#langchain.agents.agent.AgentExecutor")
        data = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(chunk_size = 500, chunk_overlap = 0)
        all_splits = text_splitter.split_documents(data)

        vectorstore = Chroma.from_documents(documents=all_splits, embedding=OpenAIEmbeddings())

        retriever = vectorstore.as_retriever()

    
        generator = send_message(chat_request, retriever)
        
        return StreamingResponse(generator, media_type="text/event-stream")
    
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) from e

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
        memory_key="memory", return_messages=True, chat_memory=message_history, k=5
    )
    return memory, message_history

@router.post("/stream_chat/")
async def stream_chat(chat_request: schemas.ChatAIRequest):
    loader = WebBaseLoader("https://api.python.langchain.com/en/latest/agents/langchain.agents.agent.AgentExecutor.html#langchain.agents.agent.AgentExecutor")
    data = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size = 500, chunk_overlap = 0)
    all_splits = text_splitter.split_documents(data)

    vectorstore = Chroma.from_documents(documents=all_splits, embedding=OpenAIEmbeddings())

    retriever = vectorstore.as_retriever()

    generator = send_message(chat_request, retriever)
    
    return StreamingResponse(generator, media_type="text/event-stream")