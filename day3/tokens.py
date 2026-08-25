import os
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
my_api_key=os.getenv("GROQ_API_KEY")

client=Groq(api_key=my_api_key)

prompt1="Hi"
prompt2="Explain time travel in detail"
prompt3="Write an essay on machine learning in 1000 words"

prompts = [prompt1, prompt2, prompt3]

for prompt in prompts:
    completion = client.chat.completions.create(
        model="groq/compound-mini",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        max_tokens=50
    )
    usage = completion.usage
    print(
        f"Prompt: {prompt}\n"
        f"Completion tokens: {usage.completion_tokens}\n"
        f"Prompt tokens: {usage.prompt_tokens}\n"
        f"Total tokens: {usage.total_tokens}\n"
        f"Finish reason: {completion.choices[0].finish_reason}\n"
    )