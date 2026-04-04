def evaluate_response(query: str, response: str, sources: list) -> dict:
    issues = []
    score = 100

    if len(response.strip()) < 20:
        issues.append("response_too_short")
        score -= 40

    if "[error" in response.lower() or "error:" in response.lower():
        issues.append("contains_error")
        score -= 30

    if sources and len(response) < 100:
        issues.append("low_rag_utilization")
        score -= 10

    uncertain_phrases = ["i don't know", "i am not sure", "i cannot", "i'm unable"]
    if any(p in response.lower() for p in uncertain_phrases):
        issues.append("uncertain_response")
        score -= 5

    return {
        "score": max(score, 0),
        "issues": issues,
        "passed": score >= 60,
        "rag_used": bool(sources),
        "response_length": len(response),
    }


def should_retry(evaluation: dict) -> bool:
    return not evaluation["passed"] and "contains_error" in evaluation["issues"]