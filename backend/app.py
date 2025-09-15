from flask import Flask, request, jsonify
from functools import wraps
from flask_cors import CORS
from datetime import datetime
from flask import make_response
from embeddings import get_embedding, cosine_similarity 
import json
import os
import numpy as np

app = Flask(__name__)

SUPERADMIN_USERNAME = os.environ.get("SUPERADMIN_USERNAME", "Shama08")

def superadmin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        data = request.get_json(silent=True) or {}
        username = data.get("username") or request.args.get("username")
        if username != SUPERADMIN_USERNAME:
            return jsonify({"error": "Unauthorized. Superadmin access only."}), 401
        return f(*args, **kwargs)
    return decorated

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

if not os.path.exists(IDEAS_FILE):
    with open(IDEAS_FILE, "w") as f:
        f.write("[]")

def load_ideas(include_embeddings=True):
    if os.path.exists(IDEAS_FILE):
        try:
            with open(IDEAS_FILE, "r") as f:
                ideas = json.load(f)
                if include_embeddings:
                    for idea in ideas:
                        try:
                            if "embedding" in idea and idea["embedding"] is not None:
                                idea["embedding"] = np.array(idea["embedding"])
                            else:
                                idea["embedding"] = None
                        except Exception:
                            idea["embedding"] = None
                return ideas
        except json.JSONDecodeError:
            return []
    return []

def save_ideas(ideas):
    ideas_to_save = []
    for idea in ideas:
        idea_copy = idea.copy()
        if "embedding" in idea_copy and idea_copy["embedding"] is not None:
            idea_copy["embedding"] = idea_copy["embedding"].tolist()
        ideas_to_save.append(idea_copy)
    with open(IDEAS_FILE, "w") as f:
        json.dump(ideas_to_save, f, indent=2)

@app.route('/api/add-idea', methods=['POST'])
def add_idea():
    data = request.get_json()
    title = data.get("title")
    description = data.get("description")
    category = data.get("category", "")
    impact = data.get("impact", "")
    author = data.get("author", "Unknown")
    force = data.get("force", False)

    if not title or not description:
        return jsonify({"error": "Title and description are required"}), 400

    try:
        input_text = f"{title}. {description}"
        embedding = get_embedding(input_text)

        if not force:
            # Check for similar ideas first
            ideas = load_ideas()
            SIMILARITY_THRESHOLD = 0.75
            matches = []

            for idea in ideas:
                if idea.get("embedding") is None:
                    continue
                score = cosine_similarity(embedding, idea["embedding"])
                if score >= SIMILARITY_THRESHOLD:
                    matches.append({
                        "id": idea["id"],
                        "title": idea["title"],
                        "description": idea["description"],
                        "similarity score": round(score, 3)
                    })

            if matches:
                matches.sort(key=lambda x: x["similarity score"], reverse=True)
                return jsonify({
                    "warning": "Similar idea(s) found",
                    "matches": matches[:3]  # Show top 3 matches
                }), 409  # Conflict

        ideas = load_ideas()
        new_id = max([idea.get("id", 0) for idea in ideas] + [0]) + 1

        new_idea = {
            "id": new_id,
            "title": title,
            "description": description,
            "category": category,
            "impact": impact,
            "author": author,
            "date_submitted": datetime.utcnow().isoformat() + "Z",
            "embedding": embedding
        }

        ideas.append(new_idea)
        save_ideas(ideas)

        return jsonify({"message": "Idea added successfully", "id": new_id})

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route('/api/similar-ideas', methods=['POST'])
def find_similar():
    data = request.get_json()
    title = data.get("title")
    description = data.get("description")

    if not title or not description:
        return jsonify({"error": "Title and description are required"}), 400

    try:
        input_text = f"{title}. {description}"
        input_embedding = get_embedding(input_text)
        ideas = load_ideas()

        SIMILARITY_THRESHOLD = 0.75
        results = []

        for idea in ideas:
            if idea.get("embedding") is None:
                continue
            score = cosine_similarity(input_embedding, idea["embedding"])
            if score >= SIMILARITY_THRESHOLD:
                results.append({
                    "id": idea.get("id"),
                    "title": idea.get("title"),
                    "description": idea.get("description"),
                    "similarity score": round(score, 3)
                })

        results.sort(key=lambda x: x["similarity score"], reverse=True)
        return jsonify({"matches": results[:3]})  # Return top 3 matches

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route('/api/delete-idea/<int:idea_id>', methods=['DELETE'])
@superadmin_required
def delete_idea(idea_id):
    ideas = load_ideas()
    filtered_ideas = [idea for idea in ideas if idea.get("id") != idea_id]

    if len(filtered_ideas) == len(ideas):
        return jsonify({"error": "Idea not found"}), 404

    save_ideas(filtered_ideas)
    return jsonify({"message": "Idea deleted successfully"})

@app.route('/api/all-ideas', methods=['GET'])
def get_all_ideas():
    try:
        ideas = load_ideas(include_embeddings=False)
        ideas_no_embeddings = [
            {k: v for k, v in idea.items() if k != "embedding"} for idea in ideas
        ]
        response = make_response(jsonify(ideas_no_embeddings))
        # Prevent caching to ensure fresh data on each request
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        return response
    except Exception as e:
        app.logger.exception("Error in /api/all-ideas")
        return jsonify({"error": "Internal Server Error"}), 500
@app.route('/api/clear-ideas', methods=['POST'])
def clear_ideas():
    save_ideas([])
    return jsonify({"message": "Ideas cleared"})



if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)