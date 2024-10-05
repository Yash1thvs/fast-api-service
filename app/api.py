from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.models import Client as ClientModel  # SQLAlchemy model
from app.schemas import Client as ClientSchema  # Pydantic schema

from app.schemas import ClientCostDetails, UserCostDetails

from .crud import get_clients, get_client_cost, get_user_cost

from app.database import get_db

router = APIRouter()


@router.get("/clients", response_model=List[ClientSchema])
def list_clients(db: Session = Depends(get_db)):
    # Use the SQLAlchemy model (ClientModel) to query the database
    clients = db.query(ClientModel).all()  # This is the ORM model query
    if not clients:
        raise HTTPException(status_code=404, detail="No clients found")

    # Return the clients (they will be automatically converted to the Pydantic schema)
    return clients


@router.get("/clients/{client_id}/cost", response_model=ClientCostDetails)
def client_cost(client_id: str, month: int = 10, db: Session = Depends(get_db)):
    cost_details = get_client_cost(db, client_id, month)
    if not cost_details:
        raise HTTPException(status_code=404, detail="No cost details found")

    # Return client_id as a string directly
    return {
        "client": client_id,  # Return the client_id as a string
        "total_cost": sum([c.total_cost for c in cost_details]),
        "tasks": cost_details
    }


@router.get("/clients/{client_id}/user/{user_email}/cost", response_model=UserCostDetails)
def user_cost(client_id: str, user_email: str, month: int = 10, db: Session = Depends(get_db)):
    user_cost_details = get_user_cost(db, client_id, user_email, month)
    if not user_cost_details:
        raise HTTPException(status_code=404, detail="No user cost details found")
    return {"email": user_email, "task_costs": user_cost_details}