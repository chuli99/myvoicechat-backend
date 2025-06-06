from typing import List, Optional, Dict, Any

from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.services.file_storage import FileStorageService


def get_user(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    return db.query(User).filter(User.username == username).first()


def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    return db.query(User).offset(skip).limit(limit).all()


def create_user(db: Session, user: UserCreate) -> User:
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        primary_language=user.primary_language
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(
    db: Session, db_user: User, user_in: UserUpdate
) -> User:
    user_data = user_in.dict(exclude_unset=True)
    if user_data.get("password"):
        hashed_password = get_password_hash(user_data["password"])
        del user_data["password"]
        user_data["hashed_password"] = hashed_password
    
    for field, value in user_data.items():
        setattr(db_user, field, value)
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user_audio(
    db: Session, 
    user_id: int, 
    audio_url: str
) -> Optional[User]:
    """Actualiza la referencia de audio del usuario"""
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        # Si ya tenía un audio, eliminar el anterior
        if user.ref_audio_url:
            file_service = FileStorageService()
            old_file_path = file_service.get_full_path_from_url(user.ref_audio_url)
            file_service.delete_audio_file(old_file_path)
        
        user.ref_audio_url = audio_url
        db.commit()
        db.refresh(user)
    return user


def delete_user(db: Session, user_id: int) -> Optional[User]:
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        # Eliminar archivo de audio si existe
        if user.ref_audio_url:
            file_service = FileStorageService()
            file_path = file_service.get_full_path_from_url(user.ref_audio_url)
            file_service.delete_audio_file(file_path)
        
        db.delete(user)
        db.commit()
    return user
