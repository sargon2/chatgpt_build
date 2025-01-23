#!/usr/bin/env python3

import os
import sys
from openai import OpenAI
from dotenv import load_dotenv

print("Starting")

# Load environment variables from .env file
load_dotenv()

# Initialize the OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Read the contents of this script
file_path = __file__
with open(file_path, "r") as file:
    script_content = file.read()

try:
    REQUEST
except NameError: # No request
    REQUEST = sys.argv[1]

content = (
    f"{REQUEST}:\n\n{script_content}"
)

print("Content is", content)

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

print("Got response")

# Extract the response content
response_message = chat_completion.choices[0].message.content

# Parse the response to extract only the script content
if "```python" in response_message:
    start_index = response_message.find("```python") + len("```python")
    end_index = response_message.rfind("```")  # Use rfind to find the last occurrence of ```
    script_content_clean = response_message[start_index:end_index].strip()
else:
    script_content_clean = response_message.strip()

try:
    SKIP_TESTS
except NameError: # Don't skip tests

    print("Executing child")

    # Execute script_content_clean and capture its result
    exec_globals = {"__file__": __file__, "SKIP_TESTS": True, "REQUEST": "Please echo back the following script with no changes"}
    exec_locals = {}
    exec(script_content_clean, exec_globals, exec_locals)
    result = exec_locals


    if result["script_content_clean"] == script_content_clean:
        print("No changes")
    else:
        print("Changes detected!")

