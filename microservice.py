import json
import os
import random
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DATA_PATH = os.path.join(os.path.dirname(__file__), "exercises.json")

with open(DATA_PATH, encoding="utf-8") as f:
    EXERCISES = json.load(f)

EXERCISE_INDEX = {e["id"]: e for e in EXERCISES}


@app.route("/scale", methods=["POST"])
def scale():
    body = request.get_json(silent=True)

    if not body:
        return jsonify({"error": "Request body must be valid JSON."}), 400

    exercise_id = body.get("exercise_id")
    target_difficulty = body.get("target_difficulty", "").strip()

    # Validate exercise_id
    if exercise_id is None:
        return jsonify({"error": "Missing required field: 'exercise_id'."}), 400

    if not isinstance(exercise_id, int):
        return jsonify({"error": "'exercise_id' must be an integer."}), 400

    if exercise_id not in EXERCISE_INDEX:
        return jsonify({"error": f"Exercise with id {exercise_id} not found."}), 404

    # Validate target_difficulty
    if target_difficulty.lower() not in ["beginner", "intermediate", "advanced"]:
        return jsonify({
            "error": "Invalid target_difficulty. Supported values: 'Beginner', 'Intermediate', 'Advanced'."
        }), 400

    original = EXERCISE_INDEX[exercise_id]
    muscle_group = original["muscle_group"]

    # If already at target difficulty, return original
    if original["difficulty"].lower() == target_difficulty.lower():
        return jsonify({
            "original": {
                "id": original["id"],
                "name": original["name"],
                "difficulty": original["difficulty"],
                "muscle_group": original["muscle_group"],
                "reps_sets": original["reps_sets"],
                "equipment": original["equipment"]
            },
            "scaled": None,
            "note": f"Exercise is already at {target_difficulty} difficulty."
        }), 200

    # Find alternatives in same muscle group at target difficulty
    alternatives = [
        e for e in EXERCISES
        if e["muscle_group"] == muscle_group
        and e["difficulty"].lower() == target_difficulty.lower()
        and e["id"] != exercise_id
    ]

    if not alternatives:
        return jsonify({
            "original": {
                "id": original["id"],
                "name": original["name"],
                "difficulty": original["difficulty"],
                "muscle_group": original["muscle_group"],
                "reps_sets": original["reps_sets"],
                "equipment": original["equipment"]
            },
            "scaled": None,
            "note": f"No {target_difficulty} alternative found in the {muscle_group} muscle group."
        }), 200

    result = random.choice(alternatives)

    return jsonify({
        "original": {
            "id": original["id"],
            "name": original["name"],
            "difficulty": original["difficulty"],
            "muscle_group": original["muscle_group"],
            "reps_sets": original["reps_sets"],
            "equipment": original["equipment"]
        },
        "scaled": {
            "id": result["id"],
            "name": result["name"],
            "difficulty": result["difficulty"],
            "muscle_group": result["muscle_group"],
            "reps_sets": result["reps_sets"],
            "equipment": result["equipment"]
        },
        "note": f"Scaled from {original['difficulty']} to {result['difficulty']}."
    }), 200


if __name__ == "__main__":
    print("Workout Difficulty Scaler running on http://localhost:5005")
    app.run(port=5005)
