import uuid

from fastapi import APIRouter, HTTPException, Query, status

from backend.app.api.deps import CurrentUser, DbSession
from backend.app.schemas.billing import (
    InvoiceResponse,
    PaymentMethodCreate,
    PaymentMethodResponse,
    TransactionResponse,
)
from backend.app.services.billing_service import BillingService

router = APIRouter(prefix="/billing", tags=["billing"])


@router.get("/invoices", response_model=list[InvoiceResponse])
async def list_invoices(db: DbSession, current_user: CurrentUser):
    service = BillingService(db)
    return await service.list_invoices(current_user.id)


@router.get("/invoices/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(invoice_id: uuid.UUID, db: DbSession, current_user: CurrentUser):
    service = BillingService(db)
    invoice = await service.get_invoice(invoice_id, current_user.id)
    if not invoice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")
    return invoice


@router.post("/invoices/{invoice_id}/pay")
async def pay_invoice(invoice_id: uuid.UUID, db: DbSession, current_user: CurrentUser):
    service = BillingService(db)
    await service.pay_invoice(invoice_id, current_user.id)
    return {"paid": True}


@router.get("/transactions", response_model=list[TransactionResponse])
async def list_transactions(
    db: DbSession, current_user: CurrentUser, limit: int = Query(50, ge=1, le=200)
):
    service = BillingService(db)
    return await service.list_transactions(current_user.id, limit)


@router.post("/payment-methods", response_model=PaymentMethodResponse, status_code=status.HTTP_201_CREATED)
async def add_payment_method(data: PaymentMethodCreate, db: DbSession, current_user: CurrentUser):
    service = BillingService(db)
    return await service.add_payment_method(data, current_user.id)


@router.get("/payment-methods", response_model=list[PaymentMethodResponse])
async def list_payment_methods(db: DbSession, current_user: CurrentUser):
    service = BillingService(db)
    return await service.list_payment_methods(current_user.id)


@router.delete("/payment-methods/{method_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_payment_method(method_id: uuid.UUID, db: DbSession, current_user: CurrentUser):
    service = BillingService(db)
    await service.delete_payment_method(method_id, current_user.id)


@router.post("/payment-methods/{method_id}/default")
async def set_default_payment_method(method_id: uuid.UUID, db: DbSession, current_user: CurrentUser):
    service = BillingService(db)
    await service.set_default_payment_method(method_id, current_user.id)
    return {"default": True}
