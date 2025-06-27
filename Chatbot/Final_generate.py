import json
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Load dataset (relative path)
base_dir = os.path.dirname(__file__)
data_path = os.path.join(base_dir, "cleaned_dataset.json")

with open(data_path, "r", encoding="utf-8") as f:
    dataset = json.load(f)

# Extract questions and answers
questions = []
answers = []

for item in dataset:
    text = item.get("text", "")
    if "<|bot|>" in text and "<|endofbot|>" in text:
        try:
            user_part = text.split("<|bot|>")[0].replace("<|user|>", "").strip()
            bot_part = text.split("<|bot|>")[1].split("<|endofbot|>")[0].strip()
            if user_part and bot_part:
                questions.append(user_part)
                answers.append(bot_part)
        except Exception as e:
            print("Error parsing item:", e)

# TF-IDF setup
vectorizer = TfidfVectorizer().fit(questions)
question_vectors = vectorizer.transform(questions)

# ========== Main Bot Logic ==========

def get_bot_response(user_input, threshold=0.45):
    print("[Chatbot] Received:", user_input)
    """
    Returns best matching answer from dataset using TF-IDF similarity.
    """
    if not user_input.strip():
        return "Please enter something."
    print("[Chatbot] Input:", user_input)    

    vec_input = vectorizer.transform([user_input])
    sims = cosine_similarity(vec_input, question_vectors)[0]
    best_idx = sims.argmax()
    best_score = sims[best_idx]

    print("[Chatbot] Score:", best_score)

    if best_score >= threshold:
        return answers[best_idx]
    else:
        return "Sorry, I am unable to answer this question."
