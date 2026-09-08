"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.routers.bill import router as bill_router
from backend.app.routers.extraction import router as extraction_router

app = FastAPI(title="BillSplit API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(bill_router)
app.include_router(extraction_router)
