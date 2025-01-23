#!/usr/bin/env python3

import os
import sys
from openai import OpenAI
from dotenv import load_dotenv

MODEL = "gpt-4o-mini"

def parse_response(response_message):
    """Parse the response to extract script content."""
    if "```python" in response_message:
        start_index = response_message.find("```python") + len("```python")
        end_index = response_message.rfind("```")
        script_content_clean = response_message[start_index:end_index].strip()
    else:
        script_content_clean = response_message.strip()
    return script_content_clean

def get_corrected_script(conversation_history, assistant_response, error_details=''):
    """Requests a corrected script from the API and returns the response."""
    # Add the assistant's response to the conversation history
    conversation_history.append({
        "role": "assistant",
        "content": assistant_response
    })

    # Create a content for the correction request including the error details
    correction_request_content = (
        f"The script has an error. Please correct it and provide the entire script again. "
        f"Error details: {error_details}"
    )

    # Add the new message to the conversation history
    conversation_history.append({
        "role": "user",
        "content": correction_request_content
    })

    # Create a chat completion, asking for a correction
    chat_completion = client.chat.completions.create(
        model=MODEL,
        messages=conversation_history
    )

    # Extract the response message containing the corrected script
    correction = chat_completion.choices[0].message.content
    return parse_response(correction)

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
except NameError:  # No request
    print("No globals request, using argv")
    if len(sys.argv) <= 1:
        print("Usage: " + sys.argv[0] + " <request>")
        sys.exit(1)
    REQUEST = sys.argv[1]
else:
    print("Got request", REQUEST)

content = (
    f"{REQUEST}:\n\n{script_content}"
)

print("Request is", REQUEST)

# Initialize conversation history
conversation_history = []

# Add initial message to conversation history
conversation_history.append({
    "role": "user",
    "content": content
})

# Create a chat completion, providing the script content and asking to echo it back
chat_completion = client.chat.completions.create(
    model=MODEL,
    messages=conversation_history
)

# Extract the response content
response_message = chat_completion.choices[0].message.content

print("Got response:", response_message)

# Parse the response to extract the initial script content
script_content_clean = parse_response(response_message)

try:
    SKIP_TESTS
except NameError:  # Don't skip tests

    while True:  # Initiate a loop to keep asking for corrections until the script passes the test
        print("Executing child")

        # Execute script_content_clean and capture its result
        exec_globals = {"__file__": __file__, "SKIP_TESTS": True, "REQUEST": "Please echo back the following script with no changes"}
        exec_locals = {}
        try:
            exec(script_content_clean, exec_globals, exec_locals)
            result = exec_locals

            with open("output.txt", "w") as f:
                f.write(script_content_clean)
                f.write("\n")

            if "script_content_clean" in result:
                if result["script_content_clean"].strip() == script_content.strip():
                    print("Echo test passed")
                    break  # Exit the loop since the test passed
                else:
                    print("Echo test failed! Unexpected changes were detected.")
                    with open("left.txt", "w") as f:
                        f.write(result["script_content_clean"])
                    with open("right.txt", "w") as f:
                        f.write(script_content_clean)
                    # Get a corrected script
                    corrected_script = get_corrected_script(conversation_history, response_message, "Echo test mismatch")
                    # Update script_content_clean with the corrected script for the next iteration
                    script_content_clean = corrected_script
            else:
                print("Error: No result found!")
                corrected_script = get_corrected_script(conversation_history, response_message, "No result found in execution")
                script_content_clean = corrected_script
        except Exception as e:
            print("Execution error:", e)
            # Request a corrected script from the API with error details
            corrected_script = get_corrected_script(conversation_history, response_message, str(e))
            # Update script_content_clean with the corrected script for the next iteration
            script_content_clean = corrected_script
