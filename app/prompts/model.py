from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional, Dict, Any

class ModelChoices(str, Enum):
    GPT4o = "gpt-4o"
    GPTMini = "gpt-4o-mini"
    Qwen_coder_3b = "Qwen/Qwen2.5-Coder-3B-Instruct"

class Message(BaseModel):
    role: str
    content: str

class Prompt(BaseModel):
    model: ModelChoices | str = ModelChoices.GPTMini
    temperature: float = 0.3
    # should default to an empty list
    messages: Optional[list[Message]] = []
    prompt_type: str = "OpenAI"
    response_format: Optional[Dict[str, Any]] = None
    tool_choice: Optional[str | Dict[str, Any]] = None
    tools: Optional[Dict[str, Any]] = None
    prompt: str = "prompt.jinja"