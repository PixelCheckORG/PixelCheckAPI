from dataclasses import dataclass


@dataclass
class ResultEntity:
    image_id: str
    label: str
    confidence: float
    model_version: str
    details: dict | None = None


@dataclass
class ReportEntity:
    report_id: str
    owner_id: str
    format: str
    status: str
    filename: str | None = None
