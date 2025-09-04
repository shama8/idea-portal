from flask import Flask, request, jsonify
from flask_cors import CORS
from embeddings import get_embedding, cosine_similarity
import json
import os
import numpy as np

app = Flask(__name__)

# ✅ CORS setup: allow both local and deployed frontend
CORS(
    app,
    resources={r"/api/*": {"origins": [
        "http://localhost:3000",         # React dev (optional)
        "http://localhost:5500",         # VSCode Live Server
        "http://127.0.0.1:5500",         # Live Server alt
        "https://idea-portal.onrender.com"  # ✅ your actual frontend on Render
    ]}},
    supports_credentials=True,
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type"]
)

IDEAS_FILE = "ideas.json"

# --------------------------------------------
# Helper: Load ideas
# --------------------------------------------
def load_ideas():
    if os.path.exists(IDEAS_FILE):
        try:
            with open(IDEAS_FILE, "r") as f:
                ideas = json.load(f)
                for idea in ideas:
                    idea["embedding"] = np.array(idea["embedding"])
                return ideas
        except json.JSONDecodeError:
            return []
    return []

# --------------------------------------------
# Helper: Save ideas
# --------------------------------------------
def save_ideas(ideas):
    ideas_to_save = []
    for idea in ideas:
        idea_copy = idea.copy()
        idea_copy["embedding"] = idea_copy["embedding"].tolist()
        ideas_to_save.append(idea_copy)
    with open(IDEAS_FILE, "w") as f:
        json.dump(ideas_to_save, f, indent=2)

# --------------------------------------------
# API: Add New Idea
# --------------------------------------------
@app.route('/api/add-idea', methods=['POST'])
def add_idea():
    data = request.get_json()
    title = data.get("title")
    description = data.get("description")
    category = data.get("category", "")
    impact = data.get("impact", "")
    author = data.get("author", "Unknown")

    if not title or not description:
        return jsonify({"error": "Title and description are required"}), 400

    try:
        full_text = f"{title}. {description}"
        embedding = get_embedding(full_text)

        ideas = load_ideas()
        new_id = max([idea.get("id", 0) for idea in ideas] + [0]) + 1

        new_idea = {
            "id": new_id,
            "title": title,
            "description": description,
            "category": category,
            "impact": impact,
            "author": author,
            "embedding": embedding
        }

        ideas.append(new_idea)
        save_ideas(ideas)

        return jsonify({"message": "Idea added successfully", "id": new_id})
    
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

# --------------------------------------------
# API: Find Similar Ideas
# --------------------------------------------
@app.route('/api/similar-ideas', methods=['POST'])
def find_similar():
    data = request.get_json()
    input_text = data.get("text")

    if not input_text:
        return jsonify({"error": "Missing text"}), 400

    try:
        input_embedding = get_embedding(input_text)
        ideas = load_ideas()

        SIMILARITY_THRESHOLD = 0.75

        results = []
        for idea in ideas:
            score = cosine_similarity(input_embedding, idea["embedding"])
            if score >= SIMILARITY_THRESHOLD:
                results.append({
                    "id": idea.get("id"),
                    "text": f"{idea['title']}. {idea['description']}",
                    "similarity": round(score, 3)
                })

        results.sort(key=lambda x: x["similarity"], reverse=True)
        return jsonify({"input": input_text, "matches": results[:3]})

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

# --------------------------------------------
# API: Delete Idea by ID
# --------------------------------------------
@app.route('/api/delete-idea/<int:idea_id>', methods=['DELETE'])
def delete_idea(idea_id):
    ideas = load_ideas()
    filtered_ideas = [idea for idea in ideas if idea.get("id") != idea_id]

    if len(filtered_ideas) == len(ideas):
        return jsonify({"error": "Idea not found"}), 404

    save_ideas(filtered_ideas)
    return jsonify({"message": "Idea deleted successfully"})

# --------------------------------------------
# API: Get All Ideas (without embeddings)
# --------------------------------------------
@app.route('/api/all-ideas', methods=['GET'])
def get_all_ideas():
    ideas = load_ideas()
    ideas_no_embeddings = [
        {k: v for k, v in idea.items() if k != "embedding"} for idea in ideas
    ]
    return jsonify(ideas_no_embeddings)

# --------------------------------------------
# Run the Flask App
# --------------------------------------------
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # default to 5000 locally
    app.run(host='0.0.0.0', port=port, debug=True)
