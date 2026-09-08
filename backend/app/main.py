"""FastAPI application entry point."""

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.routers.bill import router as bill_router
from backend.app.routers.extraction import router as extraction_router

frontend_origin = os.getenv("FRONTEND_ORIGIN", "").strip()
allowed_origins = ["http://localhost:5173"]
if frontend_origin and frontend_origin not in allowed_origins:
    allowed_origins.append(frontend_origin)

app = FastAPI(title="BillSplit API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(bill_router)
app.include_router(extraction_router)
