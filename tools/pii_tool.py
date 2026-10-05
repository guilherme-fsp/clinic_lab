from guardrails.pii import mask_pii


def sanitize_medical_text(
    text: str,
) -> dict:
    """
    Removes or masks personally identifiable information
    from extracted medical text before downstream processing.
    """

    result = mask_pii(text)

    return {
        "sanitized_text": result.sanitized_text,
    }