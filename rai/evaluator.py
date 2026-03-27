

import re


class ResponseEvaluator:
    """Light-weight heuristic evaluator for response quality."""

    def evaluate(self, response: str, query: str) -> dict:
        issues = []
        score = 1.0

        if len(response.strip()) < 20:
            issues.append("response_too_short")
            score -= 0.4

        if re.search(r"\b(definitely|guaranteed|certain to|will definitely)\b",
                     response, re.IGNORECASE):
            issues.append("overconfident_financial_claim")
            score -= 0.2

        if re.search(r"\b(buy this|buy now|sell now|invest in .{1,30} immediately)\b",
                     response, re.IGNORECASE):
            issues.append("direct_investment_advice")
            score -= 0.3

        return {
            "score": max(0.0, score),
            "issues": issues,
            "passed": score >= 0.5,
        }