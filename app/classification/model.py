from pydantic import BaseModel
from typing import Literal

class ClassificationRequest(BaseModel):
    nlq: str
    classification_type: Literal["db", "table", "column"]
