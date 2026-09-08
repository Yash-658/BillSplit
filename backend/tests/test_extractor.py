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
            "restaurant_name": {"value": "Cafe", "confidence": 0.91},
            "currency": {"value": "INR", "confidence": 0.92},
            "items": [
                {
                    "id": "meal",
                    "name": {"value": "Meal", "confidence": 0.93},
                    "quantity": {"value": 2, "confidence": 0.94},
                    "unit_price": {"value": 5000, "confidence": 0.98},
                    "total_price": {"value": 10000, "confidence": 0.97},
                    "confidence": 0.96,
                }
            ],
            "subtotal": {"value": 10000, "confidence": 0.95},
            "discount": {"value": 100, "confidence": 0.86},
            "service_charge": {"value": 200, "confidence": 0.87},
            "taxes": [
                {"value": 500, "confidence": 0.9},
                {"value": 250, "confidence": 0.8},
            ],
            "adjustment": {"value": -1, "confidence": 0.78},
            "printed_total": {"value": 10949, "confidence": 0.99},
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
    assert result.restaurant_name is None
    assert result.currency is None
    assert result.adjustment is None
    assert result.printed_total is None


def test_nullable_item_fields_preserve_null_values_and_confidence():
    result = BillExtraction.model_validate(
        {
            "items": [
                {
                    "id": None,
                    "name": {"value": None, "confidence": 0.2},
                    "quantity": {"value": None, "confidence": 0.3},
                    "unit_price": {"value": None, "confidence": 0.4},
                    "total_price": {"value": None, "confidence": 0.5},
                    "confidence": 0.2,
                }
            ]
        }
    )
    item = result.items[0]
    assert item.name.value is None
    assert item.quantity.value is None
    assert item.unit_price.value is None
    assert item.total_price.value is None
    assert item.name.confidence == 0.2
    assert item.quantity.confidence == 0.3


def test_positive_adjustment_is_preserved():
    result = BillExtraction(
        items=[],
        adjustment={"value": 76, "confidence": 0.88},
    )
    assert result.adjustment.value == 76
    assert result.adjustment.confidence == 0.88


def test_negative_adjustment_is_preserved():
    result = BillExtraction(
        items=[],
        adjustment={"value": -11, "confidence": 0.89},
    )
    assert result.adjustment.value == -11
    assert result.adjustment.confidence == 0.89


def test_confidence_values_are_preserved():
    result = extracted_bill()
    assert result.restaurant_name.confidence == 0.91
    assert result.currency.confidence == 0.92
    assert result.items[0].name.confidence == 0.93
    assert result.items[0].quantity.confidence == 0.94
    assert result.items[0].confidence == 0.96
    assert result.items[0].unit_price.confidence == 0.98
    assert result.items[0].total_price.confidence == 0.97
    assert result.subtotal.confidence == 0.95
    assert result.discount.confidence == 0.86
    assert result.service_charge.confidence == 0.87
    assert [tax.confidence for tax in result.taxes] == [0.9, 0.8]
    assert result.adjustment.confidence == 0.78
    assert result.printed_total.confidence == 0.99


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
