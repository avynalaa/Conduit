from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_active_user
from app.crud import conversation as crud_conversation
from app.crud import message as crud_message
from app.crud import config as crud_config
from app.services.llm import chat_completion, chat_completion_stream, count_tokens
from app.services.context import build_context
from app.services.rag import query as rag_query
from app.schemas.message import MessageCreate, MessageResponse
from app.models.models import User

router = APIRouter()


class ChatRequest(BaseModel):
    conversation_id: int
    content: str
    model: Optional[str] = None
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    stream: bool = False
    system_prompt: Optional[str] = None
    use_rag: bool = False
    rag_results: int = 3


@router.post(
    "/",
    response_model=MessageResponse,
    summary="Send a chat message and get an AI response",
    responses={
        404: {"description": "Conversation not found"},
        401: {"description": "Not authenticated"},
    },
)
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    # Verify conversation access
    conv = crud_conversation.get(db, id=request.conversation_id)
    if not conv or conv.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

    # Load saved config as defaults
    saved_config = crud_config.get_by_conversation(db, conversation_id=request.conversation_id)
    if saved_config:
        if request.model is None:
            request.model = saved_config.model
        if request.temperature == 0.7 and saved_config.temperature is not None:
            request.temperature = saved_config.temperature
        if request.max_tokens is None:
            request.max_tokens = saved_config.max_tokens
        if request.system_prompt is None:
            request.system_prompt = saved_config.system_prompt
        if not request.use_rag and saved_config.use_rag:
            request.use_rag = saved_config.use_rag
            request.rag_results = saved_config.rag_results or 3

    # Save user message
    user_msg = crud_message.create(db, obj_in=MessageCreate(
        conversation_id=request.conversation_id,
        role="user",
        content=request.content,
    ))

    # Build message history from DB
    db_messages = crud_message.get_by_conversation(db, conversation_id=request.conversation_id)
    raw_messages = [{"role": msg.role, "content": msg.content} for msg in db_messages]

    # RAG context injection
    rag_context = ""
    if request.use_rag:
        rag_results = rag_query(
            query_text=request.content,
            user_id=current_user.id,
            n_results=request.rag_results,
        )
        if rag_results:
            rag_context = "\n\n---\nRelevant context from your documents:\n"
            for i, result in enumerate(rag_results, 1):
                rag_context += f"\n[{i}] {result['content']}\n"
            rag_context += "---\n"

    # Build system prompt with RAG context
    system_prompt = request.system_prompt or ""
    if rag_context:
        system_prompt = f"{system_prompt}\n\n{rag_context}".strip()

    # Build truncated context that fits the model's window
    messages = build_context(
        messages=raw_messages,
        system_prompt=system_prompt if system_prompt else None,
        model=request.model,
    )

    # Count input tokens
    input_tokens = count_tokens(messages, model=request.model)

    if request.stream:
        return _stream_response(db, request, messages, input_tokens)

    # Non-streaming response
    response = chat_completion(
        messages=messages,
        model=request.model,
        temperature=request.temperature,
        max_tokens=request.max_tokens,
    )

    assistant_content = response.choices[0].message.content
    completion_tokens = response.usage.completion_tokens
    prompt_tokens = response.usage.prompt_tokens

    # Save assistant message
    assistant_msg = crud_message.create(db, obj_in=MessageCreate(
        conversation_id=request.conversation_id,
        role="assistant",
        content=assistant_content,
    ))

    # Update token usage
    crud_message.update_token_usage(
        db,
        db_obj=user_msg,
        prompt_tokens=prompt_tokens,
        completion_tokens=0,
    )
    crud_message.update_token_usage(
        db,
        db_obj=assistant_msg,
        prompt_tokens=0,
        completion_tokens=completion_tokens,
    )

    return assistant_msg


def _stream_response(db, request, messages, input_tokens):
    def generate():
        full_content = ""
        for chunk in chat_completion_stream(
            messages=messages,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        ):
            full_content += chunk
            yield f"data: {chunk}\n\n"

        # Save assistant message after stream completes
        assistant_msg = crud_message.create(db, obj_in=MessageCreate(
            conversation_id=request.conversation_id,
            role="assistant",
            content=full_content,
        ))

        output_tokens = count_tokens(
            [{"role": "assistant", "content": full_content}],
            model=request.model,
        )
        crud_message.update_token_usage(
            db,
            db_obj=assistant_msg,
            prompt_tokens=input_tokens,
            completion_tokens=output_tokens,
        )

        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
