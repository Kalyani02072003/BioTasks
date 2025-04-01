import os
import subprocess
import logging
import uuid
from backend.database.azure_upload import upload_task_outputs  # Azure upload function

# Paths and Constants
ANTIFOLD_SCRIPT = "/home/texsols/BioTasks/antifold/run_antifold.py"  # Path to AntiFold script
OUTPUT_FOLDER = "/home/texsols/BioTasks/outputs/antifold_output"
UPLOAD_FOLDER = "/home/texsols/BioTasks/uploads"

# Ensure output directory exists
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def run_antifold(params):
    """Runs AntiFold, uploads outputs to Azure, and returns task details."""
    
    # Generate unique task ID
    task_id = params["task_id"]
    task_output_folder = os.path.join(OUTPUT_FOLDER, task_id)
    os.makedirs(task_output_folder, exist_ok=True)  # Ensure task folder exists
    
    # Define output file paths
    output_log = os.path.join(task_output_folder, f"{task_id}.log")
    output_csv = os.path.join(task_output_folder, f"{task_id}_predictions.csv")
    output_fasta = os.path.join(task_output_folder, f"{task_id}_predictions.fasta")

    # Construct command to run AntiFold (no Docker)
    command = f"""
    python3 {ANTIFOLD_SCRIPT} \
    --input_pdb {os.path.join(UPLOAD_FOLDER, os.path.basename(params['pdb_file']))} \
    --out_csv {output_csv} \
    --out_fasta {output_fasta} \
    > "{output_log}" 2>&1
    """

    logging.info(f"Executing AntiFold command:\n{command}")
    subprocess.run(command, shell=True, executable="/bin/bash")

    # Upload task outputs to Azure
    azure_result = upload_task_outputs(task_id, task_output_folder)

    return {
        "message": "AntiFold processing completed",
        "task_id": task_id,
        "azure_files": azure_result.get("uploaded_files", []),
        "output_log": azure_result.get("uploaded_files", [])[0] if azure_result.get("uploaded_files") else None
    }
