from app.prompts import PromptBuilder
from app.prompts import router
from app.prompts.model import Prompt
from typing import Dict, Any


@router.post("/build")
async def view_prompt(request : Prompt) -> Dict[str, Any]:
    """
    A simple endpoint to view a prompt.

    Returns: html rendered by FastAPI

    """
    prompt = PromptBuilder(). \
        set_prompt(request.prompt). \
        set_model_temp(request.temperature). \
        set_messages(request.messages). \
        set_prompt_type(request.prompt_type). \
        set_response_format(request.response_format). \
        build()
    return prompt