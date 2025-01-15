from enum import Enum

class SystemPrompts(Enum):
    SQL_QUERY_GENERATION = "sql_prompt.jinja"
    EXTRACT_TABLES = "extract_tables_prompt.jinja"
    EXTRACT_COLUMNS = "extract_columns_prompt.jinja"

