import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.domain import Domain
from backend.app.models.marketplace import Listing, ListingStatus, Offer, OfferStatus


class MarketplaceService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_listing(self, user_id: uuid.UUID, data) -> Listing:
        domain_id = uuid.UUID(data.domain_id)
        result = await self.db.execute(
            select(Domain).where(Domain.id == domain_id, Domain.owner_id == user_id)
        )
        domain = result.scalar_one_or_none()
        if not domain:
            raise ValueError("Domain not found or you don't own it")

        existing = await self.db.execute(
            select(Listing).where(
                Listing.domain_id == domain_id,
                Listing.status == ListingStatus.ACTIVE,
            )
        )
        if existing.scalar_one_or_none():
            raise ValueError("Domain already has an active listing")

        listing = Listing(
            domain_id=domain_id,
            seller_id=user_id,
            asking_price_cents=data.asking_price_cents,
            currency=data.currency,
            description=data.description,
        )
        self.db.add(listing)
        await self.db.flush()
        await self.db.refresh(listing)
        return listing

    async def list_listings(self, status: str = "active", page: int = 1, per_page: int = 25) -> list[Listing]:
        query = select(Listing)
        if status:
            query = query.where(Listing.status == ListingStatus(status))
        query = query.order_by(Listing.featured.desc(), Listing.created_at.desc())
        query = query.offset((page - 1) * per_page).limit(per_page)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_listing(self, listing_id: uuid.UUID) -> Listing | None:
        result = await self.db.execute(select(Listing).where(Listing.id == listing_id))
        listing = result.scalar_one_or_none()
        if listing:
            listing.views += 1
            await self.db.flush()
        return listing

    async def update_listing(self, listing_id: uuid.UUID, user_id: uuid.UUID, data):
        result = await self.db.execute(
            select(Listing).where(Listing.id == listing_id, Listing.seller_id == user_id)
        )
        listing = result.scalar_one_or_none()
        if not listing:
            raise ValueError("Listing not found")
        if data.asking_price_cents is not None:
            listing.asking_price_cents = data.asking_price_cents
        if data.description is not None:
            listing.description = data.description
        await self.db.flush()
        await self.db.refresh(listing)
        return listing

    async def withdraw_listing(self, listing_id: uuid.UUID, user_id: uuid.UUID):
        result = await self.db.execute(
            select(Listing).where(Listing.id == listing_id, Listing.seller_id == user_id)
        )
        listing = result.scalar_one_or_none()
        if not listing:
            raise ValueError("Listing not found")
        listing.status = ListingStatus.WITHDRAWN
        await self.db.flush()

    async def create_offer(self, buyer_id: uuid.UUID, data) -> Offer:
        listing_id = uuid.UUID(data.listing_id)
        result = await self.db.execute(
            select(Listing).where(Listing.id == listing_id, Listing.status == ListingStatus.ACTIVE)
        )
        listing = result.scalar_one_or_none()
        if not listing:
            raise ValueError("Listing not found or no longer active")
        if listing.seller_id == buyer_id:
            raise ValueError("Cannot make an offer on your own listing")

        offer = Offer(
            listing_id=listing_id,
            buyer_id=buyer_id,
            amount_cents=data.amount_cents,
            currency=data.currency,
            message=data.message,
        )
        self.db.add(offer)
        await self.db.flush()
        await self.db.refresh(offer)
        return offer

    async def list_offers_for_listing(self, listing_id: uuid.UUID, user_id: uuid.UUID) -> list[Offer]:
        result = await self.db.execute(
            select(Listing).where(Listing.id == listing_id, Listing.seller_id == user_id)
        )
        if not result.scalar_one_or_none():
            raise ValueError("Listing not found")
        result = await self.db.execute(
            select(Offer).where(Offer.listing_id == listing_id).order_by(Offer.created_at.desc())
        )
        return list(result.scalars().all())

    async def list_my_offers(self, user_id: uuid.UUID) -> list[Offer]:
        result = await self.db.execute(
            select(Offer).where(Offer.buyer_id == user_id).order_by(Offer.created_at.desc())
        )
        return list(result.scalars().all())

    async def accept_offer(self, offer_id: uuid.UUID, user_id: uuid.UUID):
        result = await self.db.execute(select(Offer).where(Offer.id == offer_id))
        offer = result.scalar_one_or_none()
        if not offer:
            raise ValueError("Offer not found")
        listing_result = await self.db.execute(
            select(Listing).where(Listing.id == offer.listing_id, Listing.seller_id == user_id)
        )
        listing = listing_result.scalar_one_or_none()
        if not listing:
            raise ValueError("Not your listing")
        offer.status = OfferStatus.ACCEPTED
        offer.responded_at = datetime.now(UTC)
        listing.status = ListingStatus.SOLD
        other_offers = await self.db.execute(
            select(Offer).where(
                Offer.listing_id == listing.id,
                Offer.id != offer_id,
                Offer.status == OfferStatus.PENDING,
            )
        )
        for other in other_offers.scalars().all():
            other.status = OfferStatus.REJECTED
            other.responded_at = datetime.now(UTC)
        await self.db.flush()

    async def reject_offer(self, offer_id: uuid.UUID, user_id: uuid.UUID):
        result = await self.db.execute(select(Offer).where(Offer.id == offer_id))
        offer = result.scalar_one_or_none()
        if not offer:
            raise ValueError("Offer not found")
        listing_result = await self.db.execute(
            select(Listing).where(Listing.id == offer.listing_id, Listing.seller_id == user_id)
        )
        if not listing_result.scalar_one_or_none():
            raise ValueError("Not your listing")
        offer.status = OfferStatus.REJECTED
        offer.responded_at = datetime.now(UTC)
        await self.db.flush()
