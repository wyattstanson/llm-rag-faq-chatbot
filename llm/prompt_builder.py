def build_prompt(user_input, context_docs, system_prompt):
    context = "\n\n".join(context_docs)

    return f"""
{system_prompt}

Use only the context below to answer.

Context:
{context}

Question:
{user_input}

Answer:
"""