import os
from flask import Blueprint, request, jsonify
from backend.services.antifold_service import run_antifold

antifold_bp = Blueprint("antifold", __name__)
UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "antifold_output"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@antifold_bp.route("/predict", methods=["POST"])
def predict():
    """Starts AntiFold and returns a task ID."""
    task_type = request.form.get("task_type")
    heavy_chain = request.form.get("heavy_chain")
    light_chain = request.form.get("light_chain")

    # Handle file upload
    pdb_file = request.files.get("pdb_file")
    if not pdb_file:
        return jsonify({"error": "No PDB file uploaded"}), 400

    filepath = os.path.join(UPLOAD_FOLDER, pdb_file.filename)
    pdb_file.save(filepath)  # Save file

    # Prepare data
    data = {
        "task_type": task_type,
        "pdb_file": filepath,
        "heavy_chain": heavy_chain,
        "light_chain": light_chain
    }

    result = run_antifold(data)
    return jsonify(result)

@antifold_bp.route("/check_status/<task_id>", methods=["GET"])
def check_status(task_id):
    """Check if AntiFold has finished running."""
    output_log = os.path.join(OUTPUT_FOLDER, f"{task_id}.log")

    if not os.path.exists(output_log):
        return jsonify({"error": "Task ID not found"}), 404

    with open(output_log, "r") as f:
        logs = f.readlines()

    return jsonify({"task_id": task_id, "logs": logs})
