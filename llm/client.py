


from config.settings import (
    LLM_BACKEND, GROQ_API_KEY, GROQ_MODEL,
    OPENAI_API_KEY, OPENAI_MODEL,
    OLLAMA_BASE_URL, OLLAMA_MODEL
)
 
 
def stream_response(messages, system_prompt=""):
    backend = LLM_BACKEND.lower()
    if backend == "groq":
        yield from _stream_groq(messages, system_prompt)
    elif backend == "openai":
        yield from _stream_openai(messages, system_prompt)
    elif backend == "ollama":
        yield from _stream_ollama(messages, system_prompt)
    else:
        yield from _stream_groq(messages, system_prompt)
 
 
def get_response(messages, system_prompt=""):
    full = ""
    for chunk in stream_response(messages, system_prompt):
        full += chunk
    return full
 
 
def _stream_groq(messages, system_prompt):
    try:
        from groq import Groq
        client = Groq(api_key=GROQ_API_KEY)
        all_messages = []
        if system_prompt:
            all_messages.append({"role": "system", "content": system_prompt})
        all_messages.extend(messages)
        stream = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=all_messages,
            max_tokens=1024,
            stream=True
        )
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta
    except Exception as e:
        yield f"\n[Groq error: {e}]\n"
 
 
def _stream_openai(messages, system_prompt):
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        all_messages = []
        if system_prompt:
            all_messages.append({"role": "system", "content": system_prompt})
        all_messages.extend(messages)
        stream = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=all_messages,
            max_tokens=1024,
            stream=True
        )
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta
    except Exception as e:
        yield f"\n[OpenAI error: {e}]\n"
 
 
def _stream_ollama(messages, system_prompt):
    try:
        import requests
        import json
        all_messages = []
        if system_prompt:
            all_messages.append({"role": "system", "content": system_prompt})
        all_messages.extend(messages)
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/chat",
            json={"model": OLLAMA_MODEL, "messages": all_messages, "stream": True},
            stream=True,
            timeout=120
        )
        for line in response.iter_lines():
            if line:
                data = json.loads(line)
                content = data.get("message", {}).get("content", "")
                if content:
                    yield content
                if data.get("done"):
                    break
    except Exception as e:
        yield f"\n[Ollama error: {e}]\n"