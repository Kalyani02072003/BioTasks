from flask import Blueprint, jsonify

tasks_bp = Blueprint("tasks", __name__)

@tasks_bp.route("/", methods=["GET"])
def list_tasks():
    return jsonify({
        "available_tasks": [
            "/v1/api/antifold/predict",
            "/v1/api/proteinmpnn/ddg"
        ]
    })
