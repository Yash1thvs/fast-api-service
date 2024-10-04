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

