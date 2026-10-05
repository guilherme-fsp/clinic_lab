import base64

import pytest

from mcp_servers.ocr.service import (
    LLMOCRService,
)


class FakeResponse:

    text = (
        "Paciente: João da Silva\n"
        "Hemograma Completo\n"
        "Glicemia"
    )


class FakeModels:

    async def generate_content(
        self,
        **kwargs,
    ):
        return FakeResponse()


class FakeAsyncClient:

    models = FakeModels()


class FakeClient:

    aio = FakeAsyncClient()


@pytest.mark.anyio
async def test_llm_ocr_extracts_text():

    fake_image = b"fake-image-content"

    encoded_image = base64.b64encode(
        fake_image
    ).decode("utf-8")

    service = LLMOCRService(
        client=FakeClient(),
        model="fake-model",
    )

    result = await service.extract_text(
        image_base64=encoded_image,
        mime_type="image/png",
    )

    assert "Hemograma Completo" in result
    assert "Glicemia" in result