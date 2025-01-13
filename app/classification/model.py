from pydantic import BaseModel


class ClassificationRequest(BaseModel):
    nlq:str