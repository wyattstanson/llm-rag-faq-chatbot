from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

texts = [
    "how to invest money",
    "medical advice",
    "hack system",
    "tell joke",
    "what is ai"
]

labels = ["finance", "medical", "malicious", "safe", "safe"]

vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(texts)

model = LogisticRegression()
model.fit(X, labels)

def classify_intent(user_input):
    return model.predict(vectorizer.transform([user_input]))[0]