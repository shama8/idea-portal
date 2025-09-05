from flask import Flask, request, jsonify
from flask_cors import CORS
# from embeddings import get_embedding, cosine_similarity  # 🔒 Temporarily disabled
import json
import os
import numpy as np

app = Flask(__name__)

CORS(
    app,
    resources={r"/api/*": {"origins": [
        "http://localhost:3000",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "https://idea-portal.onrender.com"
    ]}},
    supports_credentials=True,
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type"]
)

IDEAS_FILE = "ideas.json"

# ✅ Ensure ideas.json exists
if not os.path.exists(IDEAS_FILE):
    with open(IDEAS_FILE, "w") as f:
        f.write("[]")

# --------------------------------------------
# Helper: Load ideas
# --------------------------------------------
def load_ideas():
    if os.path.exists(IDEAS_FILE):
        try:
            with open(IDEAS_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    return []

# --------------------------------------------
# Helper: Save ideas
# --------------------------------------------
def save_ideas(ideas):
    with open(IDEAS_FILE, "w") as f:
        json.dump(ideas, f, indent=2)

# --------------------------------------------
# API: Add New Idea (no embeddings)
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
        # full_text = f"{title}. {description}"
        # embedding = get_embedding(full_text)  # 🔒 Disabled

        ideas = load_ideas()
        new_id = max([idea.get("id", 0) for idea in ideas] + [0]) + 1

        new_idea = {
            "id": new_id,
            "title": title,
            "description": description,
            "category": category,
            "impact": impact,
            "author": author,
            # "embedding": embedding  # 🔒 Removed
        }

        ideas.append(new_idea)
        save_ideas(ideas)

        return jsonify({"message": "Idea added successfully", "id": new_id})
    
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

# --------------------------------------------
# API: Find Similar Ideas — disabled to save memory
# --------------------------------------------
# @app.route('/api/similar-ideas', methods=['POST'])
# def find_similar():
#     return jsonify({"error": "Similarity feature is temporarily disabled"}), 503

# --------------------------------------------
# API: Delete Idea by ID — disabled to simplify deploy
# --------------------------------------------
# @app.route('/api/delete-idea/<int:idea_id>', methods=['DELETE'])
# def delete_idea(idea_id):
#     ideas = load_ideas()
#     filtered_ideas = [idea for idea in ideas if idea.get("id") != idea_id]

#     if len(filtered_ideas) == len(ideas):
#         return jsonify({"error": "Idea not found"}), 404

#     save_ideas(filtered_ideas)
#     return jsonify({"message": "Idea deleted successfully"})

# --------------------------------------------
# API: Get All Ideas (no embeddings)
# --------------------------------------------
@app.route('/api/all-ideas', methods=['GET'])
def get_all_ideas():
    try:
        ideas = load_ideas()
        for idea in ideas:
            idea.pop("embedding", None)  # Safe: remove if exists
        return jsonify(ideas)
    except Exception as e:
        app.logger.exception("Error in /api/all-ideas")
        return jsonify({"error": "Internal Server Error"}), 500

# --------------------------------------------
# Run App
# --------------------------------------------
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
