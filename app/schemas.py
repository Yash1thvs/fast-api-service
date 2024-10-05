from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid


# Model for individual client record
class ClientResponse(BaseModel):
    id: uuid.UUID
    title: str
    created_time: datetime
    modified_time: datetime
    is_disabled: bool
    is_deleted: bool
    default_language: Optional[str]  # Optional if nullable


# Model for paginated response
class PaginatedClientsResponse(BaseModel):
    total: int
    clients: List[ClientResponse]


class ClientCostResponse(BaseModel):
    client_id: str  # Ensuring client_id is returned as a string
    total_cost: float
    year: int
    month: int


class ClientTotalCostResponse(BaseModel):
    client_id: str
    client_title: str
    total_cost: float  # Overall total for the period
    monthly_breakdown: List[ClientCostResponse]  # Breakdown by each month


# Models to structure the API response
class TaskCostResponse(BaseModel):
    task_title: str
    message_count: int
    total_cost: float


class CategoryCostResponse(BaseModel):
    handler_category: str
    tasks: List[TaskCostResponse]


# Define Pydantic models for the response
class TaskCostBreakdown(BaseModel):
    task_title: str
    message_count: int
    total_cost: float


class HandlerCategoryBreakdown(BaseModel):
    handler_category: str
    tasks: List[TaskCostBreakdown]


class ClientTotalCostResponseCategory(BaseModel):
    client_id: str
    total_cost: float
    categories: List[HandlerCategoryBreakdown]


class CategoryCostDetail(BaseModel):
    category_title: str
    tasks: List[TaskCostBreakdown]


class ClientCostResponseUser(BaseModel):
    client_id: str
    total_cost: float
    categories: List[CategoryCostDetail]
