import re

BLOCKED_PATTERNS = [
    r"\b(hack|exploit|crack|bypass security|ddos|malware|phishing)\b",
    r"\b(how to make.*bomb|weapon|poison|drug synthesis)\b",
    r"\b(suicide|self.harm|kill myself)\b",
    r"\b(child.*(abuse|exploit|porn))\b",
]

INJECTION_KEYWORDS = [
    "ignore previous", "jailbreak", "pretend you are", "act as dan",
    "developer mode", "override instructions", "bypass safety",
]


def is_safe(query: str) -> tuple:
    q_lower = query.lower()

    for pattern in BLOCKED_PATTERNS:
        if re.search(pattern, q_lower):
            return False, "harmful_content"

    for kw in INJECTION_KEYWORDS:
        if kw in q_lower:
            return False, "prompt_injection"

    return True, ""


def get_refusal_message(reason: str) -> str:
    messages = {
        "harmful_content": "I am not able to help with that request as it may involve harmful content.",
        "prompt_injection": "I detected an attempt to override my instructions. I will continue operating normally.",
    }
    return messages.get(reason, "I cannot assist with that request.")


def add_finance_disclaimer(response: str) -> str:
    disclaimer = "\n\n---\n⚠️ *Educational content only — not financial advice. Consult a qualified financial advisor before making investment decisions.*"
    if "⚠️" not in response and "Disclaimer" not in response:
        return response + disclaimer
    return response