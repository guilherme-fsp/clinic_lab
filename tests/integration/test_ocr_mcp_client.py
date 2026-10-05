import pytest
import base64
import mimetypes
from pathlib import Path

from mcp import ClientSession
from mcp.client.sse import sse_client


OCR_MCP_URL = "http://localhost:8001/sse"

IMAGE_PATH = Path(
    "examples/imagem_qualquer.png"
)


def encode_image(
    image_path: Path,
) -> tuple[str, str]:

    if not image_path.exists():
        raise FileNotFoundError(
            f"Image not found: {image_path}"
        )

    mime_type, _ = mimetypes.guess_type(
        image_path
    )

    if mime_type is None:
        raise ValueError(
            "Could not determine MIME type."
        )

    image_bytes = image_path.read_bytes()

    image_base64 = base64.b64encode(
        image_bytes
    ).decode("utf-8")

    return image_base64, mime_type

@pytest.mark.anyio
async def test_ocr_mcp_extracts_text() -> None:

    image_base64, mime_type = encode_image(
        IMAGE_PATH
    )

    async with sse_client(
        OCR_MCP_URL
    ) as streams:

        read_stream, write_stream = streams

        async with ClientSession(
            read_stream,
            write_stream,
        ) as session:

            await session.initialize()

            tools = await session.list_tools()

            assert "extract_medical_request" in {
                tool.name for tool in tools.tools
            }


            result = await session.call_tool(
                "extract_medical_request",
                arguments={
                    "image_base64": image_base64,
                    "mime_type": mime_type,
                },
            )

            assert not result.is_error, (
                f"OCR tool failed {result.content}"
            )

            text_blocks = [
                block.text
                for block in result.content
                if block.type == "text"
            ]

            assert any(
                text.strip() for text in text_blocks
            ), "OCR returned no text."

            print("\nOCR RESULT:\n")
            for text in text_blocks:
                print(text)