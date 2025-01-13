from openai import OpenAI

client = OpenAI(
	base_url="https://api-inference.huggingface.co/v1/",
	api_key="hf_xxx"
)

messages = [
	{
		"role": "user",
		"content": "What is the capital of America?"
	}
]

stream = client.chat.completions.create(
    model="Qwen/Qwen2.5-Coder-3B-Instruct", 
	messages=messages, 
	max_tokens=500,
    stream=True,
    extra_headers={
        "X-Wait-For-Model": "true",
        "grammar": """
            root ::= question
            question ::= "Hello World"
"""
        }
)

for chunk in stream:
    print(chunk.choices[0].delta.content, end="")