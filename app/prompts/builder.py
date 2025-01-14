from jinja2 import Environment, FileSystemLoader
from app.prompts.model import Prompt, ModelChoices

class PromptBuilder:
    def __init__(self):
        self.prompt = None
        self.tools = None
        self.tool_choice = None
        self.model = "gpt-4o-mini"
        self.model_temp = 0.3
        self.messages = None
        self.prompt_type = None
        self.response_format = None
        self.template_path = "prompt.jinja"

    def set_prompt(self, template_path : str):
        self.template_path = template_path
        return self
    
    def set_tools(self, tools, tool_choice = None):
        self.tools = tools
        self.tool_choice = tool_choice
        return self
    
    def set_model_temp(self, model_temp):
        self.model_temp = model_temp
        return self
    
    def set_messages(self, messages):
        self.messages = messages
        return self
    
    def set_prompt_type(self, prompt_type):
        self.prompt_type = prompt_type
        return self
    
    def set_response_format(self, response_format):
        self.response_format = response_format
        return self
    
    def set_model_type(self, model):
        self.model = model
        return self
    
    def build(self, **kwargs):
        env = Environment(loader=FileSystemLoader('app/prompts'))
        template = env.get_template(self.template_path)

        # Render system prompt with variables
        self.prompt = template.render(**kwargs)

        # Inject system prompt
        self.messages = [{
            "role": "system",
            "content": self.prompt
        }] + self.messages

        # Construct prompt object
        prompt = Prompt(
            model = self.model,
            temperature = self.model_temp,
            messages = self.messages
        )

        if self.tools:
            prompt.tools = self.tools
            if self.tool_choice:
                prompt.tool_choice = self.tool_choice
        


        # Eliminate null and giberrish for OpenAI compatible
        prompt.__delattr__("prompt_type")
        prompt.__delattr__("prompt")
        return prompt.model_dump(mode="json", exclude_none=True)
    

    

    

