import asyncio
import logging
import uuid
import time
import json
from typing import AsyncGenerator, Optional, Dict, Any
from fastapi import FastAPI, Header, Depends
from fastapi.responses import JSONResponse, StreamingResponse
from models import ChatCompletionRequest, ChatCompletionResponse, Choice, MessageResponse, DEFAULT_MODEL
from security import get_current_user
from langflow_agent import run_travel_agent

logger = logging.getLogger()
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

app = FastAPI()

@app.post("/chat/completions")
async def chat_completions(
    request: ChatCompletionRequest,
    X_IBM_THREAD_ID: Optional[str] = Header(None, alias="X-IBM-THREAD-ID", description="Optional header to specify the thread ID"),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    logger.info(f"Received POST /chat/completions ChatCompletionRequest: {request.json()}")
    thread_id = ''
    if  X_IBM_THREAD_ID:
        thread_id =  X_IBM_THREAD_ID
    if request.extra_body and request.extra_body.thread_id:
        thread_id = request.extra_body.thread_id
    logger.info("thread_id: " + thread_id)

    # ignore model selection as it will likely require custom langflow component
    model = DEFAULT_MODEL

    if request.stream:
        return StreamingResponse(_call_agent_stream(request, thread_id, 50), media_type="text/event-stream")
    else:
        # request.messages is an array of dictionary, we need to get the last entry in the user message
        agent_response = await _call_agent(request)
        id = str(uuid.uuid4())
        response = ChatCompletionResponse(
            id=id,
            object="chat.completion",
            created=int(time.time()),
            model=request.model,
            choices=[
                Choice(
                    index=0,
                    message=MessageResponse(
                        role="assistant",
                        content=agent_response
                    ),
                    finish_reason="stop"
                )
            ]
        )
        return JSONResponse(content=response.dict())

async def _call_agent(request: ChatCompletionRequest) -> str:
    # request.messages is an array of dictionary, we need to get the last entry in the user message
    last_message = request.messages[-1]
    if last_message and last_message.role== 'user':
        last_user_input = last_message.content
        agent_response = await run_travel_agent(last_user_input)
    else:
        agent_response = 'No user message received'
    return agent_response

def format_resp(struct):
    return "data: " + json.dumps(struct) + "\n\n"

async def _call_agent_stream(request: ChatCompletionRequest, thread_id: str, chuck_size : int = 10) -> AsyncGenerator:    # get the agent response
    # get the agent response 
    agent_response = await _call_agent(request)
    # turn the string into AsyncGenerator
    for i in range(0, len(agent_response), chuck_size):
        response = {
            "id": str(uuid.uuid4()),
            "object": "thread.message.delta",
            "created": int(time.time()),
            "thread_id": thread_id,
            "model": "default",
            "choices": [
                {
                    "delta": {
                        "content": agent_response[i:i + chuck_size],
                        "role": "assistant"
                    }
                }
            ]
        }

        yield format_resp(response)
        await asyncio.sleep(0.01)  # simulate async behavior

    # no more response
    yield "data: [DONE]\n\n"


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8080)
