from typing import List
from openai import OpenAI
from app.prompts import PromptBuilder
from app.prompts.model import Prompt
from llama_cpp import Llama
from llama_cpp.llama import Llama, LlamaGrammar
from pydantic_gbnf_grammar_generator import generate_gbnf_grammar_and_documentation
import importlib.resources as pkg_resources
import os

from app.generation.model import ResponseFormat

class InferenceEngine:
    def __init__(self, 
        natural_language_query: str,
        tables: List[str],
        columns: List[str],
        clarifications: List[str],
        model:str = "gpt-4o-mini", # or hf
        use_response_format: bool = True
    ):
        self.natural_language_query = natural_language_query
        self.tables = tables
        self.columns = columns
        self.clarifications = clarifications
        self.model = model
        self.prompt_type = None
        self.grammar = None
        self.use_response_format = use_response_format

        # client probing
        if "gpt" in model:
            self.client = OpenAI()
            self.extra_headers = None
            self.prompt_type = "openai"
        elif "local" in model:
            self.client = Llama(
                model_path=pkg_resources.files("app.models").joinpath(model).as_posix(),
                n_gpu_layers=-1,
                n_ctx=1024,
                
                )
            self.extra_headers = None
            self.prompt_type = "llama"
            grammar_string, documentation = generate_gbnf_grammar_and_documentation([ResponseFormat])
            self.grammar = LlamaGrammar.from_string(grammar_string)
        # fallback to huggingface
        else:
            self.client = OpenAI(
                base_url="https://api-inference.huggingface.co/v1/",
                api_key=os.getenv("HF_TOKEN")
            )
            self.prompt_type = "hf"
            self.extra_headers = {"X-Wait-For-Model": "true"}

    def generate(self):
        prompt : Prompt = PromptBuilder(). \
            set_prompt("sql_prompt.jinja"). \
            set_model_temp(0.3). \
            set_messages([]). \
            set_prompt_type(self.prompt_type). \
            set_model_type(self.model). \
            build(
                **{
                "nlq": self.natural_language_query,
                "tables": self.tables,
                "columns": self.columns,
                "clarifications": self.clarifications
            }
            )
        if self.prompt_type == "llama":
            # Process prompt locally with Llama.cpp
            if self.use_response_format and self.grammar:
                response = self.client(
                    prompt = prompt["messages"][0]["content"],
                    grammar=self.grammar,
                    max_tokens=1024
                )
            else:
                response = self.client(prompt["messages"][0]["content"], max_tokens=1024)
            return {
                "prompt": prompt,
                "response": response['choices'][0]['text'],
                "grammar": self.grammar
            }
        else:
            # OpenAI or Hugging Face processing
            if self.use_response_format and self.prompt_type == "openai": # @TODO backup HF grammar or response_format
                response = self.client.beta.chat.completions.parse(
                    **prompt, 
                    response_format=ResponseFormat,
                    extra_headers=self.extra_headers
                    ).choices[0].message.parsed
            else:
                response = self.client.chat.completions.create(
                    **prompt, 
                    extra_headers=self.extra_headers
                    ).choices[0].message.content
            return {
                "prompt": prompt,
                "response": response
            }