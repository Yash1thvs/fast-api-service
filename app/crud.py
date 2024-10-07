from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from .models import Client, Task, Chat, Message, HandlerPricing, User, ClientModel


def get_clients(db: Session):
    return db.query(Client).filter(Client.is_deleted == False, Client.is_disabled == False).all()


def get_client_cost(db: Session, client_id: str, month: int):
    try:
        cost_details = db.query(
            Task.title.label('task_name'),
            Task.category.label('category'),
            func.count(Message.id).label('message_count'),
            func.sum(HandlerPricing.execution_price).label('total_cost'),
            User.email.label('user_email')  # Include the user's email in the query
        ).join(Chat, Task.id == Chat.task_id) \
            .join(Chat.messages) \
            .join(User, Chat.user_id == User.id) \
            .join(HandlerPricing, Task.form_handler == HandlerPricing.handler_name) \
            .join(ClientModel, Task.client_models_id == ClientModel.id) \
            .filter(
                ClientModel.client_id == client_id,
                func.date_part('month', Chat.created_time) == month
            ) \
            .group_by(Task.title, Task.category, User.email).all()
        return cost_details
    except Exception as e:
        # Log the error
        print(f"Error fetching client cost details: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")



