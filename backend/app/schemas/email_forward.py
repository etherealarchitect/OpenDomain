from datetime import datetime

from pydantic import BaseModel


class EmailForwardCreate(BaseModel):
    domain_id: str
    source_address: str
    destination_email: str


class EmailForwardResponse(BaseModel):
    id: str
    domain_id: str
    source_address: str
    destination_email: str
    active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
