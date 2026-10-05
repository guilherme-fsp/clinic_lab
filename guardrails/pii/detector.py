import re

from guardrails.pii.pii_schema import DetectedPII


PII_PATTERNS = {
    "CPF": re.compile(
        r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b"
    ),
    "EMAIL": re.compile(
        r"\b[A-Za-z0-9._%+-]+"
        r"@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
    ),
    "PHONE": re.compile(
        r"(?:\+?55\s*)?"
        r"(?:\(?\d{2}\)?\s*)?"
        r"(?:9?\d{4})[-\s]?\d{4}"
    ),
    "DATE_OF_BIRTH": re.compile(
        r"\b\d{2}/\d{2}/\d{4}\b"
    ),
    "PERSON": re.compile(
        r"(?i)(?:nome|paciente)\s*:\s*"
        r"([A-Za-zÀ-ÿ]+(?:\s+[A-Za-zÀ-ÿ]+){1,5})"
    ),
}


def detect_pii(
    text: str,
) -> list[DetectedPII]:

    entities: list[DetectedPII] = []

    for entity_type, pattern in PII_PATTERNS.items():

        for match in pattern.finditer(text):

            if entity_type == "PERSON":
                value = match.group(1)
                start, end = match.span(1)

            else:
                value = match.group()
                start, end = match.span()

            entities.append(
                DetectedPII(
                    entity_type=entity_type,
                    value=value,
                    start=start,
                    end=end,
                )
            )

    return sorted(
        entities,
        key=lambda entity: entity.start,
    )