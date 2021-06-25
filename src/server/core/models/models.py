from sqlalchemy import Column, ForeignKey, Integer, String, DATETIME
from sqlalchemy.orm import relationship

from src.server.core.models.database import Base


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(length=64), unique=True, index=True)
    email = Column(String(length=128), unique=True, index=True)
    hashed_password = Column(String(length=128))


class Message(Base):
    __tablename__ = "message"

    id = Column(Integer, primary_key=True, index=True)
    time_sent = Column(DATETIME)
    content = Column(String(length=4096))


class Conversation(Base):
    __tablename__ = "conversation"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"))
    recipient_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"))
    message_id = Column(Integer, ForeignKey("message.id", ondelete="CASCADE"))

    sender = relationship("User", foreign_keys=[sender_id])
    recipient = relationship("User", foreign_keys=[recipient_id])
    message = relationship("Message", foreign_keys=[message_id])
