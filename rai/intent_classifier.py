import re

FINANCE_PATTERNS = [
    r"\b(stock|invest|portfolio|bond|etf|fund|market|trading|crypto|bitcoin|forex|dividend|equity)\b",
    r"\b(p/e|eps|rsi|macd|hedge|options|futures|derivative|ipo|sec|fed|earnings)\b",
    r"\b(budget|savings|loan|mortgage|interest rate|inflation|gdp|recession|bull|bear)\b",
    r"\b(financial|finance|economy|economic|wealth|retirement|401k|ira|tax|fiscal|monetary)\b",
]

CODING_PATTERNS = [
    r"\b(code|function|class|bug|error|script|python|javascript|api|database|sql|debug)\b",
    r"\b(algorithm|data structure|array|loop|import|library|framework|deploy|git)\b",
]

GENERAL_PATTERNS = [
    r"\b(explain|what is|how does|summarize|write|help me|create|generate|translate)\b",
]

INTENT_LABELS = {
    "finance": FINANCE_PATTERNS,
    "coding": CODING_PATTERNS,
    "general": GENERAL_PATTERNS,
}


def classify_intent(query: str) -> dict:
    q_lower = query.lower()
    scores = {}
    for label, patterns in INTENT_LABELS.items():
        scores[label] = sum(1 for p in patterns if re.search(p, q_lower))

    best = max(scores, key=scores.get)
    confidence = min(scores[best] / max(len(INTENT_LABELS[best]), 1), 1.0)

    if scores[best] == 0:
        return {"intent": "general", "confidence": 1.0, "scores": scores}

    return {"intent": best, "confidence": round(confidence, 2), "scores": scores}


def is_finance_query(query: str) -> bool:
    result = classify_intent(query)
    return result["intent"] == "finance"