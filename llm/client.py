

from typing import Generator
import os


class LLMClient:
    """Unified LLM client that switches between backends via config."""

    def __init__(self):
        from config.settings import settings
        self.settings = settings
        self.backend = settings.LLM_BACKEND.lower()
        self._client = None
        self._init_client()

    def _init_client(self):
        b = self.backend
        if b == "openai":
            self._init_openai()
        elif b == "groq":
            self._init_groq()
        elif b == "anthropic":
            self._init_anthropic()
        elif b == "ollama":
            pass  # Uses requests directly
        else:
            raise ValueError(
                f"Unknown LLM_BACKEND: '{b}'. "
                f"Choose from: ollama, openai, groq, anthropic"
            )

    def _init_openai(self):
        try:
            import openai
            self._client = openai.OpenAI(
                api_key=self.settings.LLM_API_KEY or os.getenv("OPENAI_API_KEY"),
                base_url=self.settings.LLM_BASE_URL
                if self.settings.LLM_BASE_URL != "http://localhost:11434"
                else None,
            )
        except ImportError:
            raise ImportError("Run: pip install openai")

    def _init_groq(self):
        try:
            from groq import Groq
            self._client = Groq(
                api_key=self.settings.LLM_API_KEY or os.getenv("GROQ_API_KEY")
            )
        except ImportError:
            raise ImportError("Run: pip install groq")

    def _init_anthropic(self):
        try:
            import anthropic
            self._client = anthropic.Anthropic(
                api_key=self.settings.LLM_API_KEY or os.getenv("ANTHROPIC_API_KEY")
            )
        except ImportError:
            raise ImportError("Run: pip install anthropic")



    def complete(self, prompt: str) -> str:
        """Non-streaming completion."""
        if self.backend == "ollama":
            return self._ollama_complete(prompt)
        elif self.backend in ("openai", "groq"):
            return self._openai_complete(prompt)
        elif self.backend == "anthropic":
            return self._anthropic_complete(prompt)

    def stream(self, prompt: str) -> Generator[str, None, None]:
        """Streaming completion — yields token strings."""
        if not self.settings.LLM_STREAM:
            yield self.complete(prompt)
            return

        if self.backend == "ollama":
            yield from self._ollama_stream(prompt)
        elif self.backend in ("openai", "groq"):
            yield from self._openai_stream(prompt)
        elif self.backend == "anthropic":
            yield from self._anthropic_stream(prompt)

   

    def _ollama_complete(self, prompt: str) -> str:
        import requests
        resp = requests.post(
            f"{self.settings.LLM_BASE_URL}/api/generate",
            json={
                "model": self.settings.LLM_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": self.settings.LLM_TEMPERATURE,
                    "num_predict": self.settings.LLM_MAX_TOKENS,
                },
            },
            timeout=120,
        )
        resp.raise_for_status()
        return resp.json().get("response", "")

    def _ollama_stream(self, prompt: str) -> Generator[str, None, None]:
        import requests, json
        with requests.post(
            f"{self.settings.LLM_BASE_URL}/api/generate",
            json={
                "model": self.settings.LLM_MODEL,
                "prompt": prompt,
                "stream": True,
                "options": {
                    "temperature": self.settings.LLM_TEMPERATURE,
                    "num_predict": self.settings.LLM_MAX_TOKENS,
                },
            },
            stream=True,
            timeout=120,
        ) as resp:
            resp.raise_for_status()
            for line in resp.iter_lines():
                if line:
                    data = json.loads(line)
                    token = data.get("response", "")
                    if token:
                        yield token
                    if data.get("done"):
                        break

   

    def _messages_from_prompt(self, prompt: str):
        """Convert our flat prompt string into chat messages."""
        from config.settings import settings
        return [
            {"role": "system", "content": settings.SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]

    def _openai_complete(self, prompt: str) -> str:
        resp = self._client.chat.completions.create(
            model=self.settings.LLM_MODEL,
            messages=self._messages_from_prompt(prompt),
            temperature=self.settings.LLM_TEMPERATURE,
            max_tokens=self.settings.LLM_MAX_TOKENS,
        )
        return resp.choices[0].message.content

    def _openai_stream(self, prompt: str) -> Generator[str, None, None]:
        stream = self._client.chat.completions.create(
            model=self.settings.LLM_MODEL,
            messages=self._messages_from_prompt(prompt),
            temperature=self.settings.LLM_TEMPERATURE,
            max_tokens=self.settings.LLM_MAX_TOKENS,
            stream=True,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta
            if delta and delta.content:
                yield delta.content

  

    def _anthropic_complete(self, prompt: str) -> str:
        from config.settings import settings
        message = self._client.messages.create(
            model=self.settings.LLM_MODEL,
            max_tokens=self.settings.LLM_MAX_TOKENS,
            system=settings.SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text

    def _anthropic_stream(self, prompt: str) -> Generator[str, None, None]:
        from config.settings import settings
        with self._client.messages.stream(
            model=self.settings.LLM_MODEL,
            max_tokens=self.settings.LLM_MAX_TOKENS,
            system=settings.SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        ) as stream:
            for text in stream.text_stream:
                yield text