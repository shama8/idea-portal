from flask import Flask, request, jsonify
from flask_cors import CORS
from embeddings import get_embedding, cosine_similarity

app = Flask(__name__)
CORS(app)

# Example existing ideas
existing_ideas = [
    {"id": 1, "text": "Use AI to help with HR onboarding"},
    {"id": 2, "text": "Chatbot for customer support"},
    {"id": 3, "text": "Automate feedback collection"},
]

# Precompute embeddings (once)
for idea in existing_ideas:
    idea["embedding"] = get_embedding(idea["text"])

@app.route('/api/similar-ideas', methods=['POST'])
def find_similar():
    data = request.get_json()
    input_text = data.get("text")

    if not input_text:
        return jsonify({"error": "Missing text"}), 400

    input_embedding = get_embedding(input_text)
    results = []

    for idea in existing_ideas:
        score = cosine_similarity(input_embedding, idea["embedding"])
        results.append({
            "id": idea["id"],
            "text": idea["text"],
            "similarity": round(score, 3)
        })

    # Return top 3 matches
    results.sort(key=lambda x: x["similarity"], reverse=True)
    return jsonify({"input": input_text, "matches": results[:3]})

if __name__ == '__main__':
    app.run()
