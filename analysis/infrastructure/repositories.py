from analysis.domain.entities import AnalysisResultEntity
from analysis.domain.repositories import AnalysisResultRepository
from analysis.models import AnalysisResult


def _to_entity(instance: AnalysisResult) -> AnalysisResultEntity:
    return AnalysisResultEntity(
        result_id=str(instance.result_id),
        image_id=str(instance.image_id),
        owner_id=str(instance.owner_id),
        label=instance.label,
        confidence=float(instance.confidence),
        model_version=instance.model_version,
        processed_at=instance.processed_at.isoformat(),
    )


class DjangoAnalysisResultRepository(AnalysisResultRepository):
    def save_result(self, **kwargs) -> AnalysisResultEntity:
        image = kwargs["image"]
        defaults = kwargs.copy()
        defaults.pop("image", None)
        result, _ = AnalysisResult.objects.update_or_create(
            image=image,
            defaults=defaults,
        )
        return _to_entity(result)

    def get_by_image(self, image_id: str) -> AnalysisResultEntity | None:
        try:
            result = AnalysisResult.objects.get(image_id=image_id)
        except AnalysisResult.DoesNotExist:
            return None
        return _to_entity(result)
