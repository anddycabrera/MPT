from typing import Any
from app import schemas
from app.predictions.client import model_client
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse, StreamingResponse, PlainTextResponse
from fastapi.encoders import jsonable_encoder
from app.core.config import settings


router = APIRouter(prefix="/llm", tags=["llm"])

@router.post("/mpt-7b-chat", response_model=Any)
async def llmchat(
    *,    
    chat_request: schemas.ChatAIRequest   
) -> Any:
    """
    Generate a response based on the question
    """   
    try:  

        class FLAGS:
            verbose = False
            url = "tritonserver:8001"
            stream_timeout = None
            offset = 0
            iterations = 1
            streaming_mode = True

        sampling_parameters = {
            "max_new_tokens": "2048",
            "do_sample": "True",
            "num_return_sequences": "1",
            "eos_token_id": "tokenizer.eos_token_id",
            "pad_token_id": "tokenizer.eos_token_id",
            "temperature": "0.1",
            "top_p": "0.15",
            "repetition_penalty": "1.2"
        }
        
        generator = model_client(FLAGS, chat_request.question, sampling_parameters=sampling_parameters)
        return StreamingResponse(generator, media_type="text/event-stream")
    
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) from e
