from sqlalchemy.orm import Session
from passlib.context import CryptContext
from datetime import datetime

from . import models, schemas

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_user_by_email(db: Session, email: str):
    return (
        db.query(models.User)
        .filter(models.User.email == email)
        .first()
    )


def get_user(db: Session, user_id: int):
    return db.get(models.User, user_id)


def create_user(db: Session, user_in: schemas.UserCreate):
    hashed = pwd_context.hash(user_in.password)
    db_user = models.User(
        email=user_in.email,
        nickname=user_in.nickname,
        password_hash=hashed,
        is_admin=user_in.is_admin,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_groups(db: Session, user_id: int):
    user = db.get(models.User, user_id)
    if not user:
        return []
    return user.groups


def get_group(db: Session, group_id: int):
    return db.get(models.Group, group_id)


def create_group(db: Session, group_in: schemas.GroupCreate, creator_id: int):
    db_group = models.Group(
        name=group_in.name,
        creator_id=creator_id,
    )
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    return db_group


def delete_group(db: Session, group_id: int):
    group = db.get(models.Group, group_id)
    if group:
        db.delete(group)
        db.commit()


def create_private_message(db: Session, sender_id: int, receiver_id: int, content: str):
    msg = models.Message(
        content=content,
        sender_id=sender_id,
        receiver_id=receiver_id,
        timestamp=datetime.utcnow(),
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg


def get_private_messages(db: Session, user1: int, user2: int):
    return (
        db.query(models.Message)
        .filter(
            ((models.Message.sender_id == user1) & (models.Message.receiver_id == user2))
            | ((models.Message.sender_id == user2) & (models.Message.receiver_id == user1))
        )
        .order_by(models.Message.timestamp)
        .all()
    )


def create_group_message(db: Session, sender_id: int, group_id: int, content: str):
    msg = models.Message(
        content=content,
        user_id=sender_id,
        group_id=group_id,
        timestamp=datetime.utcnow(),
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg


def get_group_messages(db: Session, group_id: int):
    return (
        db.query(models.Message)
        .filter(models.Message.group_id == group_id)
        .order_by(models.Message.timestamp)
        .all()
    )
