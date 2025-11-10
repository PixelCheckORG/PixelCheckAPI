from abc import ABC, abstractmethod
from typing import Optional

from .entities import AnalysisResultEntity


class AnalysisResultRepository(ABC):
    @abstractmethod
    def save_result(self, **kwargs) -> AnalysisResultEntity: ...

    @abstractmethod
    def get_by_image(self, image_id: str) -> Optional[AnalysisResultEntity]: ...
