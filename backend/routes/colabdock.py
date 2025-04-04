import os
import uuid
import logging
from flask import Blueprint, request, jsonify
from backend.services.colabdock_service import run_colabdock
from backend.database.azure_upload import upload_task_outputs

colabdock_bp = Blueprint("colabdock", __name__)

UPLOAD_FOLDER = "/home/texsols/BioTasks/uploads"
OUTPUT_FOLDER = "/home/texsols/BioTasks/outputs/colabdock_output"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


@colabdock_bp.route("/dock", methods=["POST"])
def dock():
    try:
        pdb_file = request.files.get("pdb_file")
        if not pdb_file:
            logging.error("No PDB file uploaded")
            return jsonify({"error": "No PDB file uploaded"}), 400

        task_id = str(uuid.uuid4())
        pdb_path = os.path.join(UPLOAD_FOLDER, f"{task_id}_{pdb_file.filename}")
        pdb_file.save(pdb_path)

        params = {
            "task_id": task_id,
            "pdb_file": pdb_path,
        }

        logging.info(f"Starting ColabDock task ID: {task_id}")
        result = run_colabdock(params)

        return jsonify(result)

    except Exception as e:
        logging.error(f"Error in dock: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@colabdock_bp.route("/check_status/<task_id>", methods=["GET"])
def check_status(task_id):
    try:
        task_folder = os.path.join(OUTPUT_FOLDER, task_id)
        log_file = os.path.join(task_folder, f"{task_id}.log")

        if not os.path.exists(log_file):
            return jsonify({"error": "Task ID not found"}), 404

        with open(log_file, "r") as f:
            logs = f.readlines()

        azure_result = upload_task_outputs(task_id, task_folder)

        return jsonify({
            "task_id": task_id,
            "logs": logs,
            "azure_files": azure_result.get("uploaded_files", [])
        })

    except Exception as e:
        logging.error(f"Error in check_status: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500
