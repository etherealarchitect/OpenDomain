from datetime import datetime

from pydantic import BaseModel


class ListingCreate(BaseModel):
    domain_id: str
    asking_price_cents: int
    description: str | None = None
    currency: str = "USD"


class ListingUpdate(BaseModel):
    asking_price_cents: int | None = None
    description: str | None = None


class ListingResponse(BaseModel):
    id: str
    domain_id: str
    seller_id: str
    asking_price_cents: int
    currency: str
    description: str | None
    status: str
    featured: bool
    views: int
    created_at: datetime
    domain_name: str | None = None

    model_config = {"from_attributes": True}


class OfferCreate(BaseModel):
    listing_id: str
    amount_cents: int
    message: str | None = None
    currency: str = "USD"


class OfferResponse(BaseModel):
    id: str
    listing_id: str
    buyer_id: str
    amount_cents: int
    currency: str
    message: str | None
    status: str
    created_at: datetime
    responded_at: datetime | None

    model_config = {"from_attributes": True}
