from types import SimpleNamespace

from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.routers import extraction
from backend.app.schemas.extraction import BillExtraction
from backend.app.services.extractor import ExtractionError

client = TestClient(app)


def test_extract_success(monkeypatch):
    expected = BillExtraction(items=[])
    monkeypatch.setattr(extraction, "extract_bill_images", lambda images: expected)
    response = client.post(
        "/extract",
        files=[("files", ("bill.jpg", b"image", "image/jpeg"))],
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
        files=[("files", ("bill.jpg", b"image", "image/jpeg"))],
    )
    assert response.status_code == 502
    assert response.json()["detail"] == "Gemini extraction request failed"
