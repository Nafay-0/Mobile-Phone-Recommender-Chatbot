import json
from sqlalchemy.orm import Session
from . import models


def create_user(db: Session, session_id: str):
    existing_user = db.query(models.User).filter(models.User.session_id == session_id).first()
    if existing_user:
        return existing_user
    db_user = models.User(session_id=session_id)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def check_user(db: Session, session_id: str):
    return db.query(models.User).filter(models.User.session_id == session_id).first()


def get_user_history(db: Session, session_id: str):
    user = db.query(models.User).filter(models.User.session_id == session_id).first()
    if not user:
        user = create_user(db, session_id)
    return user.history


def add_chat_history(db: Session, sessionId: int, conversation: list):
    db_user = db.query(models.User).filter(models.User.session_id == sessionId).first()
    db_user.history = json.dumps(conversation)
    db.commit()
    db.refresh(db_user)
    return db_user
