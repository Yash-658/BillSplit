"""Gemini vision extraction for reviewed bill input."""

import os
from dataclasses import dataclass
from typing import Any, Sequence

from backend.app.schemas.extraction import BillExtraction

SUPPORTED_IMAGE_TYPES = frozenset({"image/jpeg", "image/png", "image/webp"})
MAX_IMAGE_BYTES = 10 * 1024 * 1024

EXTRACTION_INSTRUCTIONS = """
Extract only information visibly present on the bill. Do not invent missing
values and do not silently correct arithmetic. Preserve the printed total
exactly as visible even if it appears wrong; deterministic validation will
detect inconsistencies. Handle poor lighting, perspective or steep angles,
faded thermal printing, crumpled bills, handwriting, and multiple scripts or
languages. Multiple images may be pages or different views of the same bill.
If a value cannot be determined reliably, return null and lower confidence.
Return confidence independently for every extracted field. Each confidence
must describe confidence in that specific field's transcription or extraction,
not confidence in the bill or a related field. Do not invent confidence
values independently of an extracted value.
Preserve actual printed item names and amounts. Return all money values as
integer paise/cents, not floating-point amounts. Do not calculate people's
shares, decide who owes what, or perform final bill arithmetic. Extract a
visible bill-level adjustment or round-off amount when present, preserving its
sign. Return null when no adjustment is visible; do not invent an adjustment
or use one to silently correct another extracted value. Human review will
verify or edit this field.
"""


class ExtractionError(Exception):
    """Safe, user-facing extraction failure."""


class MissingGeminiAPIKeyError(ExtractionError):
    """Raised when extraction is requested without configured credentials."""


@dataclass(frozen=True)
class ImageInput:
    data: bytes
    mime_type: str


def validate_image_bytes(image: ImageInput) -> None:
    """Verify the bytes contain an image of the declared supported type."""

    try:
        from PIL import Image
        from io import BytesIO

        with Image.open(BytesIO(image.data)) as opened:
            opened.verify()
            if opened.format not in {"JPEG", "PNG", "WEBP"}:
                raise ValueError
    except Exception as error:
        raise ExtractionError("invalid image bytes") from error


class GeminiExtractor:
    """Thin adapter around the official Google GenAI SDK."""

    def __init__(self, client: Any = None, api_key: str | None = None, model: str | None = None):
        self._client = client
        self._api_key = api_key
        self._model = model or os.getenv("GEMINI_VISION_MODEL", "gemini-2.5-flash-lite")

    def _get_client(self) -> Any:
        if self._client is not None:
            return self._client
        api_key = self._api_key or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise MissingGeminiAPIKeyError("GEMINI_API_KEY is not configured")
        try:
            from google import genai
            self._client = genai.Client(api_key=api_key)
        except ImportError as error:
            raise ExtractionError("Gemini SDK is not installed") from error
        return self._client

    def extract(self, images: Sequence[ImageInput]) -> BillExtraction:
        if not images:
            raise ExtractionError("at least one bill image is required")
        if any(image.mime_type not in SUPPORTED_IMAGE_TYPES for image in images):
            raise ExtractionError("unsupported image type")
        if any(len(image.data) > MAX_IMAGE_BYTES for image in images):
            raise ExtractionError("image exceeds the 10 MB size limit")
        for image in images:
            validate_image_bytes(image)

        try:
            from google.genai import types
            contents = [EXTRACTION_INSTRUCTIONS]
            contents.extend(
                types.Part.from_bytes(data=image.data, mime_type=image.mime_type)
                for image in images
            )
            response = self._get_client().models.generate_content(
                model=self._model,
                contents=contents,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=BillExtraction,
                ),
            )
        except ExtractionError:
            raise
        except Exception as error:
            raise ExtractionError("Gemini extraction request failed") from error

        parsed = getattr(response, "parsed", None)
        if parsed is None:
            raise ExtractionError("Gemini returned invalid structured extraction")
        try:
            return parsed if isinstance(parsed, BillExtraction) else BillExtraction.model_validate(parsed)
        except Exception as error:
            raise ExtractionError("Gemini returned invalid structured extraction") from error


def extract_bill_images(images: Sequence[ImageInput]) -> BillExtraction:
    return GeminiExtractor().extract(images)
