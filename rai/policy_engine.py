
from config.settings import settings


REFUSAL_MESSAGES = {
    "illegal": (
        "I'm not able to help with that. The query appears to involve potentially "
        "illegal financial activities such as insider trading, fraud, or market "
        "manipulation. These are serious offences with severe legal consequences."
    ),
    "manipulation": (
        "I can't assist with market manipulation tactics. Such activities are "
        "illegal, harmful to other investors, and undermine market integrity."
    ),
    "harmful": (
        "I'm unable to help with that request as it may involve harmful or "
        "illegal activities. Please rephrase if you have a legitimate finance question."
    ),
    "pii_request": (
        "I don't handle sensitive personal or financial identifiers such as "
        "Social Security numbers, credit card numbers, or bank account details. "
        "Never share such information in a chat interface."
    ),
}

DEFAULT_REFUSAL = (
    "I'm not able to assist with that request. "
    "Please ask me about investing, financial literacy, budgeting, or market concepts."
)


class PolicyEngine:
    def check(self, query: str, intent: str) -> tuple:
        """
        Returns (allowed: bool, message: str)
        If allowed=False, message contains refusal text.
        """
        if not settings.ENABLE_RAI:
            return True, ""

        if intent in settings.BLOCKED_INTENTS:
            msg = REFUSAL_MESSAGES.get(intent, DEFAULT_REFUSAL)
            return False, msg

        return True, ""