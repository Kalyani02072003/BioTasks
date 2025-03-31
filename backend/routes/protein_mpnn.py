import os
import logging
import uuid
from flask import Blueprint, request, jsonify
from backend.services.protein_mpnn_service import run_proteinmpnn
from backend.database.azure_upload import upload_task_outputs  # Azure upload function

# Define Blueprint
proteinmpnn_bp = Blueprint("proteinmpnn", __name__)

# Define Directories
UPLOAD_FOLDER = "/home/texsols/BioTasks/uploads"
OUTPUT_FOLDER = "/home/texsols/BioTasks/outputs/proteinmpnn_output"

# Ensure Directories Exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


@proteinmpnn_bp.route("/ddg", methods=["POST"])
def ddg():
    """Starts ProteinMPNN and returns a task ID with Azure Blob Storage links."""
    try:
        pdb_file = request.files.get("pdb_file")
        chain = request.form.get("chain", "A")

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
            "pdb_file": pdb_filepath,
            "chain": chain,
            "task_id": task_id
        }

        # Log and Run ProteinMPNN
        logging.info(f"Starting ProteinMPNN with task ID: {task_id}")
        result = run_proteinmpnn(params)

        return jsonify(result)

    except Exception as e:
        logging.error(f"Error in ddg: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@proteinmpnn_bp.route("/check_status/<task_id>", methods=["GET"])
def check_status(task_id):
    """Check if ProteinMPNN has finished running and return Azure storage links."""
    try:
        task_folder = os.path.join(OUTPUT_FOLDER, task_id)
        log_file = os.path.join(task_folder, f"{task_id}.log")

        if not os.path.exists(log_file):
            logging.warning(f"Task ID {task_id} not found.")
            return jsonify({"error": "Task ID not found"}), 404

        # Read log file (Optional)
        with open(log_file, "r") as f:
            logs = f.readlines()

        # Upload task outputs to Azure
        azure_result = upload_task_outputs(task_id, task_folder)

        return jsonify({
            "task_id": task_id,
            "logs": logs,
            "azure_files": azure_result.get("uploaded_files", [])
        })

    except Exception as e:
        logging.error(f"Error in check_status: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500
