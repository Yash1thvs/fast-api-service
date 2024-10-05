from pydantic import BaseModel
from typing import List, Optional


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
    id: str
    title: str


class ClientCostDetails(BaseModel):
    client: Client
    total_cost: float
    tasks: List[TaskCostDetails]
