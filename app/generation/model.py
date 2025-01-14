from pydantic import BaseModel, Field, PlainSerializer
from app.prompts.model import ModelChoices

class NLQRequest(BaseModel):
    natural_language_query: str = Field(..., title="The natural language query")
    tables: list[str] = Field(..., title="The tables to query")
    columns: list[str] = Field(..., title="The columns to query")
    clarifications: list[str] = Field(..., title="The clarifications to query")
    model: ModelChoices | str = Field(..., title="Type of model")

class Step(BaseModel):
    """
    Individual steps to generate query.
    """
    explanation: str
    output: str

class ResponseFormat(BaseModel):
    """
    The response format containing the steps and the final answer.
    """
    steps: list[Step]
    final_answer: str
