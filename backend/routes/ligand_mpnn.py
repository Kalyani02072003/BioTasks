import os
import logging
import uuid
from flask import Blueprint, request, jsonify
from backend.services.ligand_mpnn_service import run_ligandmpnn
from backend.database.azure_upload import upload_task_outputs  # Azure upload function

# Define Blueprint
ligandmpnn_bp = Blueprint("ligandmpnn", __name__)

# Define Directories
UPLOAD_FOLDER = "/home/texsols/BioTasks/uploads"
OUTPUT_FOLDER = "/home/texsols/BioTasks/outputs/ligandmpnn_output"

# Ensure Directories Exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


@ligandmpnn_bp.route("/design", methods=["POST"])
def design():
    """Starts LigandMPNN and returns a task ID with Azure Blob Storage links."""
    try:
        pdb_file = request.files.get("pdb_file")
        chains_to_design = request.form.get("chains_to_design")
        fixed_residues = request.form.get("fixed_residues", "")
        residues_to_design = request.form.get("residues_to_design", "")  # Ensure default value
        temperature = request.form.get("temperature", 0.1, type=float)
        number_of_batches = request.form.get("number_of_batches", 8, type=int)  # Ensure correct key

        if not pdb_file or not chains_to_design:
            logging.error("PDB file and Chains to Design are required.")
            return jsonify({"error": "PDB file and Chains to Design are required."}), 400

        # Generate unique task ID
        task_id = str(uuid.uuid4())

        # Save uploaded file
        pdb_filepath = os.path.join(UPLOAD_FOLDER, f"{task_id}_{pdb_file.filename}")
        pdb_file.save(pdb_filepath)

        # Prepare parameters
        params = {
            "pdb_file": pdb_filepath,
            "chains_to_design": chains_to_design,
            "fixed_residues": fixed_residues,
            "residues_to_design": residues_to_design,  # Ensure default value
            "temperature": temperature,
            "number_of_batches": number_of_batches,  # Updated key
            "task_id": task_id
        }

        # Log and Run LigandMPNN
        logging.info(f"Starting LigandMPNN with task ID: {task_id}")
        result = run_ligandmpnn(params)

        return jsonify(result)

    except Exception as e:
        logging.error(f"Error in design: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@ligandmpnn_bp.route("/check_status/<task_id>", methods=["GET"])
def check_status(task_id):
    """Check if LigandMPNN has finished running and return Azure storage links."""
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
