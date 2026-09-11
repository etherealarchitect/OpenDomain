import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status

from backend.app.api.deps import CurrentUser, DbSession
from backend.app.schemas.marketplace import (
    ListingCreate,
    ListingResponse,
    OfferCreate,
    OfferResponse,
)
from backend.app.services.marketplace_service import MarketplaceService

router = APIRouter(prefix="/marketplace", tags=["marketplace"])


@router.post("/listings", response_model=ListingResponse, status_code=status.HTTP_201_CREATED)
async def create_listing(data: ListingCreate, db: DbSession, current_user: CurrentUser):
    service = MarketplaceService(db)
    return await service.create_listing(data, current_user)


@router.get("/listings", response_model=list[ListingResponse])
async def browse_listings(
    db: DbSession,
    page: int = Query(1, ge=1),
    per_page: int = Query(25, ge=1, le=100),
    sort: str = Query("newest", pattern="^(newest|price_asc|price_desc|name)$"),
):
    service = MarketplaceService(db)
    return await service.browse_listings(page, per_page, sort)


@router.get("/listings/{listing_id}", response_model=ListingResponse)
async def get_listing(listing_id: uuid.UUID, db: DbSession):
    service = MarketplaceService(db)
    listing = await service.get_listing(listing_id)
    if not listing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found")
    return listing


@router.delete("/listings/{listing_id}", status_code=status.HTTP_204_NO_CONTENT)
async def withdraw_listing(listing_id: uuid.UUID, db: DbSession, current_user: CurrentUser):
    service = MarketplaceService(db)
    await service.withdraw_listing(listing_id, current_user.id)


@router.post(
    "/listings/{listing_id}/offers",
    response_model=OfferResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_offer(
    listing_id: uuid.UUID, data: OfferCreate, db: DbSession, current_user: CurrentUser
):
    service = MarketplaceService(db)
    return await service.create_offer(listing_id, data, current_user)


@router.get("/listings/{listing_id}/offers", response_model=list[OfferResponse])
async def list_offers_on_listing(
    listing_id: uuid.UUID, db: DbSession, current_user: CurrentUser
):
    service = MarketplaceService(db)
    return await service.list_offers_for_listing(listing_id, current_user.id)


@router.get("/offers/mine", response_model=list[OfferResponse])
async def list_my_offers(db: DbSession, current_user: CurrentUser):
    service = MarketplaceService(db)
    return await service.list_my_offers(current_user.id)


@router.post("/offers/{offer_id}/accept")
async def accept_offer(offer_id: uuid.UUID, db: DbSession, current_user: CurrentUser):
    service = MarketplaceService(db)
    await service.accept_offer(offer_id, current_user.id)
    return {"accepted": True}


@router.post("/offers/{offer_id}/reject")
async def reject_offer(offer_id: uuid.UUID, db: DbSession, current_user: CurrentUser):
    service = MarketplaceService(db)
    await service.reject_offer(offer_id, current_user.id)
    return {"rejected": True}
