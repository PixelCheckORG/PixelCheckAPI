from dataclasses import asdict, dataclass
from typing import Any, Dict


@dataclass
class DTO:
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
