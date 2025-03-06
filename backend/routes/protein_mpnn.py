import os
from flask import Blueprint, request, jsonify
from backend.services.protein_mpnn_service import run_proteinmpnn

proteinmpnn_bp = Blueprint("proteinmpnn", __name__)
UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "proteinmpnn_output"  # Match AntiFold's logging structure
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@proteinmpnn_bp.route("/ddg", methods=["POST"])
def ddg():
    """Starts ProteinMPNN and returns a task ID."""
    pdb_file = request.files.get("pdb_file")
    chain = request.form.get("chain", "A")

    if not pdb_file:
        return jsonify({"error": "No PDB file uploaded"}), 400

    filepath = os.path.join(UPLOAD_FOLDER, pdb_file.filename)
    pdb_file.save(filepath)

    data = {
        "pdb_file": filepath,
        "chain": chain
    }

    result = run_proteinmpnn(data)
    return jsonify(result)

@proteinmpnn_bp.route("/check_status/<task_id>", methods=["GET"])
def check_status(task_id):
    """Check if ProteinMPNN has finished running."""
    output_log = os.path.join(OUTPUT_FOLDER, f"{task_id}.log")

    if not os.path.exists(output_log):
        return jsonify({"error": "Task ID not found"}), 404

    with open(output_log, "r") as f:
        logs = f.readlines()

    return jsonify({"task_id": task_id, "logs": logs})
