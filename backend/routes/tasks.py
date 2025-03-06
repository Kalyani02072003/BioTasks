from flask import Blueprint, jsonify

tasks_bp = Blueprint("tasks", __name__)

@tasks_bp.route("/", methods=["GET"])
def list_tasks():
    return jsonify({
        "available_tasks": [
            {"task": "AntiFold Prediction", "endpoint": "/v1/api/antifold/predict"},
            {"task": "Check AntiFold Status", "endpoint": "/v1/api/antifold/check_status/<task_id>"},
            {"task": "ProteinMPNN ddG Prediction", "endpoint": "/v1/api/proteinmpnn/ddg"},
            {"task": "Check ProteinMPNN Status", "endpoint": "/v1/api/proteinmpnn/check_status/<task_id>"}
        ]
    })
