import os
import logging
import uuid
from flask import Blueprint, request, jsonify
from backend.services.antifold_service import run_antifold
from backend.database.azure_upload import upload_task_outputs  # Azure upload function

# Define Blueprint
antifold_bp = Blueprint("antifold", __name__)

# Define Directories
UPLOAD_FOLDER = "/home/texsols/BioTasks/uploads"
OUTPUT_FOLDER = "/home/texsols/BioTasks/outputs/antifold_output"

# Ensure Directories Exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


@antifold_bp.route("/predict", methods=["POST"])
def predict():
    """Starts AntiFold and returns a task ID with Azure Blob Storage links."""
    try:
        task_type = request.form.get("task_type")
        heavy_chain = request.form.get("heavy_chain")
        light_chain = request.form.get("light_chain")

        # Handle file upload
        pdb_file = request.files.get("pdb_file")
        if not pdb_file:
            logging.error("No PDB file uploaded")
            return jsonify({"error": "No PDB file uploaded"}), 400

        # Generate unique task ID
        task_id = str(uuid.uuid4())

        # Save uploaded file
        pdb_filepath = os.path.join(UPLOAD_FOLDER, f"{task_id}_{pdb_file.filename}")
        pdb_file.save(pdb_filepath)

        # Prepare parameters
        params = {
            "task_type": task_type,
            "pdb_file": pdb_filepath,
            "heavy_chain": heavy_chain,
            "light_chain": light_chain,
            "task_id": task_id
        }

        # Log and Run AntiFold
        logging.info(f"Starting AntiFold with task ID: {task_id}")
        result = run_antifold(params)

        return jsonify(result)

    except Exception as e:
        logging.error(f"Error in predict: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@antifold_bp.route("/check_status/<task_id>", methods=["GET"])
def check_status(task_id):
    """Check if AntiFold has finished running and return Azure storage links."""
    try:
        task_folder = os.path.join(OUTPUT_FOLDER, task_id)
        log_file = os.path.join(task_folder, f"{task_id}.log")

        if not os.path.exists(log_file):
            logging.warning(f"Task ID {task_id} not found.")
            return jsonify({"error": "Task ID not found"}), 404

        # Read log file (Optional)
        with open(log_file, "r") as f:
            logs = f.readlines()

        # Upload task outputs to Azure and get SAS URLs
        azure_result = upload_task_outputs(task_id, task_folder)

        return jsonify({
            "task_id": task_id,
            "logs": logs,
            "azure_files": azure_result.get("uploaded_files", [])
        })

    except Exception as e:
        logging.error(f"Error in check_status: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500
