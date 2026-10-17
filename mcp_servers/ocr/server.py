from google import genai
from mcp.server.mcpserver import MCPServer

from mcp_servers.ocr.service import (
    LLMOCRService,
)

from config.settings import settings_config

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


settings = settings_config()

client = genai.Client()

ocr_service = LLMOCRService(
    client=client,
    model=settings.GEMINI_OCR_MODEL
)

mcp = MCPServer(
    "laboratory-ocr-server",
)


@mcp.tool()
async def extract_medical_request(image_path: str) -> dict[str, str]:
    """
    Extract visible text from a fictitious
    laboratory medical request image.

    """
    logger.info("extract_medical_request: OCR tool called with image: %s", image_path)


    extracted_text = await ocr_service.extract_text(
            image_path=image_path,
        )
    logger.info("extract_medical_request: OCR tool finished processing image: %s", image_path)

    return {
            "extracted_text": extracted_text,
        }
    


if __name__ == "__main__":
    mcp.run(
        transport="sse",
        host="0.0.0.0",
        port=8001,
        sse_path="/sse",
    )