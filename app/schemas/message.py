from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class MessageBase(BaseModel):
    role: str
    content: str
    extra_metadata: Optional[dict] = {}


class MessageCreate(MessageBase):
    conversation_id: int
    branch_id: Optional[int] = None
    parent_message_id: Optional[int] = None


class MessageUpdate(BaseModel):
    content: Optional[str] = None
    extra_metadata: Optional[dict] = None


class MessageResponse(MessageBase):
    id: int
    conversation_id: int
    branch_id: Optional[int] = None
    parent_message_id: Optional[int] = None
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MessageWithFiles(MessageResponse):
    """Message with attached files"""
    files: List["FileResponse"] = []

    model_config = ConfigDict(from_attributes=True)
