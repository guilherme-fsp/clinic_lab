from google import genai
from mcp.server.mcpserver import MCPServer

from mcp_servers.ocr.service import (
    LLMOCRService,
)

from config.settings import settings_config

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
    print(
        f">>> OCR TOOL CALLED: {image_path}"
    )

    extracted_text = await ocr_service.extract_text(
            image_path=image_path,
        )

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