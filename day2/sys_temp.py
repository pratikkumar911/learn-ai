import os
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
my_api_key=os.getenv("GROQ_API_KEY")

client=Groq(api_key=my_api_key)

completion = client.chat.completions.create(
    model="groq/compound-mini",
    messages=[
        {
            "role": "system",
            "content": "you are my mother"
        },
        {
            "role": "user",
            "content": "i love your cooking"
        }
    ],
    temperature=1
)
print(completion.choices[0].message.content)
