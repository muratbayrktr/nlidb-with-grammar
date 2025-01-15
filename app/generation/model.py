from typing import Optional
from pydantic import BaseModel, Field
from app.prompts.model import ModelChoices

class NLQRequest(BaseModel):
    natural_language_query: str = Field(..., title="The natural language query")
    clarifications: list[str] = Field(..., title="The clarifications to query")
    model: ModelChoices | str = Field(..., title="Type of model")

class Step(BaseModel):
    """
    Individual steps to generate query.
    """
    explanation: str
    output: str

class InferenceResponseFormat(BaseModel):
    """
    The response format containing the steps and the final answer.
    """
    steps: list[Step]
    final_answer: str

class ExtractTables(BaseModel):
    """
    The response format for extracting the table names as list of strings.
    """
    table_names: list[str]

class ExtractColumns(BaseModel):
    """
    The response format for extracting the column names as list of strings.
    """
    column_names: list[str]