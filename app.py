import streamlit as st
from rag.retriever import retrieve
from llm.prompt_builder import build_prompt
from llm.client import stream_response
from rai.intent_classifier import classify_intent
from rai.policy_engine import apply_policy
from rai.evaluator import evaluate_response
from memory.chat_memory import init_memory, add_memory

st.title("Local LLM with RAI + RAG")

if "history" not in st.session_state:
    st.session_state.history = init_memory()

user_input = st.chat_input("Enter your query")

if user_input:
    intent = classify_intent(user_input)
    policy = apply_policy(intent)

    if not policy["allow"]:
        st.error(policy["message"])
    else:
        docs = retrieve(user_input)

        prompt = build_prompt(
            user_input,
            docs,
            "You are a safe and helpful assistant."
        )

        response_box = st.empty()
        full_response = ""

        for chunk in stream_response(prompt):
            full_response += chunk
            response_box.markdown(full_response)

        evaluation = evaluate_response(full_response)

        st.markdown("### Evaluation")
        st.write(evaluation)

        if "note" in policy:
            st.info(policy["note"])

        add_memory(st.session_state.history, user_input, full_response)