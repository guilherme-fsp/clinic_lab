from guardrails.pii.detector import detect_pii
from guardrails.pii.pii_schema import SanitizationResult


def mask_pii(
    text: str,
) -> SanitizationResult:

    entities = detect_pii(text)

    sanitized_text = text

    counters: dict[str, int] = {}

    for entity in reversed(entities):

        counters.setdefault(
            entity.entity_type,
            0,
        )

        counters[entity.entity_type] += 1

        replacement = (
            f"[{entity.entity_type}_"
            f"{counters[entity.entity_type]}]"
        )

        sanitized_text = (
            sanitized_text[:entity.start]
            + replacement
            + sanitized_text[entity.end:]
        )

    return SanitizationResult(
        sanitized_text=sanitized_text,
        detected_entities=entities,
    )