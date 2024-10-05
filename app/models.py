from sqlalchemy import Column, String, Boolean, ForeignKey, Numeric, TIMESTAMP, Integer, text, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base
import uuid


class Client(Base):
    __tablename__ = 'clients'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    created_time = Column(TIMESTAMP, nullable=False)
    modified_time = Column(TIMESTAMP, nullable=False)
    is_disabled = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    default_language = Column(String, default='en-US')

    client_models = relationship("ClientModel", back_populates="client")


class ClientModel(Base):
    __tablename__ = "client_models"
    id = Column(UUID(as_uuid=True), primary_key=True)
    client_id = Column(UUID(as_uuid=True), ForeignKey('clients.id'))
    client = relationship("Client", back_populates="client_models")
    tasks = relationship("Task", back_populates="client_model")


class Task(Base):
    __tablename__ = "tasks"
    id = Column(UUID(as_uuid=True), primary_key=True)
    client_models_id = Column(UUID(as_uuid=True), ForeignKey('client_models.id'))
    form_handler = Column(String)
    title = Column(String)
    category = Column(String)
    client_model = relationship("ClientModel", back_populates="tasks")
    chats = relationship("Chat", back_populates="task")


class Chat(Base):
    __tablename__ = 'chats'

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=text('gen_random_uuid()'))
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    task_id = Column(UUID(as_uuid=True), ForeignKey('tasks.id'))
    title = Column(String)
    payload = Column(JSONB, nullable=False)
    request_text = Column(String, nullable=False)
    response_text = Column(String)
    created_time = Column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    modified_time = Column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    is_deleted = Column(Boolean, default=False)

    # Relationships
    task = relationship("Task")
    user = relationship("User")
    messages = relationship("Message", back_populates="chat")



class Message(Base):
    __tablename__ = 'messages'

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=text('gen_random_uuid()'))
    chat_id = Column(UUID(as_uuid=True), ForeignKey('chats.id'))  # Foreign key to the Chat table
    error_code = Column(String)
    error_text = Column(String)
    rating = Column(Integer)
    created_time = Column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    modified_time = Column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    is_deleted = Column(Boolean, default=False)

    # Relationship with Chat
    chat = relationship("Chat", back_populates="messages")


class HandlerPricing(Base):
    __tablename__ = "handler_pricing"
    id = Column(UUID(as_uuid=True), primary_key=True)
    title = Column(String)
    handler_name = Column(String)
    execution_price = Column(Numeric(32, 16))

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=func.gen_random_uuid())
    title = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    created_time = Column(DateTime(timezone=True), server_default=func.now())
    modified_time = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    is_disabled = Column(Boolean, default=False, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)

    def __repr__(self):
        return f"<User {self.email}>"
