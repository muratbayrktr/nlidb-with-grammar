from pydantic import BaseModel
from app.prompts.model import ModelChoices

class TestRequest(BaseModel):
    question_id: int
    db_id: str
    question: str
    evidence: str
    SQL: str
    difficulty: str
    model: ModelChoices | str = "gpt-4o"