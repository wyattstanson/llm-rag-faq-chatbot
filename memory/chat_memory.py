def init_memory():
    return []

def add_memory(history, user, assistant):
    history.append({
        "user": user,
        "assistant": assistant
    })