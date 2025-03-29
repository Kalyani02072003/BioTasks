import os
import logging
import uuid
from flask import Blueprint, request, jsonify
from backend.service.freewilson_service import run_freewilson

freewilson_bp = Blueprint("freewilson", __name__)
UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs/freewilson_output"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

@freewilson_bp.route("/run_analysis", methods=["POST"])
def run_analysis():
    """Runs Free-Wilson analysis and returns a task ID."""
    scaffold_file = request.files.get("scaffold_file")
    input_smiles_file = request.files.get("input_smiles_file")
    activity_file = request.files.get("activity_file")
    job_prefix = request.form.get("prefix", str(uuid.uuid4()))  # Default: random UUID

    if not scaffold_file or not input_smiles_file or not activity_file:
        return jsonify({"error": "Missing required files (scaffold, SMILES, activity)"}), 400

    # Save uploaded files
    scaffold_path = os.path.join(UPLOAD_FOLDER, scaffold_file.filename)
    input_smiles_path = os.path.join(UPLOAD_FOLDER, input_smiles_file.filename)
    activity_path = os.path.join(UPLOAD_FOLDER, activity_file.filename)

    scaffold_file.save(scaffold_path)
    input_smiles_file.save(input_smiles_path)
    activity_file.save(activity_path)

    # Prepare parameters
    params = {
        "scaffold": scaffold_path,
        "input_smiles": input_smiles_path,
        "activity": activity_path,
        "prefix": job_prefix,
        "smarts": request.form.get("smarts"),
        "max_spec": request.form.get("max"),
        "log": request.form.get("log", "false").lower() == "true"
    }

    result = run_freewilson(params)
    return jsonify(result)

@freewilson_bp.route("/check_status/<task_id>", methods=["GET"])
def check_status(task_id):
    """Check if Free-Wilson has finished running."""
    output_log = os.path.join(OUTPUT_FOLDER, f"{task_id}.log")

    if not os.path.exists(output_log):
        return jsonify({"error": "Task ID not found"}), 404

    with open(output_log, "r") as f:
        logs = f.readlines()

    return jsonify({"task_id": task_id, "logs": logs})
