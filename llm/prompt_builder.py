
def build_messages(conversation_history, user_query, context=None):
    messages = list(conversation_history)

    if context:
        user_content = f"""Use the following context to answer the question. If the context does not contain relevant information, use your general knowledge.

Context:
{context}

Question: {user_query}"""
    else:
        user_content = user_query

    messages.append({"role": "user", "content": user_content})
    return messages