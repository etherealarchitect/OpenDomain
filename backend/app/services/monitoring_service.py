import uuid
from datetime import UTC, datetime, timedelta

import httpx
from backend.app.models.domain import Domain
from backend.app.models.monitoring import (
    Alert,
    AlertRule,
    AlertStatus,
    AlertType,
    CheckStatus,
    DomainWatch,
    SslMonitor,
    UptimeCheck,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class MonitoringService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_domain_watch(self, user_id: uuid.UUID, data) -> DomainWatch:
        watch = DomainWatch(
            user_id=user_id,
            domain_name=data.query.lower().strip(),
            notify_email=data.notify_email,
        )
        self.db.add(watch)
        await self.db.flush()
        await self.db.refresh(watch)
        return watch

    async def list_domain_watches(self, user_id: uuid.UUID) -> list[DomainWatch]:
        result = await self.db.execute(
            select(DomainWatch)
            .where(DomainWatch.user_id == user_id)
            .order_by(DomainWatch.created_at.desc())
        )
        return list(result.scalars().all())

    async def delete_domain_watch(self, watch_id: uuid.UUID, user_id: uuid.UUID):
        result = await self.db.execute(
            select(DomainWatch).where(DomainWatch.id == watch_id, DomainWatch.user_id == user_id)
        )
        watch = result.scalar_one_or_none()
        if not watch:
            raise ValueError("Watch not found")
        await self.db.delete(watch)

    async def check_domain_watches(self):
        result = await self.db.execute(select(DomainWatch).where(DomainWatch.active.is_(True)))
        watches = result.scalars().all()
        from backend.app.services.whois_service import WhoisService

        whois_service = WhoisService()
        for watch in watches:
            try:
                info = await whois_service.lookup(watch.domain_name)
                was_available = watch.is_available
                # Registrar data is optional in both RDAP and WHOIS.  Only an
                # authoritative RDAP "available" response can mark a watch available.
                if info.lookup_status == "available":
                    # Kept for registry-backed implementations that can prove
                    # availability; RDAP 404 deliberately returns not_found.
                    watch.is_available = True
                elif info.lookup_status == "registered":
                    watch.is_available = False
                else:
                    # Keep the prior state on an inconclusive/failed lookup.
                    watch.last_checked = datetime.now(UTC)
                    continue
                watch.last_checked = datetime.now(UTC)
                if watch.is_available and not was_available:
                    alert = Alert(
                        user_id=watch.user_id,
                        alert_type=AlertType.DOMAIN_AVAILABLE,
                        title=f"{watch.domain_name} is now available",
                        message=f"The domain {watch.domain_name} you were watching is now available for registration.",
                    )
                    self.db.add(alert)
            except Exception:
                # A failed lookup must not change availability state.
                continue
        await self.db.flush()

    async def create_uptime_check(self, user_id: uuid.UUID, data) -> UptimeCheck:
        check = UptimeCheck(
            user_id=user_id,
            domain_id=uuid.UUID(data.domain_id),
            url=data.url,
            check_interval_seconds=data.check_interval_seconds,
        )
        self.db.add(check)
        await self.db.flush()
        await self.db.refresh(check)
        return check

    async def list_uptime_checks(self, user_id: uuid.UUID) -> list[UptimeCheck]:
        result = await self.db.execute(
            select(UptimeCheck)
            .where(UptimeCheck.user_id == user_id)
            .order_by(UptimeCheck.created_at.desc())
        )
        return list(result.scalars().all())

    async def delete_uptime_check(self, check_id: uuid.UUID, user_id: uuid.UUID):
        result = await self.db.execute(
            select(UptimeCheck).where(UptimeCheck.id == check_id, UptimeCheck.user_id == user_id)
        )
        check = result.scalar_one_or_none()
        if not check:
            raise ValueError("Uptime check not found")
        await self.db.delete(check)

    async def run_uptime_checks(self):
        result = await self.db.execute(select(UptimeCheck).where(UptimeCheck.active.is_(True)))
        checks = result.scalars().all()
        async with httpx.AsyncClient(timeout=10) as client:
            for check in checks:
                old_status = check.status
                try:
                    start = datetime.now(UTC)
                    resp = await client.head(check.url)
                    elapsed_ms = int((datetime.now(UTC) - start).total_seconds() * 1000)
                    check.response_time_ms = elapsed_ms
                    check.status = (
                        CheckStatus.UP if resp.status_code < 500 else CheckStatus.DEGRADED
                    )
                except Exception:
                    check.status = CheckStatus.DOWN
                    check.response_time_ms = None

                check.last_checked = datetime.now(UTC)
                if check.status != old_status:
                    check.last_status_change = datetime.now(UTC)
                    if check.status == CheckStatus.DOWN:
                        alert = Alert(
                            user_id=check.user_id,
                            alert_type=AlertType.UPTIME_DOWN,
                            title=f"Downtime detected: {check.url}",
                            message=f"The URL {check.url} is not responding.",
                            domain_id=check.domain_id,
                        )
                        self.db.add(alert)
        await self.db.flush()

    async def get_ssl_info(self, domain_id: uuid.UUID, user_id: uuid.UUID) -> SslMonitor | None:
        result = await self.db.execute(
            select(SslMonitor).where(
                SslMonitor.domain_id == domain_id, SslMonitor.user_id == user_id
            )
        )
        return result.scalar_one_or_none()

    async def refresh_ssl_info(self, domain_id: uuid.UUID, user_id: uuid.UUID) -> SslMonitor:
        monitor = await self.get_ssl_info(domain_id, user_id)
        if not monitor:
            monitor = SslMonitor(user_id=user_id, domain_id=domain_id)
            self.db.add(monitor)
        monitor.last_checked = datetime.now(UTC)
        await self.db.flush()
        await self.db.refresh(monitor)
        return monitor

    async def create_alert_rule(self, user_id: uuid.UUID, data) -> AlertRule:
        rule = AlertRule(
            user_id=user_id,
            domain_id=uuid.UUID(data.domain_id) if data.domain_id else None,
            alert_type=AlertType(data.alert_type),
            threshold_days=data.threshold_days,
            webhook_url=data.webhook_url,
            email=data.email,
        )
        self.db.add(rule)
        await self.db.flush()
        await self.db.refresh(rule)
        return rule

    async def list_alert_rules(self, user_id: uuid.UUID) -> list[AlertRule]:
        result = await self.db.execute(
            select(AlertRule)
            .where(AlertRule.user_id == user_id)
            .order_by(AlertRule.created_at.desc())
        )
        return list(result.scalars().all())

    async def list_alerts(self, user_id: uuid.UUID, limit: int = 50) -> list[Alert]:
        result = await self.db.execute(
            select(Alert)
            .where(Alert.user_id == user_id)
            .order_by(Alert.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def acknowledge_alert(self, alert_id: uuid.UUID, user_id: uuid.UUID):
        result = await self.db.execute(
            select(Alert).where(Alert.id == alert_id, Alert.user_id == user_id)
        )
        alert = result.scalar_one_or_none()
        if not alert:
            raise ValueError("Alert not found")
        alert.status = AlertStatus.ACKNOWLEDGED
        alert.acknowledged_at = datetime.now(UTC)
        await self.db.flush()

    async def check_expiry_alerts(self):
        result = await self.db.execute(
            select(AlertRule).where(
                AlertRule.active.is_(True),
                AlertRule.alert_type == AlertType.EXPIRY_WARNING,
            )
        )
        rules = result.scalars().all()
        for rule in rules:
            threshold = rule.threshold_days or 30
            cutoff = datetime.now(UTC) + timedelta(days=threshold)
            query = select(Domain).where(
                Domain.owner_id == rule.user_id,
                Domain.expiry_date <= cutoff,
                Domain.expiry_date > datetime.now(UTC),
                Domain.status == "active",
            )
            if rule.domain_id:
                query = query.where(Domain.id == rule.domain_id)
            domains_result = await self.db.execute(query)
            for domain in domains_result.scalars().all():
                days_left = (domain.expiry_date - datetime.now(UTC)).days
                alert = Alert(
                    user_id=rule.user_id,
                    rule_id=rule.id,
                    alert_type=AlertType.EXPIRY_WARNING,
                    title=f"{domain.name} expires in {days_left} days",
                    message=f"Your domain {domain.name} will expire on {domain.expiry_date.strftime('%Y-%m-%d')}. Consider renewing it.",
                    domain_id=domain.id,
                )
                self.db.add(alert)
        await self.db.flush()
