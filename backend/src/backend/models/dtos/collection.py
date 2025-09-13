from backend.models.base import BaseModel
from typing import Optional

class CollectionDTO(BaseModel):
    id: Optional[str] = None
    name: str
