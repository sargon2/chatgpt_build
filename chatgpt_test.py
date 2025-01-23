#!/usr/bin/env python3

import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize the OpenAI client
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),  # This is the default and can be omitted
)

# Read the contents of this script
file_path = __file__
with open(file_path, "r") as file:
    script_content = file.read()

# Create a chat completion, providing the script content and asking to echo it back
chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": f"Please echo back the following script content exactly as it is provided:\n\n{script_content}",
        }
    ],
    model="gpt-4o",
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

# Write the cleaned script content to a new file
new_file_path = "echoed_script.py"
with open(new_file_path, "w") as new_file:
    new_file.write(script_content_clean)
    new_file.write("\n")

print(f"The script has been echoed back and written to {new_file_path}")
