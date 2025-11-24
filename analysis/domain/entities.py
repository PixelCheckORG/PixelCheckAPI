from dataclasses import dataclass


@dataclass
class AnalysisResultEntity:
    result_id: str
    image_id: str
    owner_id: str
    label: str
    confidence: float
    model_version: str
    details: dict
    processed_at: str
