from typing import List
from openai import OpenAI
from app.prompts import PromptBuilder
from app.prompts.model import Prompt
from pydantic import BaseModel
import os

class Step(BaseModel):
    explanation: str
    output: str

class MathReasoning(BaseModel):
    steps: list[Step]
    final_answer: str

class InferenceEngine:
    def __init__(self, 
        natural_language_query: str,
        tables: List[str],
        columns: List[str],
        clarifications: List[str],
        model:str = "gpt-4o-mini" # or hf
    ):
        self.natural_language_query = natural_language_query
        self.tables = tables
        self.columns = columns
        self.clarifications = clarifications
        self.model = model
        if "gpt-4o" in model:
            self.client = OpenAI()
            self.extra_headers = None
        else:
            self.client = OpenAI(
                base_url="https://api-inference.huggingface.co/v1/",
                api_key=os.getenv("HF_TOKEN")
            )
            self.extra_headers = {"X-Wait-For-Model": "true"}

    def generate(self):
        prompt : Prompt = PromptBuilder(). \
            set_prompt("sql_prompt.jinja"). \
            set_model_temp(0.3). \
            set_messages([]). \
            set_prompt_type("OpenAI"). \
            set_model_type(self.model). \
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
            "response" : self.client.chat.completions.create(**prompt, extra_headers=self.extra_headers).choices[0].message.content
        }