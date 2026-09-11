import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.billing import (
    Invoice,
    InvoiceItem,
    InvoiceStatus,
    PaymentMethod,
    Transaction,
    TransactionType,
)


class BillingService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_invoice(
        self, user_id: uuid.UUID, items: list[dict]
    ) -> Invoice:
        result = await self.db.execute(select(func.count(Invoice.id)))
        count = result.scalar() or 0
        invoice_number = f"INV-{count + 1:06d}"

        subtotal = sum(i["quantity"] * i["unit_price_cents"] for i in items)
        invoice = Invoice(
            user_id=user_id,
            invoice_number=invoice_number,
            status=InvoiceStatus.PENDING,
            subtotal_cents=subtotal,
            tax_cents=0,
            total_cents=subtotal,
        )
        self.db.add(invoice)
        await self.db.flush()

        for item in items:
            total = item["quantity"] * item["unit_price_cents"]
            inv_item = InvoiceItem(
                invoice_id=invoice.id,
                description=item["description"],
                quantity=item["quantity"],
                unit_price_cents=item["unit_price_cents"],
                total_cents=total,
                domain_id=uuid.UUID(item["domain_id"]) if item.get("domain_id") else None,
            )
            self.db.add(inv_item)

        await self.db.flush()
        await self.db.refresh(invoice)
        return invoice

    async def list_invoices(self, user_id: uuid.UUID) -> list[Invoice]:
        result = await self.db.execute(
            select(Invoice).where(Invoice.user_id == user_id).order_by(Invoice.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_invoice(self, invoice_id: uuid.UUID, user_id: uuid.UUID) -> Invoice | None:
        result = await self.db.execute(
            select(Invoice).where(Invoice.id == invoice_id, Invoice.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def mark_paid(self, invoice_id: uuid.UUID, user_id: uuid.UUID):
        invoice = await self.get_invoice(invoice_id, user_id)
        if not invoice:
            raise ValueError("Invoice not found")
        invoice.status = InvoiceStatus.PAID
        invoice.paid_at = datetime.now(UTC)

        transaction = Transaction(
            user_id=user_id,
            invoice_id=invoice.id,
            transaction_type=TransactionType.REGISTRATION,
            amount_cents=invoice.total_cents,
            description=f"Payment for {invoice.invoice_number}",
        )
        self.db.add(transaction)
        await self.db.flush()

    async def list_transactions(self, user_id: uuid.UUID, limit: int = 50) -> list[Transaction]:
        result = await self.db.execute(
            select(Transaction)
            .where(Transaction.user_id == user_id)
            .order_by(Transaction.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def add_payment_method(self, user_id: uuid.UUID, data) -> PaymentMethod:
        method = PaymentMethod(
            user_id=user_id,
            method_type=data.method_type,
            label=data.label,
            provider_id=data.provider_id,
            last_four=data.last_four,
        )
        self.db.add(method)
        await self.db.flush()
        await self.db.refresh(method)
        return method

    async def list_payment_methods(self, user_id: uuid.UUID) -> list[PaymentMethod]:
        result = await self.db.execute(
            select(PaymentMethod).where(PaymentMethod.user_id == user_id).order_by(PaymentMethod.created_at.desc())
        )
        return list(result.scalars().all())

    async def delete_payment_method(self, method_id: uuid.UUID, user_id: uuid.UUID):
        result = await self.db.execute(
            select(PaymentMethod).where(PaymentMethod.id == method_id, PaymentMethod.user_id == user_id)
        )
        method = result.scalar_one_or_none()
        if not method:
            raise ValueError("Payment method not found")
        await self.db.delete(method)

    async def set_default_payment_method(self, method_id: uuid.UUID, user_id: uuid.UUID):
        result = await self.db.execute(
            select(PaymentMethod).where(PaymentMethod.user_id == user_id)
        )
        for m in result.scalars().all():
            m.is_default = m.id == method_id
        await self.db.flush()
