"""Gemini-backed bill extraction endpoint."""

from fastapi import APIRouter, File, HTTPException, UploadFile

from backend.app.services.extractor import (
    MAX_IMAGE_BYTES,
    SUPPORTED_IMAGE_TYPES,
    ExtractionError,
    ImageInput,
    MissingGeminiAPIKeyError,
    validate_image_bytes,
    extract_bill_images,
)

router = APIRouter()


@router.post("/extract")
async def extract_endpoint(files: list[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=422, detail="at least one bill image is required")

    images: list[ImageInput] = []
    for file in files:
        if file.content_type not in SUPPORTED_IMAGE_TYPES:
            raise HTTPException(status_code=415, detail=f"unsupported image type: {file.content_type}")
        data = await file.read()
        if len(data) > MAX_IMAGE_BYTES:
            raise HTTPException(status_code=413, detail="image exceeds the 10 MB size limit")
        image = ImageInput(data=data, mime_type=file.content_type)
        try:
            validate_image_bytes(image)
        except ExtractionError as error:
            raise HTTPException(status_code=400, detail="invalid image bytes") from error
        images.append(image)

    try:
        return extract_bill_images(images)
    except MissingGeminiAPIKeyError as error:
        raise HTTPException(status_code=500, detail="Gemini API key is not configured") from error
    except ExtractionError as error:
        raise HTTPException(status_code=502, detail="Gemini extraction failed") from error
