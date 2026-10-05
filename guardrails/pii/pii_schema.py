from pydantic import BaseModel


class DetectedPII(BaseModel):
    entity_type: str
    value: str
    start: int
    end: int


class SanitizationResult(BaseModel):
    sanitized_text: str
    detected_entities: list[DetectedPII]