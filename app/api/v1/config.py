from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_active_user
from app.crud import conversation as crud_conversation
from app.crud import config as crud_config
from app.schemas.config import ConfigUpdate, ConfigResponse
from app.models.models import User

router = APIRouter()


@router.get(
    "/{conversation_id}/config",
    response_model=ConfigResponse,
    summary="Get configuration for a conversation",
    responses={
        404: {"description": "Conversation or config not found"},
        401: {"description": "Not authenticated"},
    },
)
def get_config(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    conv = crud_conversation.get(db, id=conversation_id)
    if not conv or conv.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    config = crud_config.get_by_conversation(db, conversation_id=conversation_id)
    if not config:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No config set for this conversation")
    return config


@router.put(
    "/{conversation_id}/config",
    response_model=ConfigResponse,
    summary="Create or update configuration for a conversation",
    responses={
        404: {"description": "Conversation not found"},
        401: {"description": "Not authenticated"},
    },
)
def set_config(
    conversation_id: int,
    config_in: ConfigUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    conv = crud_conversation.get(db, id=conversation_id)
    if not conv or conv.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    return crud_config.create_or_update(db, conversation_id=conversation_id, obj_in=config_in)
