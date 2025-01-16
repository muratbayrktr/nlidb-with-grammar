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
    final_query: str


class SQLSubquery(BaseModel):
    """
    A (potential) subquery needed in the final SQL, if any.
    Keep these short and labeled for clarity.
    """
    label: str               # e.g. "SubQuery for filtering recent rows"
    query: str               # The subquery itself

class SQLCandidate(BaseModel):
    """
    Each candidate SQL solution your model might consider.
    """
    rationale: str           # Quick reason why the candidate might work
    query: str               # Candidate SQL (possibly incomplete)

class SQLReflection(BaseModel):
    """
    Short self-reflection on the correctness or rationale for picking the final query.
    """
    notes: str               # e.g. "Candidate #2 gave the correct join logic"

class SQLGenerationResult(BaseModel):
    """
    The entire structure capturing how the final SQL statement came to be.
    """
    subqueries: SQLSubquery            # If your model uses subqueries, list them
    candidates: SQLCandidate           # Potential SQL statements your model considers
    reflection: Optional[SQLReflection]      # Brief, final self-analysis (optional but helpful)
    final_query: str                         # A single syntactically valid SQL statement


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