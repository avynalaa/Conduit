from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_active_user
from app.crud import message as crud_message, conversation as crud_conversation
from app.schemas.message import MessageCreate, MessageUpdate, MessageResponse
from app.models.models import User

router = APIRouter()


@router.get(
    "/conversations/{conversation_id}/messages",
    response_model=List[MessageResponse],
    summary="List conversation messages",
    responses={404: {"description": "Conversation not found"}},
)
def list_messages(
    conversation_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """List all messages in a conversation."""
    conv = crud_conversation.get(db, id=conversation_id)
    if not conv or conv.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    return crud_message.get_by_conversation(db, conversation_id=conversation_id, skip=skip, limit=limit)


@router.get(
    "/branches/{branch_id}/messages",
    response_model=List[MessageResponse],
    summary="List branch messages",
)
def list_branch_messages(
    branch_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """List all messages in a branch."""
    return crud_message.get_by_branch(db, branch_id=branch_id, skip=skip, limit=limit)


@router.post(
    "/messages",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a message",
    responses={404: {"description": "Conversation not found"}},
)
def create_message(
    message_in: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Create a new message."""
    conv = crud_conversation.get(db, id=message_in.conversation_id)
    if not conv or conv.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    return crud_message.create(db, obj_in=message_in)


@router.get(
    "/messages/{message_id}",
    response_model=MessageResponse,
    summary="Get a message",
    responses={404: {"description": "Message not found"}},
)
def get_message(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Get a specific message."""
    msg = crud_message.get(db, id=message_id)
    if not msg:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")

    conv = crud_conversation.get(db, id=msg.conversation_id)
    if not conv or conv.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")

    return msg


@router.get(
    "/messages/{message_id}/thread",
    response_model=List[MessageResponse],
    summary="Get message thread",
    responses={404: {"description": "Message not found"}},
)
def get_message_thread(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Get the full thread leading to this message."""
    msg = crud_message.get(db, id=message_id)
    if not msg:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")

    conv = crud_conversation.get(db, id=msg.conversation_id)
    if not conv or conv.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")

    return crud_message.get_thread(db, message_id=message_id)


@router.patch(
    "/messages/{message_id}",
    response_model=MessageResponse,
    summary="Update a message",
    responses={404: {"description": "Message not found"}},
)
def update_message(
    message_id: int,
    message_in: MessageUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Update a message."""
    msg = crud_message.get(db, id=message_id)
    if not msg:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")

    conv = crud_conversation.get(db, id=msg.conversation_id)
    if not conv or conv.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")

    return crud_message.update(db, db_obj=msg, obj_in=message_in)


@router.delete(
    "/messages/{message_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a message",
    responses={404: {"description": "Message not found"}},
)
def delete_message(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> None:
    """Delete a message."""
    msg = crud_message.get(db, id=message_id)
    if not msg:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")

    conv = crud_conversation.get(db, id=msg.conversation_id)
    if not conv or conv.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")

    crud_message.remove(db, id=message_id)
