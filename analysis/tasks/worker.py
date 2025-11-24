import logging
from celery import shared_task

from analysis.application.use_cases import AnalyzeImageUseCase
from analysis.infrastructure.repositories import DjangoAnalysisResultRepository

logger = logging.getLogger(__name__)


@shared_task(name="analysis.run_analysis")
def run_analysis_task(image_id: str) -> None:
    logger.info("Recibida tarea analysis.run_analysis para image_id=%s", image_id)
    use_case = AnalyzeImageUseCase(DjangoAnalysisResultRepository())
    result = use_case.execute(image_id=image_id)
    logger.info("Tarea analysis.run_analysis completada image_id=%s success=%s", image_id, result.success)
