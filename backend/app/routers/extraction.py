"""Gemini-backed bill extraction endpoint."""

from fastapi import APIRouter, File, HTTPException, UploadFile

from backend.app.services.extractor import (
    MAX_IMAGE_BYTES,
    SUPPORTED_IMAGE_TYPES,
    ExtractionError,
    ImageInput,
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
        images.append(ImageInput(data=data, mime_type=file.content_type))

    try:
        return extract_bill_images(images)
    except ExtractionError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error
