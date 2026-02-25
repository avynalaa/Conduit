from typing import List, Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.models import Message
from app.schemas.message import MessageCreate, MessageUpdate


class CRUDMessage(CRUDBase[Message, MessageCreate, MessageUpdate]):
    def get_by_conversation(
        self, db: Session, *, conversation_id: int, skip: int = 0, limit: int = 100
    ) -> List[Message]:
        return (
            db.query(Message)
            .filter(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_branch(
        self, db: Session, *, branch_id: int, skip: int = 0, limit: int = 100
    ) -> List[Message]:
        return (
            db.query(Message)
            .filter(Message.branch_id == branch_id)
            .order_by(Message.created_at.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_thread(self, db: Session, *, message_id: int) -> List[Message]:
        """Walk up the parent chain to build the conversation thread."""
        thread = []
        current = self.get(db, id=message_id)
        while current:
            thread.append(current)
            current = (
                self.get(db, id=current.parent_message_id)
                if current.parent_message_id
                else None
            )
        thread.reverse()
        return thread

    def update_token_usage(
        self, db: Session, *, db_obj: Message, prompt_tokens: int, completion_tokens: int
    ) -> Message:
        db_obj.prompt_tokens = prompt_tokens
        db_obj.completion_tokens = completion_tokens
        db_obj.total_tokens = prompt_tokens + completion_tokens
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


message = CRUDMessage(Message)
