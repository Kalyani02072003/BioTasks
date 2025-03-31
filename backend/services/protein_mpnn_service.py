import os
import subprocess
import logging
import uuid
from backend.database.azure_upload import upload_task_outputs  # Azure upload function

# Paths and Constants
PROTEINMPNN_SCRIPT = "/app/proteinmpnn_ddg/predict.py"
OUTPUT_FOLDER = "/home/texsols/BioTasks/outputs/proteinmpnn_output"
UPLOAD_FOLDER = "/home/texsols/BioTasks/uploads"
DOCKER_IMAGE = "ghcr.io/peptoneltd/proteinmpnn_ddg:1.0.0_base_cpu"

# Ensure output directory exists
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def run_proteinmpnn(params):
    """Runs ProteinMPNN, uploads outputs to Azure, and returns task details."""
    
    # Generate unique task ID
    task_id = params["task_id"]
    task_output_folder = os.path.join(OUTPUT_FOLDER, task_id)
    os.makedirs(task_output_folder, exist_ok=True)  # Ensure task folder exists
    output_log = os.path.join(task_output_folder, f"{task_id}.log")
    output_csv = os.path.join(task_output_folder, f"{task_id}_predictions.csv")

    # Construct command
    command = f"""
    docker run \
    -v {UPLOAD_FOLDER}:/workspace \
    -v {task_output_folder}:/outputs \
    --workdir /workspace \
    {DOCKER_IMAGE} \
    python3 {PROTEINMPNN_SCRIPT} \
    --pdb_path /workspace/{os.path.basename(params['pdb_file'])} \
    --chains {params["chain"]} \
    --outpath /outputs/{task_id}_predictions.csv \
    > "{output_log}" 2>&1
    """

    logging.info(f"Executing ProteinMPNN command:\n{command}")
    subprocess.run(command, shell=True, executable="/bin/bash")

    # Upload task outputs to Azure
    azure_result = upload_task_outputs(task_id, task_output_folder)

    return {
        "message": "ProteinMPNN processing completed",
        "task_id": task_id,
        "azure_files": azure_result.get("uploaded_files", []),
        "output_log": azure_result.get("uploaded_files", [])[0] if azure_result.get("uploaded_files") else None
    }
