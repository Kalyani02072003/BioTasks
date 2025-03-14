import os
from flask import Blueprint, request, jsonify
from backend.services.ligand_mpnn_service import run_ligandmpnn

ligandmpnn_bp = Blueprint("ligandmpnn", __name__)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "ligandmpnn_output"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@ligandmpnn_bp.route("/design", methods=["POST"])
def design():
    """Starts LigandMPNN and returns a task ID."""
    pdb_file = request.files.get("pdb_file")
    chains_to_design = request.form.get("chains_to_design")
    fixed_residues = request.form.get("fixed_residues", "")
    residues_to_design = request.form.get("residues_to_design", "")  # Ensure default value
    temperature = request.form.get("temperature", 0.1, type=float)
    number_of_batches = request.form.get("number_of_batches", 8, type=int)  # Ensure correct key

    if not pdb_file or not chains_to_design:
        return jsonify({"error": "PDB file and Chains to Design are required."}), 400

    filepath = os.path.join(UPLOAD_FOLDER, pdb_file.filename)
    pdb_file.save(filepath)

    data = {
        "pdb_file": filepath,
        "chains_to_design": chains_to_design,
        "fixed_residues": fixed_residues,
        "residues_to_design": residues_to_design,  # Ensure default value
        "temperature": temperature,
        "number_of_batches": number_of_batches  # Updated key
    }

    result = run_ligandmpnn(data)
    return jsonify(result)


@ligandmpnn_bp.route("/check_status/<task_id>", methods=["GET"])
def check_status(task_id):
    """Check if LigandMPNN has finished running."""
    output_log = os.path.join(OUTPUT_FOLDER, f"{task_id}.log")

    if not os.path.exists(output_log):
        return jsonify({"error": "Task ID not found"}), 404

    with open(output_log, "r") as f:
        logs = f.readlines()

    return jsonify({"task_id": task_id, "logs": logs})
