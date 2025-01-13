from typing import List
from openai import OpenAI
from app.prompts import PromptBuilder
from app.prompts.model import Prompt

class InferenceEngine:
    def __init__(self, 
        natural_language_query: str,
        tables: List[str],
        columns: List[str],
        clarifications: List[str],
    ):
        self.natural_language_query = natural_language_query
        self.tables = tables
        self.columns = columns
        self.clarifications = clarifications
        self.client = OpenAI()

    def generate(self):
        prompt : Prompt = PromptBuilder(). \
            set_prompt("sql_prompt.jinja"). \
            set_model_temp(0.3). \
            set_messages([]). \
            set_prompt_type("OpenAI"). \
            set_response_format(None). \
            build(
                **{
                "nlq": self.natural_language_query,
                "tables": self.tables,
                "columns": self.columns,
                "clarifications": self.clarifications
            }
            )
        return {
            "prompt": prompt,
            "response" : self.client.chat.completions.create(**prompt).choices[0].message.content
        }