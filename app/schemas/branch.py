from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class BranchBase(BaseModel):
    name: Optional[str] = None
    is_active: bool = True


class BranchCreate(BranchBase):
    conversation_id: int


class BranchUpdate(BaseModel):
    name: Optional[str] = None
    is_active: Optional[bool] = None


class BranchResponse(BranchBase):
    id: int
    conversation_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
