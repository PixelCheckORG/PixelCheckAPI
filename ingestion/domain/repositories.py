from abc import ABC, abstractmethod
from typing import Iterable, Optional

from .entities import ImageEntity


class ImageRepository(ABC):
    @abstractmethod
    def create(self, **kwargs) -> ImageEntity: ...

    @abstractmethod
    def get(self, image_id: str) -> Optional[ImageEntity]: ...

    @abstractmethod
    def exists_checksum(self, checksum: str, uploader_id: str) -> bool: ...

    @abstractmethod
    def list_by_uploader(self, uploader_id: str) -> Iterable[ImageEntity]: ...
