

import re
from typing import Tuple


# ── Intent definitions ────────────────────────────────────────────────────────

FINANCE_INTENTS = {
    "investing": [
        r"\b(stock|share|equity|etf|fund|portfolio|dividend|bond|invest|asset|return|yield|index)\b",
        r"\b(buy|sell|trade|market|nasdaq|s&p|dow|crypto|bitcoin|nft)\b",
    ],
    "budgeting": [
        r"\b(budget|spend|saving|expense|income|salary|debt|loan|mortgage|credit|emergency fund)\b",
        r"\b(50.30.20|finance plan|personal finance|monthly|annual|cost of living)\b",
    ],
    "risk": [
        r"\b(risk|volatility|drawdown|hedge|diversif|beta|alpha|correlation|standard deviation)\b",
        r"\b(loss|downside|bear market|recession|inflation|deflation|uncertainty)\b",
    ],
    "tax": [
        r"\b(tax|irs|capital gains|deduction|write.off|401k|ira|roth|filing|gst|vat)\b",
    ],
    "economics": [
        r"\b(gdp|inflation|interest rate|fed|central bank|monetary|fiscal|employment|cpi|ppi)\b",
    ],
}

UNSAFE_PATTERNS = {
    "illegal": [
        r"\b(insider trading|pump and dump|money laundering|fraud|ponzi|pyramid scheme|scam)\b",
        r"\b(tax evasion|evade|launder|illegal|illicit)\b",
    ],
    "manipulation": [
        r"\b(manipulat|fake news|spread rumor|short squeeze.*manipulat)\b",
    ],
    "harmful": [
        r"\b(hack|phish|steal|exploit|breach|unauthorized access)\b",
    ],
    "pii_request": [
        r"\b(ssn|social security number|credit card number|bank account number|password|pin)\b",
    ],
}


class IntentClassifier:
    def classify(self, text: str) -> str:
        """
        Returns one of:
          finance intents: investing | budgeting | risk | tax | economics
          safety intents:  illegal | manipulation | harmful | pii_request
          fallback:        general
        """
        text_lower = text.lower()

      
        for intent, patterns in UNSAFE_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    return intent

       
        scores = {}
        for intent, patterns in FINANCE_INTENTS.items():
            hits = sum(
                1 for p in patterns if re.search(p, text_lower)
            )
            if hits:
                scores[intent] = hits

        if scores:
            return max(scores, key=scores.get)

        return "general"

    def is_finance_related(self, text: str) -> bool:
        intent = self.classify(text)
        return intent in FINANCE_INTENTS