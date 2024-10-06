from sqlalchemy.orm import Session
from sqlalchemy import func
from .models import Client, Task, Chat, Message, HandlerPricing, User, ClientModel


def get_clients(db: Session):
    return db.query(Client).filter(Client.is_deleted == False, Client.is_disabled == False).all()


def get_client_cost(db: Session, client_id: str, month: int):
    # Get cost details for a specific client and month
    cost_details = db.query(
        Task.title.label('task_name'),
        Task.category.label('category'),
        func.count(Message.id).label('message_count'),
        func.sum(HandlerPricing.execution_price).label('total_cost')
    ).join(Chat, Task.id == Chat.task_id) \
        .join(Chat.messages) \
        .join(HandlerPricing, Task.form_handler == HandlerPricing.handler_name) \
        .join(ClientModel, Task.client_models_id == ClientModel.id) \
        .filter(ClientModel.client_id == client_id, func.date_part('month', Chat.created_time) == month) \
        .group_by(Task.title, Task.category).all()

    return cost_details


def get_user_cost(db: Session, client_id: str, user_id: str, month: int):
    # Fetch costs for the specified user, client, and month
    user_costs = db.query(
        Task.title.label('task_name'),
        Task.category.label('category'),
        func.count(Message.id).label('message_count'),
        func.sum(HandlerPricing.execution_price).label('total_cost')
    ).join(Chat, Task.id == Chat.task_id) \
        .join(Message, Chat.id == Message.chat_id) \
        .join(HandlerPricing, Task.form_handler == HandlerPricing.handler_name) \
        .join(User, Chat.user_id == User.id) \
        .filter(
            User.id == user_id,
            func.date_part('month', Message.created_time) == month,
            Task.client_models_id == client_id
        ) \
        .group_by(Task.title, Task.category).all()
    print(str(user_costs))
    return user_costs
