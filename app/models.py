from sqlalchemy import Column, String, Boolean, ForeignKey, Numeric, TIMESTAMP, JSONB, Integer, Text, UUID
from sqlalchemy.orm import relationship
from .database import Base


class Client(Base):
    __tablename__ = "clients"
    id = Column(UUID(as_uuid=True), primary_key=True, index=True)
    title = Column(String)
    is_disabled = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)

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
    __tablename__ = "chats"
    id = Column(UUID(as_uuid=True), primary_key=True)
    task_id = Column(UUID(as_uuid=True), ForeignKey('tasks.id'))
    task = relationship("Task", back_populates="chats")
    messages = relationship("Message", back_populates="chat")


class Message(Base):
    __tablename__ = "messages"
    id = Column(UUID(as_uuid=True), primary_key=True)
    chat_id = Column(UUID(as_uuid=True), ForeignKey('chats.id'))
    chat = relationship("Chat", back_populates="messages")


class HandlerPricing(Base):
    __tablename__ = "handler_pricing"
    id = Column(UUID(as_uuid=True), primary_key=True)
    title = Column(String)
    handler_name = Column(String)
    execution_price = Column(Numeric(32, 16))
