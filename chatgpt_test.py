#!/usr/bin/env python3
import os
import sys
import traceback
from openai import OpenAI
from dotenv import load_dotenv

MODEL = "gpt-4o"

# This RESULT is a bit odd.  The way it works is when we invoke exec() below,
# we expect the script we're executing to set RESULT as a "local" variable
# (really global to that script).
# But we're essentially exec()ing ourselves! So to return a result to the outer
# instance, we just set the global RESULT.
# So, be sure not to wrap this RESULT in any function.  It must stay global to this script.
# Also, please don't delete this comment.
RESULT = ""

def parse_response(response_message):
    """Parse the response to extract script content."""
    if "```python" in response_message:
        start_index = response_message.find("```python") + len("```python")
        end_index = response_message.rfind("```")
        return response_message[start_index:end_index].strip()
    return response_message.strip()

def get_corrected_script(conversation_history, error_details=''):
    """Requests a corrected script from the API and returns the response."""
    correction_request_content = (
        f"The script has an error. Please correct it and provide the entire script again. "
        f"Error details: {error_details}"
    )
    conversation_history.append({
        "role": "user",
        "content": correction_request_content
    })
    print("\n\n<user>", correction_request_content)
    chat_completion = client.chat.completions.create(
        model=MODEL,
        messages=conversation_history
    )
    correction = chat_completion.choices[0].message.content
    conversation_history.append({
        "role": "assistant",
        "content": correction
    })
    print("\n\n<assistant>", correction)
    return parse_response(correction)

print("Starting")

# Load environment variables from .env file
load_dotenv()

# Check API key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("Error: OPENAI_API_KEY not set in environment")
    sys.exit(1)

# Initialize the OpenAI client
client = OpenAI(api_key=api_key)

# Read the contents of this script
with open(__file__, "r") as file:
    script_content = file.read()

# REQUEST is passed in via exec_globals, so it must stay global.
# This check makes sure we have a request.
if "REQUEST" not in globals():
    print("No globals request, using argv")
    if len(sys.argv) <= 1:
        print("Usage: {} <request>".format(sys.argv[0]))
        sys.exit(1)
    REQUEST = sys.argv[1]
else:
    print("Got request:", REQUEST)

content = f"{REQUEST}:\n\n{script_content}"
print("Request is", REQUEST)

# Initialize conversation history
conversation_history = []
conversation_history.append({
    "role": "user",
    "content": content
})
print("\n\n<user>", content)

# Create a chat completion, echoing the script back
chat_completion = client.chat.completions.create(
    model=MODEL,
    messages=conversation_history
)
response_message = chat_completion.choices[0].message.content
conversation_history.append({
    "role": "assistant",
    "content": response_message
})
print("\n\n<assistant>", response_message)

# Parse the response to extract the script content
RESULT = parse_response(response_message)

# Save result for debugging
with open("output.txt", "w") as f:
    f.write(RESULT + "\n")

if "SKIP_TESTS" not in globals():
    max_attempts = 10
    attempts = 0
    while attempts < max_attempts:
        print("Executing child (attempt {})".format(attempts + 1))
        try:
            exec_globals = {
                "__name__": __name__,
                "__file__": __file__,
                "SKIP_TESTS": True,
                "REQUEST": "Please echo back the following script with no changes"
            }
            exec_locals = {}
            print("EXECUTING:\n", RESULT)
            exec(RESULT, exec_globals, exec_locals)
            # Check that the executed script defined RESULT correctly
            if "RESULT" in exec_locals:
                child_result = exec_locals["RESULT"].strip()
                if child_result == script_content.strip():
                    print("Echo test passed")
                    break  # Exit loop since the test passed
                else:
                    print("Echo test failed! Unexpected changes were detected.")
                    with open("left.txt", "w") as lf:
                        lf.write(child_result)
                    with open("right.txt", "w") as rf:
                        rf.write(script_content)
                    RESULT = get_corrected_script(conversation_history, "Echo test mismatch")
            else:
                print("Error: RESULT not found in executed script.")
                RESULT = get_corrected_script(conversation_history, "No RESULT found in exec")
        except Exception as e:
            print("Execution error:", e)
            traceback.print_exc()
            RESULT = get_corrected_script(conversation_history, str(e))
        attempts += 1
    else:
        print("Maximum correction attempts reached. Exiting.")

