import requests
import json
from config.settings import settings

def stream_response(prompt):
    response = requests.post(
        f"{settings.OLLAMA_URL}/api/generate",
        json={
            "model": settings.MODEL_NAME,
            "prompt": prompt,
            "stream": True,
            "options": {
                "temperature": settings.TEMPERATURE,
                "num_predict": settings.MAX_TOKENS
            }
        },
        stream=True
    )

    for line in response.iter_lines():
        if line:
            data = json.loads(line.decode("utf-8"))
            yield data.get("response", "")