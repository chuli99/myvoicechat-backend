from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.schemas.user import UserCreate, UserUpdate
from app.models.user import User
from app.crud import user as user_crud
from app.core.security import verify_password

class UserService:
    @staticmethod
    def register_user(db: Session, user_in: UserCreate) -> User:
        if user_crud.get_user_by_email(db, email=user_in.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The user with this email already exists in the system",
            )
        if user_crud.get_user_by_username(db, username=user_in.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The user with this username already exists in the system",
            )
        return user_crud.create_user(db, user=user_in)

    @staticmethod
    def authenticate(db: Session, username: str, password: str) -> Optional[User]:
        user = user_crud.get_user_by_username(db, username=username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        if hasattr(user, 'is_active') and not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )
        return user

    @staticmethod
    def update_user_profile(db: Session, user_id: int, user_data: UserUpdate) -> User:
        user = user_crud.get_user(db, user_id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        # Aquí puedes agregar validaciones adicionales si es necesario
        return user_crud.update_user(db, db_user=user, user_in=user_data)
