from abc import ABC, abstractmethod

from .entities import AuditLogEntity


class AuditLogRepository(ABC):
    @abstractmethod
    def create(self, **kwargs) -> AuditLogEntity: ...

    @abstractmethod
    def list_recent(self, limit: int = 50) -> list[AuditLogEntity]: ...
