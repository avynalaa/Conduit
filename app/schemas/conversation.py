from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ConversationBase(BaseModel):
    title: Optional[str] = None
    extra_metadata: Optional[dict] = {}


class ConversationCreate(ConversationBase):
    pass


class ConversationUpdate(BaseModel):
    title: Optional[str] = None
    extra_metadata: Optional[dict] = None


class ConversationResponse(ConversationBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ConversationWithMessages(ConversationResponse):
    """Conversation with its messages included"""
    messages: List["MessageResponse"] = []

    model_config = ConfigDict(from_attributes=True)


class ConversationWithBranches(ConversationResponse):
    """Conversation with branch metadata"""
    branches: List["BranchResponse"] = []

    model_config = ConfigDict(from_attributes=True)
