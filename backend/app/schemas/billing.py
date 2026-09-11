from datetime import datetime

from pydantic import BaseModel


class InvoiceItemResponse(BaseModel):
    id: str
    description: str
    quantity: int
    unit_price_cents: int
    total_cents: int
    domain_id: str | None

    model_config = {"from_attributes": True}


class InvoiceResponse(BaseModel):
    id: str
    invoice_number: str
    status: str
    subtotal_cents: int
    tax_cents: int
    total_cents: int
    currency: str
    notes: str | None
    due_date: datetime | None
    paid_at: datetime | None
    created_at: datetime
    items: list[InvoiceItemResponse] = []

    model_config = {"from_attributes": True}


class TransactionResponse(BaseModel):
    id: str
    transaction_type: str
    amount_cents: int
    currency: str
    description: str
    created_at: datetime

    model_config = {"from_attributes": True}


class PaymentMethodCreate(BaseModel):
    method_type: str
    label: str
    provider_id: str | None = None
    last_four: str | None = None


class PaymentMethodResponse(BaseModel):
    id: str
    method_type: str
    label: str
    last_four: str | None
    is_default: bool
    created_at: datetime

    model_config = {"from_attributes": True}
