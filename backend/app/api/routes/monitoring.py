import uuid

from fastapi import APIRouter, HTTPException, Query, status

from backend.app.api.deps import CurrentUser, DbSession
from backend.app.schemas.monitoring import (
    AlertResponse,
    AlertRuleCreate,
    AlertRuleResponse,
    DomainWatchCreate,
    DomainWatchResponse,
    SslMonitorResponse,
    UptimeCheckCreate,
    UptimeCheckResponse,
)
from backend.app.services.monitoring_service import MonitoringService

router = APIRouter(prefix="/monitoring", tags=["monitoring"])


@router.post("/watches", response_model=DomainWatchResponse, status_code=status.HTTP_201_CREATED)
async def create_watch(data: DomainWatchCreate, db: DbSession, current_user: CurrentUser):
    service = MonitoringService(db)
    return await service.create_domain_watch(data, current_user.id)


@router.get("/watches", response_model=list[DomainWatchResponse])
async def list_watches(db: DbSession, current_user: CurrentUser):
    service = MonitoringService(db)
    return await service.list_domain_watches(current_user.id)


@router.delete("/watches/{watch_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_watch(watch_id: uuid.UUID, db: DbSession, current_user: CurrentUser):
    service = MonitoringService(db)
    await service.delete_domain_watch(watch_id, current_user.id)


@router.post("/uptime", response_model=UptimeCheckResponse, status_code=status.HTTP_201_CREATED)
async def create_uptime_check(data: UptimeCheckCreate, db: DbSession, current_user: CurrentUser):
    service = MonitoringService(db)
    return await service.create_uptime_check(data, current_user.id)


@router.get("/uptime", response_model=list[UptimeCheckResponse])
async def list_uptime_checks(db: DbSession, current_user: CurrentUser):
    service = MonitoringService(db)
    return await service.list_uptime_checks(current_user.id)


@router.delete("/uptime/{check_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_uptime_check(check_id: uuid.UUID, db: DbSession, current_user: CurrentUser):
    service = MonitoringService(db)
    await service.delete_uptime_check(check_id, current_user.id)


@router.get("/domains/{domain_id}/ssl", response_model=SslMonitorResponse)
async def get_ssl_monitor(domain_id: uuid.UUID, db: DbSession, current_user: CurrentUser):
    service = MonitoringService(db)
    result = await service.get_ssl_monitor(domain_id, current_user.id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SSL monitor not found")
    return result


@router.post("/domains/{domain_id}/ssl/refresh", response_model=SslMonitorResponse)
async def refresh_ssl_monitor(domain_id: uuid.UUID, db: DbSession, current_user: CurrentUser):
    service = MonitoringService(db)
    return await service.refresh_ssl_monitor(domain_id, current_user.id)


@router.post("/alerts/rules", response_model=AlertRuleResponse, status_code=status.HTTP_201_CREATED)
async def create_alert_rule(data: AlertRuleCreate, db: DbSession, current_user: CurrentUser):
    service = MonitoringService(db)
    return await service.create_alert_rule(data, current_user.id)


@router.get("/alerts/rules", response_model=list[AlertRuleResponse])
async def list_alert_rules(db: DbSession, current_user: CurrentUser):
    service = MonitoringService(db)
    return await service.list_alert_rules(current_user.id)


@router.get("/alerts", response_model=list[AlertResponse])
async def list_alerts(
    db: DbSession, current_user: CurrentUser, limit: int = Query(50, ge=1, le=200)
):
    service = MonitoringService(db)
    return await service.list_alerts(current_user.id, limit)


@router.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: uuid.UUID, db: DbSession, current_user: CurrentUser):
    service = MonitoringService(db)
    await service.acknowledge_alert(alert_id, current_user.id)
    return {"acknowledged": True}
