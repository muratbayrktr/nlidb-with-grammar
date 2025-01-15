from pydantic import BaseModel
from typing import Literal, Optional

class DBClassificationRequest(BaseModel):
    nlq: str
    
class TableClassificationRequest(BaseModel):
    nlq: str
    db: Optional[str] = None

class ColumnsClassificationRequest(BaseModel):
    nlq: str
    db: Optional[str] = None
    tables: Optional[list[str]]

class AllClassificationRequest(BaseModel):
    nlq: str