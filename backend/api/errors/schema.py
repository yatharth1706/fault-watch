from pydantic import BaseModel


class ErrorPayload(BaseModel):
    service: str
    error_type: str | None = None
    message: str
    stack_trace: str | None = None
    error_metadata: dict | None = {}