from celery import shared_task

from analysis.application.use_cases import AnalyzeImageUseCase
from analysis.infrastructure.repositories import DjangoAnalysisResultRepository


@shared_task(name="analysis.run_analysis")
def run_analysis_task(image_id: str) -> None:
    use_case = AnalyzeImageUseCase(DjangoAnalysisResultRepository())
    use_case.execute(image_id=image_id)
