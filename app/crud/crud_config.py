from typing import Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.models import ConversationConfig
from app.schemas.config import ConfigCreate, ConfigUpdate


class CRUDConfig(CRUDBase[ConversationConfig, ConfigCreate, ConfigUpdate]):
    def get_by_conversation(self, db: Session, *, conversation_id: int) -> Optional[ConversationConfig]:
        return (
            db.query(ConversationConfig)
            .filter(ConversationConfig.conversation_id == conversation_id)
            .first()
        )

    def create_or_update(
        self, db: Session, *, conversation_id: int, obj_in: ConfigUpdate
    ) -> ConversationConfig:
        existing = self.get_by_conversation(db, conversation_id=conversation_id)
        if existing:
            return self.update(db, db_obj=existing, obj_in=obj_in)
        create_data = ConfigCreate(conversation_id=conversation_id, **obj_in.model_dump(exclude_unset=True))
        return self.create(db, obj_in=create_data)


config = CRUDConfig(ConversationConfig)
