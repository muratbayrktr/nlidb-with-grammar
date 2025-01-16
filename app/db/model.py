from pydantic import BaseModel
from typing import Any

class DBRequest(BaseModel):
    sql: str

class ErrorModel(BaseModel):
    error: str

class SuccessResponse(BaseModel):
    value: Any