from flask import Blueprint, request, jsonify
from backend.models import db, Task
from backend.storage import upload_to_blob
import os
import datetime

tasks_bp = Blueprint("tasks", __name__)

@tasks_bp.route("/", methods=["GET"])
def list_tasks():
    """List all available tasks"""
    return jsonify({
        "available_tasks": [
            {"task": "AntiFold Prediction", "endpoint": "/v1/api/antifold/predict"},
            {"task": "Check AntiFold Status", "endpoint": "/v1/api/antifold/check_status/<task_id>"},
            {"task": "ProteinMPNN ddG Prediction", "endpoint": "/v1/api/proteinmpnn/ddg"},
            {"task": "Check ProteinMPNN Status", "endpoint": "/v1/api/proteinmpnn/check_status/<task_id>"}
        ]
    })

@tasks_bp.route("/run", methods=["POST"])
def run_task():
    """Start a task for a user and upload result to Azure"""
    data = request.json
    user_id = data.get("user_id")
    task_name = data.get("task_name")
    file_path = data.get("file_path")  # Path to the generated output file

    if not user_id or not task_name or not file_path:
        return jsonify({"error": "Missing parameters"}), 400

    # Create a new task entry in the database
    task = Task(user_id=user_id, task_name=task_name, status="running")
    db.session.add(task)
    db.session.commit()

    try:
        # Upload to Azure Blob Storage
        blob_url = upload_to_blob(file_path, f"{user_id}/{task.id}.txt")

        # Update task status to completed
        task.status = "completed"
        task.completed_at = datetime.datetime.utcnow()
        task.output_blob_url = blob_url
        db.session.commit()

        return jsonify({"message": "Task completed", "task_id": task.id, "output_url": blob_url})

    except Exception as e:
        task.status = "failed"
        db.session.commit()
        return jsonify({"error": str(e)}), 500

@tasks_bp.route("/user_tasks/<user_id>", methods=["GET"])
def get_user_tasks(user_id):
    """Get all tasks for a specific user"""
    tasks = Task.query.filter_by(user_id=user_id).all()

    task_list = [
        {
            "task_id": task.id,
            "task_name": task.task_name,
            "status": task.status,
            "output_url": task.output_blob_url
        }
        for task in tasks
    ]

    return jsonify({"user_id": user_id, "tasks": task_list})
