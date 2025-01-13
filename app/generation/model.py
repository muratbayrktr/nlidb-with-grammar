from pydantic import BaseModel, Field

class NLQRequest(BaseModel):
    natural_language_query: str = Field(..., title="The natural language query")
    tables: list[str] = Field(..., title="The tables to query")
    columns: list[str] = Field(..., title="The columns to query")
    clarifications: list[str] = Field(..., title="The clarifications to query")
