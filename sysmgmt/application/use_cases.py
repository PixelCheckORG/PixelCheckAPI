from sysmgmt.domain.repositories import AuditLogRepository
from shared.application.use_case import UseCase, UseCaseResult


class RecordAuditEventUseCase(UseCase):
    def __init__(self, repository: AuditLogRepository):
        self.repository = repository

    def execute(self, actor, action: str, target: str, payload: dict) -> UseCaseResult:
        entity = self.repository.create(actor=actor, action=action, target=target, payload=payload)
        return UseCaseResult(success=True, data={"logId": entity.log_id})


class ListAuditLogsUseCase(UseCase):
    def __init__(self, repository: AuditLogRepository):
        self.repository = repository

    def execute(self, limit: int = 50) -> UseCaseResult:
        logs = self.repository.list_recent(limit=limit)
        return UseCaseResult(success=True, data=[log.__dict__ for log in logs])
