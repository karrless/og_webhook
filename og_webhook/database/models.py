from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship, Mapped, mapped_column

from og_webhook.database.database import Base


class User(Base):
    __tablename__ = 'users'
    # id: Mapped[int] = mapped_column(primary_key=True)
    peer_id: Mapped[int] = mapped_column(unique=True, primary_key=True)
    screen_name: Mapped[str] = mapped_column(unique=True, nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    surname: Mapped[str] = mapped_column(nullable=False)
    room_id: Mapped[int] = mapped_column(ForeignKey('rooms.id'), nullable=True)
    comfort_name: Mapped[str] = mapped_column(ForeignKey('comforts.name'), nullable=True)


class Comfort(Base):
    __tablename__ = 'comforts'
    name: Mapped[str] = mapped_column(unique=True, nullable=False, primary_key=True)
    title: Mapped[str] = mapped_column(nullable=False)
    first: Mapped[str] = mapped_column(nullable=False)
    second: Mapped[int] = mapped_column(nullable=True)
    third: Mapped[int] = mapped_column(nullable=True)
    users = relationship('User', backref='comfort')
    rooms = relationship('Room', backref='comfort')


class Room(Base):
    __tablename__ = 'rooms'
    id: Mapped[int] = mapped_column(primary_key=True)
    number: Mapped[str] = mapped_column(unique=False)
    comfort_name: Mapped[str] = mapped_column(ForeignKey('comforts.name'), nullable=True)
    users = relationship('User', backref='room')


class Answer(Base):
    __tablename__ = 'answers'
    id: Mapped[int] = mapped_column(primary_key=True)
    topic: Mapped[str] = mapped_column(unique=False, nullable=False)
    subtopic: Mapped[str] = mapped_column(unique=True, nullable=True)
    answer: Mapped[str] = mapped_column()
    attachment = mapped_column(type_=ARRAY(String), nullable=True)


class Question(Base):
    __tablename__ = 'questions'
    id: Mapped[int] = mapped_column(primary_key=True)
    topic: Mapped[str] = mapped_column(unique=False, nullable=False)
    peer_id: Mapped[int] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    surname: Mapped[str] = mapped_column(nullable=False)
    question: Mapped[str] = mapped_column(nullable=True)
    close: Mapped[bool] = mapped_column(default=False)

class Chat(Base):
    __tablename__ = 'chats' 
    peer_id: Mapped[int] = mapped_column(primary_key=True)
    faculty: Mapped[str] = mapped_column(nullable=False)
    send: Mapped[bool] = mapped_column(default=True)
    color: Mapped[str] = mapped_column(nullable=False)

class Message(Base):
    __tablename__="messages"
    __table_args__ = (
    UniqueConstraint("peer_id", "conversation_message_id", name="uix_peer_conv_msg"),
)

    id: Mapped[int] = mapped_column(primary_key=True)
    conversation_message_id:  Mapped[int] = mapped_column(nullable=False)
    from_id: Mapped[int] = mapped_column(ForeignKey('users.peer_id'), nullable=False)
    peer_id: Mapped[int] = mapped_column(ForeignKey('chats.peer_id'), nullable=False)
    message: Mapped[str] = mapped_column(nullable=True)
    sticker_id: Mapped[int] = mapped_column(nullable=True) 
    sticker_url: Mapped[str] = mapped_column(nullable=True)
    date: Mapped[int] = mapped_column(nullable=False)
    user = relationship("User", back_populates=None)
    chat = relationship("Chat", back_populates=None)
