"""
OpenAI-compatible API endpoints

This module provides OpenAI-compatible API endpoints for ClawdBot,
allowing it to be used as a drop-in replacement for OpenAI in many applications.
"""
import time
import uuid
import logging
from typing import Optional, List, Dict, Any, AsyncIterator
from datetime import datetime

from fastapi import APIRouter, HTTPException, Header
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from ..agents.runtime import AgentRuntime
from ..agents.session import SessionManager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1", tags=["OpenAI Compatible"])


# Request/Response models following OpenAI API format
class ChatMessage(BaseModel):
    """Chat message"""
    role: str
    content: str
    name: Optional[str] = None


class ChatCompletionRequest(BaseModel):
    """Chat completion request"""
    model: str
    messages: List[ChatMessage]
    temperature: Optional[float] = 1.0
    top_p: Optional[float] = 1.0
    n: Optional[int] = 1
    stream: Optional[bool] = False
    max_tokens: Optional[int] = None
    presence_penalty: Optional[float] = 0.0
    frequency_penalty: Optional[float] = 0.0
    user: Optional[str] = None


class ChatCompletionChoice(BaseModel):
    """Chat completion choice"""
    index: int
    message: ChatMessage
    finish_reason: Optional[str] = None


class ChatCompletionUsage(BaseModel):
    """Token usage"""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class ChatCompletionResponse(BaseModel):
    """Chat completion response"""
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[ChatCompletionChoice]
    usage: Optional[ChatCompletionUsage] = None


class ChatCompletionChunkDelta(BaseModel):
    """Streaming chunk delta"""
    role: Optional[str] = None
    content: Optional[str] = None


class ChatCompletionChunkChoice(BaseModel):
    """Streaming chunk choice"""
    index: int
    delta: ChatCompletionChunkDelta
    finish_reason: Optional[str] = None


class ChatCompletionChunk(BaseModel):
    """Streaming chunk"""
    id: str
    object: str = "chat.completion.chunk"
    created: int
    model: str
    choices: List[ChatCompletionChunkChoice]


class ModelInfo(BaseModel):
    """Model information"""
    id: str
    object: str = "model"
    created: int
    owned_by: str


class ModelsResponse(BaseModel):
    """Models list response"""
    object: str = "list"
    data: List[ModelInfo]


# Available models
AVAILABLE_MODELS = [
    ModelInfo(
        id="claude-opus-4",
        created=int(time.time()),
        owned_by="anthropic"
    ),
    ModelInfo(
        id="claude-sonnet-4",
        created=int(time.time()),
        owned_by="anthropic"
    ),
    ModelInfo(
        id="gpt-4o",
        created=int(time.time()),
        owned_by="openai"
    ),
    ModelInfo(
        id="gpt-4-turbo",
        created=int(time.time()),
        owned_by="openai"
    ),
]


# Global instances (set by main API server)
_runtime: Optional[AgentRuntime] = None
_session_manager: Optional[SessionManager] = None


def set_runtime(runtime: AgentRuntime) -> None:
    """Set runtime instance"""
    global _runtime
    _runtime = runtime


def set_session_manager(manager: SessionManager) -> None:
    """Set session manager"""
    global _session_manager
    _session_manager = manager


def _map_model_name(model: str) -> str:
    """Map OpenAI model name to internal model name"""
    model_mapping = {
        "gpt-4": "openai/gpt-4",
        "gpt-4-turbo": "openai/gpt-4-turbo",
        "gpt-4o": "openai/gpt-4o",
        "gpt-3.5-turbo": "openai/gpt-3.5-turbo",
        "claude-3-opus": "anthropic/claude-opus-4",
        "claude-3-sonnet": "anthropic/claude-sonnet-4",
        "claude-opus-4": "anthropic/claude-opus-4",
        "claude-sonnet-4": "anthropic/claude-sonnet-4",
    }
    
    return model_mapping.get(model, f"anthropic/{model}")


@router.get("/models", response_model=ModelsResponse)
async def list_models():
    """
    List available models
    
    Returns a list of models compatible with this API.
    """
    return ModelsResponse(data=AVAILABLE_MODELS)


