import pytest

from mcp_servers.ocr.service import (
    OCRServiceError,
)

from mcp_servers.ocr.service import LLMOCRService

class FakeClient:
    pass

@pytest.mark.anyio
async def test_llm_ocr_rejects_invalid_base64():

    service = LLMOCRService(
        client=FakeClient(),
        model="fake-model",
    )

    with pytest.raises(
        OCRServiceError,
        match="Invalid base64",
    ):
        await service.extract_text(
            image_base64="%%%invalid%%%",
            mime_type="image/png",
        )

@pytest.mark.anyio
async def test_llm_ocr_rejects_invalid_mime_type():

    service = LLMOCRService(
        client=FakeClient(),
        model="fake-model",
    )

    with pytest.raises(
        OCRServiceError,
        match="Unsupported image MIME type",
    ):
        await service.extract_text(
            image_base64="AAAA",
            mime_type="application/pdf",
        )