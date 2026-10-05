import base64
import binascii

from google import genai
from google.genai import types
import mimetypes
from pathlib import Path


OCR_PROMPT = """
Extract all visible text from this laboratory medical request.

Rules:
- Perform transcription only.
- Do not summarize.
- Do not interpret medical information.
- Do not correct or normalize the text.
- Do not infer text that is not clearly visible.
- Preserve patient names, numbers and exam names exactly as visible.
- Preserve line breaks whenever possible.
- Return only the extracted text.

""".strip()

class OCRServiceError(Exception):
    """Raised when OCR processing fails."""


class LLMOCRService:

    ALLOWED_MIME_TYPES= {
        "image/jpeg",
        "image/png",
        "image/webp",
    }

    def __init__(self, client: genai.Client, model: str) -> None:

        self.client = client
        self.model = model

    async def extract_text(self,image_path: str) -> str:
        path = Path(image_path)

        if not path.exists():
            raise OCRServiceError(
                f"Image not found: {image_path}"
            )

        mime_type, _ = mimetypes.guess_type(path)

        if mime_type not in self.ALLOWED_MIME_TYPES:
            raise OCRServiceError(
                f"Unsupported image MIME type: {mime_type}"
            )

        image_bytes = path.read_bytes()

        if not image_bytes:
            raise OCRServiceError(
                "Image payload is empty."
            )

        image_part = types.Part.from_bytes(
            data=image_bytes,
            mime_type=mime_type,
        )

        try:
            response = await self.client.aio.models.generate_content(
                model=self.model,
                contents=[
                    OCR_PROMPT,
                    image_part,
                ],
                config=types.GenerateContentConfig(
                    temperature=0,
                ),
            )

        except Exception as exc:
            raise OCRServiceError(
                "Failed to process image using OCR model."
            ) from exc

        extracted_text = response.text

        if not extracted_text:
            raise OCRServiceError(
                "OCR model returned empty text."
            )

        return extracted_text.strip()