@router.get("/models/{model_id}", response_model=ModelInfo)
async def get_model(model_id: str):
    """
    Get model information
    
    Returns information about a specific model.
    """
    for model in AVAILABLE_MODELS:
        if model.id == model_id:
            return model
    
    raise HTTPException(status_code=404, detail=f"Model {model_id} not found")


@router.post("/chat/completions")
async def chat_completions(
    request: ChatCompletionRequest,
    authorization: Optional[str] = Header(None)
):
    """
    Create chat completion
    
    Creates a completion for the chat messages.
    Compatible with OpenAI's chat completions API.
    """
    if not _runtime or not _session_manager:
        raise HTTPException(
            status_code=503,
            detail="Service not initialized"
        )
    
    # Generate IDs
    completion_id = f"chatcmpl-{uuid.uuid4().hex[:24]}"
    created = int(time.time())
    
    # Map model name
    model = _map_model_name(request.model)
    
    # Create session for this request
    session_id = request.user or f"openai-compat-{uuid.uuid4().hex[:8]}"
    session = _session_manager.get_session(session_id)
    
    # Clear session for fresh context (OpenAI-style stateless)
    session.clear()
    
    # Add messages to session
    for msg in request.messages:
        if msg.role == "system":
            session.add_system_message(msg.content)
        elif msg.role == "user":
            session.add_user_message(msg.content)
        elif msg.role == "assistant":
            session.add_assistant_message(msg.content)
    
    # Create runtime with specified model
    runtime = AgentRuntime(model=model)
    
    if request.stream:
        # Streaming response
        async def stream_response() -> AsyncIterator[str]:
            try:
                # Send initial chunk with role
                initial_chunk = ChatCompletionChunk(
                    id=completion_id,
                    created=created,
                    model=request.model,
                    choices=[ChatCompletionChunkChoice(
                        index=0,
                        delta=ChatCompletionChunkDelta(role="assistant")
                    )]
                )
                yield f"data: {initial_chunk.model_dump_json()}\n\n"
                
                # Stream content
                async for event in runtime.run_turn(
                    session,
                    "",  # Empty message since we already added messages
                    max_tokens=request.max_tokens or 4096
                ):
                    if event.type == "assistant":
                        delta = event.data.get("delta", {})
                        if "text" in delta:
                            chunk = ChatCompletionChunk(
                                id=completion_id,
                                created=created,
                                model=request.model,
                                choices=[ChatCompletionChunkChoice(
                                    index=0,
                                    delta=ChatCompletionChunkDelta(
                                        content=delta["text"]
                                    )
                                )]
                            )
                            yield f"data: {chunk.model_dump_json()}\n\n"
                
                # Send final chunk
                final_chunk = ChatCompletionChunk(
                    id=completion_id,
                    created=created,
                    model=request.model,
                    choices=[ChatCompletionChunkChoice(
                        index=0,
                        delta=ChatCompletionChunkDelta(),
                        finish_reason="stop"
                    )]
                )
                yield f"data: {final_chunk.model_dump_json()}\n\n"
                yield "data: [DONE]\n\n"
                
            except Exception as e:
                logger.error(f"Streaming error: {e}")
                error_chunk = {"error": str(e)}
                yield f"data: {error_chunk}\n\n"
        
        return StreamingResponse(
            stream_response(),
            media_type="text/event-stream"
        )
    
    else:
        # Non-streaming response
        try:
            response_text = ""
            
            async for event in runtime.run_turn(
                session,
                "",  # Empty message since we already added messages
                max_tokens=request.max_tokens or 4096
            ):
                if event.type == "assistant":
                    delta = event.data.get("delta", {})
                    if "text" in delta:
                        response_text += delta["text"]
            
            # Estimate tokens (rough approximation)
            prompt_tokens = sum(len(m.content) // 4 for m in request.messages)
            completion_tokens = len(response_text) // 4
            
            return ChatCompletionResponse(
                id=completion_id,
                created=created,
                model=request.model,
                choices=[ChatCompletionChoice(
                    index=0,
                    message=ChatMessage(
                        role="assistant",
                        content=response_text
                    ),
                    finish_reason="stop"
                )],
                usage=ChatCompletionUsage(
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    total_tokens=prompt_tokens + completion_tokens
                )
            )
        
        except Exception as e:
            logger.error(f"Chat completion error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
