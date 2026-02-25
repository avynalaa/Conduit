from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_active_user
from app.crud import conversation as crud_conversation
from app.schemas.conversation import (
    ConversationCreate,
    ConversationUpdate,
    ConversationResponse,
    ConversationWithMessages,
    ConversationWithBranches,
)
from app.models.models import User

router = APIRouter()


@router.get(
    "/",
    response_model=List[ConversationResponse],
    summary="List user conversations",
)
def list_conversations(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    return crud_conversation.get_by_user(db, user_id=current_user.id, skip=skip, limit=limit)


@router.post(
    "/",
    response_model=ConversationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new conversation",
)
def create_conversation(
    conversation_in: ConversationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    return crud_conversation.create_for_user(db, obj_in=conversation_in, user_id=current_user.id)


@router.get(
    "/{conversation_id}",
    response_model=ConversationWithMessages,
    summary="Get conversation with messages",
    responses={404: {"description": "Conversation not found"}},
)
def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    conv = crud_conversation.get_with_messages(db, id=conversation_id)
    if not conv or conv.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    return conv


@router.get(
    "/{conversation_id}/branches",
    response_model=ConversationWithBranches,
    summary="Get conversation with branches",
    responses={404: {"description": "Conversation not found"}},
)
def get_conversation_branches(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    conv = crud_conversation.get_with_branches(db, id=conversation_id)
    if not conv or conv.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    return conv


@router.patch(
    "/{conversation_id}",
    response_model=ConversationResponse,
    summary="Update conversation",
    responses={404: {"description": "Conversation not found"}},
)
def update_conversation(
    conversation_id: int,
    conversation_in: ConversationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    conv = crud_conversation.get(db, id=conversation_id)
    if not conv or conv.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    return crud_conversation.update(db, db_obj=conv, obj_in=conversation_in)


@router.delete(
    "/{conversation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete conversation",
    responses={404: {"description": "Conversation not found"}},
)
def delete_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> None:
    conv = crud_conversation.get(db, id=conversation_id)
    if not conv or conv.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    crud_conversation.remove(db, id=conversation_id)
