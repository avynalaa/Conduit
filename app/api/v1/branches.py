from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_active_user
from app.crud import conversation as crud_conversation
from app.crud import message as crud_message
from app.schemas.branch import BranchCreate, BranchUpdate, BranchResponse
from app.schemas.message import MessageCreate, MessageResponse
from app.models.models import User, Branch

router = APIRouter()


def _verify_conversation_access(db: Session, conversation_id: int, user_id: int):
    conv = crud_conversation.get(db, id=conversation_id)
    if not conv or conv.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    return conv


@router.get(
    "/{conversation_id}/branches",
    response_model=List[BranchResponse],
    summary="List all branches for a conversation",
    responses={
        404: {"description": "Conversation not found"},
        401: {"description": "Not authenticated"},
    },
)
def list_branches(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    _verify_conversation_access(db, conversation_id, current_user.id)
    return db.query(Branch).filter(Branch.conversation_id == conversation_id).all()


@router.post(
    "/{conversation_id}/branches",
    response_model=BranchResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new branch in a conversation",
    responses={
        400: {"description": "Conversation ID mismatch"},
        404: {"description": "Conversation not found"},
        401: {"description": "Not authenticated"},
    },
)
def create_branch(
    conversation_id: int,
    branch_in: BranchCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    _verify_conversation_access(db, conversation_id, current_user.id)
    if branch_in.conversation_id != conversation_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Conversation ID mismatch")
    branch = Branch(**branch_in.model_dump())
    db.add(branch)
    db.commit()
    db.refresh(branch)
    return branch


@router.patch(
    "/branches/{branch_id}",
    response_model=BranchResponse,
    summary="Update a branch by ID",
    responses={
        404: {"description": "Branch or conversation not found"},
        401: {"description": "Not authenticated"},
    },
)
def update_branch(
    branch_id: int,
    branch_in: BranchUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    branch = db.query(Branch).filter(Branch.id == branch_id).first()
    if not branch:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Branch not found")
    _verify_conversation_access(db, branch.conversation_id, current_user.id)
    update_data = branch_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(branch, field, value)
    db.commit()
    db.refresh(branch)
    return branch


@router.post(
    "/branches/{branch_id}/switch",
    response_model=BranchResponse,
    summary="Set a branch as active and deactivate all others",
    responses={
        404: {"description": "Branch or conversation not found"},
        401: {"description": "Not authenticated"},
    },
)
def switch_active_branch(
    branch_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Set this branch as active and deactivate all others in the conversation."""
    branch = db.query(Branch).filter(Branch.id == branch_id).first()
    if not branch:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Branch not found")
    _verify_conversation_access(db, branch.conversation_id, current_user.id)
    # Deactivate all branches in this conversation
    db.query(Branch).filter(
        Branch.conversation_id == branch.conversation_id
    ).update({"is_active": False})
    # Activate the selected one
    branch.is_active = True
    db.commit()
    db.refresh(branch)
    return branch


@router.post(
    "/{conversation_id}/regenerate",
    response_model=MessageResponse,
    summary="Regenerate a response from a specific message by creating a new branch",
    responses={
        400: {"description": "Invalid parent message"},
        404: {"description": "Conversation not found"},
        401: {"description": "Not authenticated"},
    },
)
def regenerate_from_message(
    conversation_id: int,
    parent_message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Create a new branch from a specific message (swipe/regenerate)."""
    conv = _verify_conversation_access(db, conversation_id, current_user.id)
    parent = crud_message.get(db, id=parent_message_id)
    if not parent or parent.conversation_id != conversation_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid parent message")
    # Create a new branch
    branch = Branch(conversation_id=conversation_id, name=f"Branch from message {parent_message_id}")
    db.add(branch)
    db.commit()
    db.refresh(branch)
    # Get the thread up to the parent message
    thread = crud_message.get_thread(db, message_id=parent_message_id)
    messages = [{"role": msg.role, "content": msg.content} for msg in thread]
    # Call LLM for a new response
    from app.services.llm import chat_completion
    from app.crud import config as crud_config
    from app.core.config import settings
    saved_config = crud_config.get_by_conversation(db, conversation_id=conversation_id)
    model = saved_config.model if saved_config and saved_config.model else settings.DEFAULT_MODEL
    system_prompt = saved_config.system_prompt if saved_config and saved_config.system_prompt else None
    if system_prompt:
        messages.insert(0, {"role": "system", "content": system_prompt})
    response = chat_completion(messages=messages, model=model)
    assistant_content = response.choices[0].message.content
    # Save as new message on the branch
    assistant_msg = crud_message.create(db, obj_in=MessageCreate(
        conversation_id=conversation_id,
        branch_id=branch.id,
        parent_message_id=parent_message_id,
        role="assistant",
        content=assistant_content,
    ))
    crud_message.update_token_usage(
        db, db_obj=assistant_msg,
        prompt_tokens=response.usage.prompt_tokens,
        completion_tokens=response.usage.completion_tokens,
    )
    return assistant_msg


@router.delete(
    "/branches/{branch_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a branch by ID",
    responses={
        404: {"description": "Branch or conversation not found"},
        401: {"description": "Not authenticated"},
    },
)
def delete_branch(
    branch_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> None:
    branch = db.query(Branch).filter(Branch.id == branch_id).first()
    if not branch:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Branch not found")
    _verify_conversation_access(db, branch.conversation_id, current_user.id)
    db.delete(branch)
    db.commit()
