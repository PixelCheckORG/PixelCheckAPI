from abc import ABC, abstractmethod
from typing import Iterable, Optional

from .entities import ReportEntity, ResultEntity


class ResultsQueryRepository(ABC):
    @abstractmethod
    def get_by_image(self, image_id: str, owner_id: str, can_view_all: bool) -> Optional[ResultEntity]: ...


class ReportRepository(ABC):
    @abstractmethod
    def create_report(self, **kwargs) -> ReportEntity: ...

    @abstractmethod
    def update_report(self, report_id: str, **kwargs) -> ReportEntity: ...

    @abstractmethod
    def get_report(self, report_id: str, owner_id: str, can_view_all: bool) -> Optional[ReportEntity]: ...
