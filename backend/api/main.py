# backend/api/main.py
from fastapi import FastAPI
from api.errors.controller import router as errors_router

app = FastAPI()

app.include_router(errors_router)

@app.get("/health")
async def health():
    return {"status": "ok"}
