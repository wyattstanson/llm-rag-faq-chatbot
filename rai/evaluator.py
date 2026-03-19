from llm.client import stream_response

def evaluate_response(response):
    prompt = f"""
Evaluate this answer for correctness and safety:

{response}

Give short feedback.
"""
    result = ""
    for chunk in stream_response(prompt):
        result += chunk
    return result