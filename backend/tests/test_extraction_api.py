from types import SimpleNamespace

from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.routers import extraction
from backend.app.schemas.extraction import BillExtraction
from backend.app.services.extractor import ExtractionError, MissingGeminiAPIKeyError

client = TestClient(app)
PNG_BYTES = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\xff"
    b"\xff?\x00\x05\xfe\x02\xfe\r\xefF\xb8\x00\x00\x00\x00IEND\xaeB`\x82"
)


def test_extract_success(monkeypatch):
    expected = BillExtraction(items=[])
    monkeypatch.setattr(extraction, "extract_bill_images", lambda images: expected)
    response = client.post(
        "/extract",
        files=[("files", ("bill.png", PNG_BYTES, "image/png"))],
    )
    assert response.status_code == 200
    assert response.json()["items"] == []


def test_extract_requires_files():
    assert client.post("/extract").status_code == 422


def test_extract_rejects_unsupported_type():
    response = client.post(
        "/extract",
        files=[("files", ("bill.txt", b"text", "text/plain"))],
    )
    assert response.status_code == 415


def test_extract_rejects_oversized_file():
    monkeypatch_data = b"x" * (10 * 1024 * 1024 + 1)
    response = client.post(
        "/extract",
        files=[("files", ("bill.jpg", monkeypatch_data, "image/jpeg"))],
    )
    assert response.status_code == 413


def test_extract_handles_gemini_failure(monkeypatch):
    def fail(images):
        raise ExtractionError("Gemini extraction request failed")

    monkeypatch.setattr(extraction, "extract_bill_images", fail)
    response = client.post(
        "/extract",
        files=[("files", ("bill.png", PNG_BYTES, "image/png"))],
    )
    assert response.status_code == 502
    assert response.json()["detail"] == "Gemini extraction failed"


def test_extract_rejects_invalid_image_bytes(monkeypatch):
    monkeypatch.setattr(extraction, "extract_bill_images", lambda images: None)
    response = client.post(
        "/extract",
        files=[("files", ("bill.jpg", b"not-an-image", "image/jpeg"))],
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "invalid image bytes"


def test_extract_missing_api_key_returns_safe_500(monkeypatch):
    def fail(images):
        raise MissingGeminiAPIKeyError("GEMINI_API_KEY is not configured")

    monkeypatch.setattr(extraction, "extract_bill_images", fail)
    response = client.post(
        "/extract",
        files=[("files", ("bill.png", PNG_BYTES, "image/png"))],
    )
    assert response.status_code == 500
    assert response.json()["detail"] == "Gemini API key is not configured"
