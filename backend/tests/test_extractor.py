from types import SimpleNamespace

import pytest

from backend.app.schemas.extraction import BillExtraction
from backend.app.services.extractor import (
    ExtractionError,
    GeminiExtractor,
    ImageInput,
    MissingGeminiAPIKeyError,
)

PNG_BYTES = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\xff"
    b"\xff?\x00\x05\xfe\x02\xfe\r\xefF\xb8\x00\x00\x00\x00IEND\xaeB`\x82"
)


def extracted_bill() -> BillExtraction:
    return BillExtraction.model_validate(
        {
            "restaurant_name": "Cafe",
            "currency": "INR",
            "items": [
                {
                    "id": "meal",
                    "name": "Meal",
                    "quantity": 2,
                    "unit_price": {"value": 5000, "confidence": 0.98},
                    "total_price": {"value": 10000, "confidence": 0.97},
                    "confidence": 0.96,
                }
            ],
            "subtotal": {"value": 10000, "confidence": 0.95},
            "taxes": [
                {"value": 500, "confidence": 0.9},
                {"value": 250, "confidence": 0.8},
            ],
            "printed_total": {"value": 10750, "confidence": 0.99},
        }
    )


class FakeModels:
    def __init__(self, parsed):
        self.parsed = parsed
        self.calls = []

    def generate_content(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(parsed=self.parsed)


def test_successful_extraction_sends_multiple_images():
    models = FakeModels(extracted_bill())
    extractor = GeminiExtractor(client=SimpleNamespace(models=models), api_key="test")
    result = extractor.extract(
        [ImageInput(PNG_BYTES, "image/png"), ImageInput(PNG_BYTES, "image/png")]
    )
    assert result.items[0].total_price.value == 10000
    assert len(result.taxes) == 2
    assert len(models.calls[0]["contents"]) == 3
    config = models.calls[0]["config"]
    assert config.response_mime_type == "application/json"
    assert config.response_schema is BillExtraction


def test_optional_fields_can_be_missing():
    model = BillExtraction(items=[])
    models = FakeModels(model)
    result = GeminiExtractor(client=SimpleNamespace(models=models)).extract(
        [ImageInput(PNG_BYTES, "image/png")]
    )
    assert result.discount is None
    assert result.printed_total is None


def test_confidence_values_are_preserved():
    result = extracted_bill()
    assert result.items[0].confidence == 0.96
    assert result.items[0].unit_price.confidence == 0.98


def test_malformed_model_output_raises():
    models = FakeModels({"items": [{"bad": "output"}]})
    with pytest.raises(ExtractionError, match="invalid structured extraction"):
        GeminiExtractor(client=SimpleNamespace(models=models)).extract(
            [ImageInput(PNG_BYTES, "image/png")]
        )


def test_gemini_failure_is_wrapped():
    class FailingModels:
        def generate_content(self, **kwargs):
            raise RuntimeError("provider failure")

    with pytest.raises(ExtractionError, match="request failed"):
        GeminiExtractor(client=SimpleNamespace(models=FailingModels())).extract(
            [ImageInput(PNG_BYTES, "image/png")]
        )


def test_missing_api_key_is_reported(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    with pytest.raises(MissingGeminiAPIKeyError, match="GEMINI_API_KEY is not configured"):
        GeminiExtractor().extract([ImageInput(PNG_BYTES, "image/png")])
