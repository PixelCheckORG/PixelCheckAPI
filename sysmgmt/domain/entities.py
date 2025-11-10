from dataclasses import dataclass


@dataclass
class AuditLogEntity:
    log_id: str
    actor_id: str | None
    action: str
    target: str
    payload: dict
    occurred_at: str
