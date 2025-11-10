from sysmgmt.domain.entities import AuditLogEntity
from sysmgmt.domain.repositories import AuditLogRepository
from sysmgmt.models import AuditLog


def _entity(instance: AuditLog) -> AuditLogEntity:
    return AuditLogEntity(
        log_id=str(instance.log_id),
        actor_id=str(instance.actor_id) if instance.actor_id else None,
        action=instance.action,
        target=instance.target,
        payload=instance.payload,
        occurred_at=instance.occurred_at.isoformat(),
    )


class DjangoAuditLogRepository(AuditLogRepository):
    def create(self, **kwargs) -> AuditLogEntity:
        log = AuditLog.objects.create(**kwargs)
        return _entity(log)

    def list_recent(self, limit: int = 50) -> list[AuditLogEntity]:
        return [_entity(log) for log in AuditLog.objects.order_by("-occurred_at")[:limit]]
