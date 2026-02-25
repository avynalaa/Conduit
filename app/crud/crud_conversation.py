from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from app.crud.base import CRUDBase
from app.models.models import Conversation
from app.schemas.conversation import ConversationCreate, ConversationUpdate


class CRUDConversation(CRUDBase[Conversation, ConversationCreate, ConversationUpdate]):
    def get_by_user(
        self, db: Session, *, user_id: int, skip: int = 0, limit: int = 50
    ) -> List[Conversation]:
        return (
            db.query(Conversation)
            .filter(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc().nullslast(), Conversation.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_with_messages(self, db: Session, *, id: int) -> Optional[Conversation]:
        return (
            db.query(Conversation)
            .options(joinedload(Conversation.messages))
            .filter(Conversation.id == id)
            .first()
        )

    def get_with_branches(self, db: Session, *, id: int) -> Optional[Conversation]:
        return (
            db.query(Conversation)
            .options(joinedload(Conversation.branches))
            .filter(Conversation.id == id)
            .first()
        )

    def create_for_user(
        self, db: Session, *, obj_in: ConversationCreate, user_id: int
    ) -> Conversation:
        obj_data = obj_in.model_dump()
        db_obj = Conversation(**obj_data, user_id=user_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


conversation = CRUDConversation(Conversation)
