
from config.settings import settings


class PromptBuilder:

    def build(
        self,
        query: str,
        history: list,
        context_chunks: list,
        intent: str = "general"
    ) -> str:
        """
        Build a complete prompt string for the LLM.

        For OpenAI/Groq/Anthropic backends, client.py injects the system
        prompt automatically, so here we build the user-facing portion only.
        For Ollama we embed the system prompt inline.
        """
        parts = []

      
        if settings.LLM_BACKEND == "ollama":
            parts.append(f"<|system|>\n{settings.SYSTEM_PROMPT}\n</s>")

      
        if context_chunks:
            ctx = "\n\n---\n\n".join(context_chunks)
            parts.append(
                f"RELEVANT CONTEXT FROM KNOWLEDGE BASE:\n\"\"\"\n{ctx}\n\"\"\"\n"
                "Use this context to inform your answer where relevant. "
                "Cite the context naturally when you use it.\n"
            )
        else:
            parts.append(
                "No specific documents were found for this query. "
                "Answer from your general financial knowledge.\n"
            )

     
        if history:
            parts.append("CONVERSATION HISTORY:")
            for msg in history:
                role = "User" if msg["role"] == "user" else "Assistant"
                parts.append(f"{role}: {msg['content']}")
            parts.append("")  # blank line

        intent_instructions = {
            "investing": (
                "The user is asking about investing. "
                "Be thorough, explain concepts clearly, and always mention risk."
            ),
            "budgeting": (
                "The user is asking about budgeting/personal finance. "
                "Be practical and give actionable frameworks."
            ),
            "risk": (
                "The user is asking about financial risk. "
                "Explain clearly, use examples, and discuss risk management strategies."
            ),
            "tax": (
                "The user is asking about taxes. "
                "Be accurate, note jurisdiction-specific differences, and recommend professionals."
            ),
            "general": "",
        }
        instruction = intent_instructions.get(intent, "")
        if instruction:
            parts.append(f"INSTRUCTION: {instruction}\n")

      
        parts.append(f"User: {query}")
        parts.append("Assistant:")

        return "\n".join(parts)