from pydantic import BaseModel

class DBRequest(BaseModel):
    nlq: str