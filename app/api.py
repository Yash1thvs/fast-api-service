from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.models import Client as ClientModel  # SQLAlchemy model
from app.schemas import Client as ClientSchema  # Pydantic schema

from app.schemas import ClientCostDetails

from .crud import get_client_cost

from app.database import get_db

router = APIRouter()


@router.get("/clients", response_model=List[ClientSchema])
def list_clients(db: Session = Depends(get_db)):
    clients = db.query(ClientModel).all()  # This is the ORM model query
    if not clients:
        raise HTTPException(status_code=404, detail="No clients found")
    return clients


@router.get("/clients/{client_id}/cost", response_model=ClientCostDetails)
def client_cost(client_id: str, month: int = 10, db: Session = Depends(get_db)):
    cost_details = get_client_cost(db, client_id, month)
    if not cost_details:
        raise HTTPException(status_code=404, detail="No cost details found")

    return {
        "client": client_id,
        "total_cost": sum([c.total_cost for c in cost_details]),
        "tasks": [
            {
                "task_name": c.task_name,
                "category": c.category,
                "message_count": c.message_count,
                "total_cost": c.total_cost,
                "user_email": c.user_email
            }
            for c in cost_details
        ]
    }