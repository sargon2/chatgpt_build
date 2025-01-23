#!/usr/bin/env python3

import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize the OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Read the contents of this script
file_path = __file__
with open(file_path, "r") as file:
    script_content = file.read()

content = (
    f"Please echo the following script back exactly as written:"
    f"\n\n{script_content}"
)

# Create a chat completion, providing the script content and asking to echo it back
chat_completion = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {
            "role": "user",
            "content": content
        }
    ]
)

# Extract the response content
response_message = chat_completion.choices[0].message.content

# Parse the response to extract only the script content
if "```python" in response_message:
    start_index = response_message.find("```python") + len("```python")
    end_index = response_message.rfind("```")  # Use rfind to find the last occurrence of ```
    script_content_clean = response_message[start_index:end_index].strip()
else:
    script_content_clean = response_message.strip()

# Print the new script
print(script_content_clean + "\n", end="")
