def apply_policy(intent):
    if intent == "malicious":
        return {"allow": False, "message": "Request blocked."}

    if intent == "medical":
        return {"allow": True, "note": "This is not medical advice."}

    if intent == "finance":
        return {"allow": True, "note": "This is not financial advice."}

    return {"allow": True}