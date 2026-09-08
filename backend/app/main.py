"""FastAPI application entry point."""

from fastapi import FastAPI

from backend.app.routers.bill import router as bill_router

app = FastAPI(title="BillSplit API")
app.include_router(bill_router)
