from typing import List
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.models import File, FileStatus, MessageFile
from app.schemas.file import FileCreate, FileUpdate


class CRUDFile(CRUDBase[File, FileCreate, FileUpdate]):
    def get_by_user(
        self, db: Session, *, user_id: int, skip: int = 0, limit: int = 50
    ) -> List[File]:
        return (
            db.query(File)
            .filter(File.user_id == user_id)
            .order_by(File.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_pending(self, db: Session, *, limit: int = 10) -> List[File]:
        return (
            db.query(File)
            .filter(File.status == FileStatus.PENDING)
            .limit(limit)
            .all()
        )

    def attach_to_message(
        self, db: Session, *, message_id: int, file_id: int
    ) -> MessageFile:
        db_obj = MessageFile(message_id=message_id, file_id=file_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


file = CRUDFile(File)
