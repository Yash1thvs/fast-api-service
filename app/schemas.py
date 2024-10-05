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
    client_title: str
    total_cost: float
    year: int
    month: int


class ClientTotalCostResponse(BaseModel):
    client_id: str
    client_title: str
    total_cost: float  # Overall total for the period
    monthly_breakdown: List[ClientCostResponse]  # Breakdown by each month



