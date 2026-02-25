from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ConfigBase(BaseModel):
    model: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    system_prompt: Optional[str] = None
    use_rag: Optional[bool] = None
    rag_results: Optional[int] = None


class ConfigCreate(ConfigBase):
    conversation_id: int


class ConfigUpdate(ConfigBase):
    pass


class ConfigResponse(ConfigBase):
    id: int
    conversation_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)
