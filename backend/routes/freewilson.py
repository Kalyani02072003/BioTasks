import os
import logging
import uuid
from flask import Blueprint, request, jsonify
from backend.services.freewilson_service import run_freewilson
from backend.database.azure_upload import upload_task_outputs

# Define Blueprint
freewilson_bp = Blueprint("freewilson", __name__)

# Define Directories
UPLOAD_FOLDER = "/home/texsols/BioTasks/uploads"
OUTPUT_FOLDER = "/home/texsols/BioTasks/outputs/freewilson_output"

# Ensure Directories Exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


@freewilson_bp.route("/run_analysis", methods=["POST"])
def run_analysis():
    """Runs Free-Wilson analysis and returns a task ID with Azure Blob Storage links."""
    try:
        scaffold_file = request.files.get("scaffold_file")
        input_smiles_file = request.files.get("input_smiles_file")
        activity_file = request.files.get("activity_file")
        job_prefix = request.form.get("prefix", str(uuid.uuid4()))  # Default: random UUID

        # Validate Required Files
        if not scaffold_file or not input_smiles_file or not activity_file:
            logging.error("Missing required files: scaffold, SMILES, or activity")
            return jsonify({"error": "Missing required files (scaffold, SMILES, activity)"}), 400

        # Save Uploaded Files in `uploads/`
        scaffold_path = os.path.join(UPLOAD_FOLDER, scaffold_file.filename)
        input_smiles_path = os.path.join(UPLOAD_FOLDER, input_smiles_file.filename)
        activity_path = os.path.join(UPLOAD_FOLDER, activity_file.filename)

        scaffold_file.save(scaffold_path)
        input_smiles_file.save(input_smiles_path)
        activity_file.save(activity_path)

        # Prepare Parameters
        params = {
            "scaffold": scaffold_path,
            "input_smiles": input_smiles_path,
            "activity": activity_path,
            "prefix": job_prefix,
            "smarts": request.form.get("smarts", ""),
            "max_spec": request.form.get("max", ""),
            "log": request.form.get("log", "false").lower() == "true"
        }

        # Log and Run Free-Wilson
        logging.info(f"Starting Free-Wilson analysis with task ID: {job_prefix}")
        result = run_freewilson(params)

        return jsonify(result)

    except Exception as e:
        logging.error(f"Error in run_analysis: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@freewilson_bp.route("/check_status/<task_id>", methods=["GET"])
def check_status(task_id):
    """Check if Free-Wilson has finished running and return Azure storage links."""
    try:
        task_folder = os.path.join(OUTPUT_FOLDER, task_id)
        log_file = os.path.join(task_folder, f"{task_id}.log")

        if not os.path.exists(log_file):
            logging.warning(f"Task ID {task_id} not found.")
            return jsonify({"error": "Task ID not found"}), 404

        # Read the local log file (Optional)
        with open(log_file, "r") as f:
            logs = f.readlines()

        # Get Azure Blob Storage links
        azure_result = upload_task_outputs(task_id, task_folder)

        return jsonify({
            "task_id": task_id,
            "logs": logs,
            "azure_files": azure_result.get("uploaded_files", [])
        })

    except Exception as e:
        logging.error(f"Error in check_status: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500
