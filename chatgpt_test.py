#!/usr/bin/env python3

import os
import sys
from openai import OpenAI
from dotenv import load_dotenv

def get_corrected_script(conversation_history, error_details=''):
    """Requests a corrected script from the API and returns the response."""
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
        model="gpt-4o-mini",
        messages=conversation_history
    )

    # Extract and return the response message containing the corrected script
    correction = chat_completion.choices[0].message.content
    print("Correction:", correction)
    return correction

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
    model="gpt-4o",
    messages=conversation_history
)

# Extract the response content
response_message = chat_completion.choices[0].message.content

print("Got response:", response_message)

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
                    corrected_script = get_corrected_script(conversation_history, "Echo test mismatch")
                    # Update script_content_clean with the corrected script for the next iteration
                    script_content_clean = corrected_script
            else:
                print("Error: No result found!")
                corrected_script = get_corrected_script(conversation_history, "No result found in execution")
                script_content_clean = corrected_script
        except Exception as e:
            print("Execution error:", e)
            # Request a corrected script from the API with error details
            corrected_script = get_corrected_script(conversation_history, str(e))
            # Update script_content_clean with the corrected script for the next iteration
            script_content_clean = corrected_script
