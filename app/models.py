from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Table, Text
from sqlalchemy.orm import relationship
from .database import Base


memberships = Table(
    "memberships",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("group_id", Integer, ForeignKey("groups.id", ondelete="CASCADE"), primary_key=True),
)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    nickname = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    groups = relationship(
        "Group",
        secondary=memberships,
        back_populates="members",
    )

    created_groups = relationship(
        "Group",
        back_populates="creator",
        cascade="all, delete-orphan",
    )

    sent_private_messages = relationship(
        "Message",
        foreign_keys="[Message.sender_id]",
        back_populates="sender",
        cascade="all, delete-orphan",
    )
    received_private_messages = relationship(
        "Message",
        foreign_keys="[Message.receiver_id]",
        back_populates="receiver",
        cascade="all, delete-orphan",
    )

    
    sent_group_messages = relationship(
        "Message",
        foreign_keys="[Message.user_id]",
        back_populates="user",
        cascade="all, delete-orphan",
    )


class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    creator_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=False)
    creator = relationship(
        "User",
        back_populates="created_groups",
    )

    members = relationship(
        "User",
        secondary=memberships,
        back_populates="groups",
    )

    messages = relationship(
        "Message",
        back_populates="group",
        cascade="all, delete-orphan",
    )





class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True, nullable=False)
    
    sender_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    receiver_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)

    group_id = Column(Integer, ForeignKey("groups.id", ondelete="CASCADE"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"),  nullable=True)

    sender = relationship(
        "User",
        foreign_keys=[sender_id],
        back_populates="sent_private_messages",
    )
    receiver = relationship(
        "User",
        foreign_keys=[receiver_id],
        back_populates="received_private_messages",
    )
    user = relationship(
        "User",
        foreign_keys=[user_id],
        back_populates="sent_group_messages",
    )
    group = relationship(
        "Group",
        foreign_keys=[group_id],
        back_populates="messages",
    )
