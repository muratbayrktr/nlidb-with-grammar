from typing import List, Optional
from openai import OpenAI
from app.prompts import PromptBuilder
from app.prompts.model import Prompt
from llama_cpp import Llama
from llama_cpp.llama import Llama, LlamaGrammar
from pydantic_gbnf_grammar_generator import generate_gbnf_grammar_and_documentation
from pydantic import BaseModel
import importlib.resources as pkg_resources
from app.constants import SystemPrompts
import os


class InferenceEngine:
    def __init__(self,
        model:str = "gpt-4o-mini", # or hf
        response_format : Optional[BaseModel] = None
    ):
        self.model = model
        self.prompt_type = None
        self.grammar = None
        self.response_format = response_format

        # client probing
        if "gpt" in model:
            self.client = OpenAI()
            self.extra_headers = None
            self.prompt_type = "openai"
        elif "local" in model:
            self.client = Llama(
                model_path=pkg_resources.files("app.models").joinpath(model).as_posix(),
                n_gpu_layers=-1,
                n_ctx=1024
                )
            self.extra_headers = None
            self.prompt_type = "llama"
            grammar_string, documentation = generate_gbnf_grammar_and_documentation([self.response_format])
            self.grammar = LlamaGrammar.from_string(grammar_string)
        # fallback to huggingface
        else:
            self.client = OpenAI(
                base_url="https://api-inference.huggingface.co/v1/",
                api_key=os.getenv("HF_TOKEN")
            )
            self.prompt_type = "hf"
            self.extra_headers = {"X-Wait-For-Model": "true"}

    def generate(self, system_prompt = SystemPrompts.SQL_QUERY_GENERATION, **kwargs):
        prompt : Prompt = PromptBuilder(). \
            set_prompt(system_prompt.value). \
            set_model_temp(0.3). \
            set_messages([]). \
            set_prompt_type(self.prompt_type). \
            set_model_type(self.model). \
            build(**kwargs)
        if self.prompt_type == "llama":
            # Process prompt locally with Llama.cpp
            if self.response_format and self.grammar:
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
            if self.response_format and self.prompt_type == "openai": # @TODO backup HF grammar or response_format
                response = self.client.beta.chat.completions.parse(
                    **prompt, 
                    response_format=self.response_format,
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