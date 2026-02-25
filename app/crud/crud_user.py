from typing import Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.models import User
from app.schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    def get_by_username(self, db: Session, *, username: str) -> Optional[User]:
        return db.query(User).filter(User.username == username).first()

    def get_by_oauth(self, db: Session, *, provider: str, oauth_id: str) -> Optional[User]:
        return db.query(User).filter(
            User.oauth_provider == provider,
            User.oauth_id == oauth_id
        ).first()


user = CRUDUser(User)
