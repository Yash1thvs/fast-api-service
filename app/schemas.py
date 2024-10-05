from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
from datetime import datetime


class Message(BaseModel):
    id: str
    chat_id: str


class TaskCostDetails(BaseModel):
    task_name: str
    category: str
    message_count: int
    total_cost: float


class UserCostDetails(BaseModel):
    email: str
    task_costs: List[TaskCostDetails]


class Client(BaseModel):
    id: UUID
    title: str
    created_time: datetime
    modified_time: datetime

    class Config:
        # Use from_attributes instead of orm_mode in Pydantic v2+
        from_attributes = True


class ClientCostDetails(BaseModel):
    client: str
    total_cost: float
    tasks: List[TaskCostDetails]

    class Config:
        from_attributes = True
