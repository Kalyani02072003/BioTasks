import os
import subprocess
import logging
import uuid
from backend.database.azure_upload import upload_task_outputs  # Azure upload function

# Paths and Constants
LIGANDMPNN_SCRIPT = os.path.abspath("/home/texsols/BioTasks/tasks/LigandMPNN/run.py")
MODEL_CHECKPOINT = os.path.abspath("/home/texsols/BioTasks/tasks/LigandMPNN/model_params/proteinmpnn_v_48_020.pt")
WORKING_DIR = os.path.abspath("/home/texsols/BioTasks/tasks/LigandMPNN")
OUTPUT_FOLDER = os.path.abspath("/home/texsols/BioTasks/outputs/ligandmpnn_output")
UPLOAD_FOLDER = os.path.abspath("/home/texsols/BioTasks/uploads")
CONDA_ENV = "ligandmpnn_env"

# Ensure output directory exists
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def run_ligandmpnn(params):
    """Runs LigandMPNN, uploads outputs to Azure, and returns task details."""
    
    # Generate unique task ID
    task_id = params["task_id"]
    task_output_folder = os.path.join(OUTPUT_FOLDER, task_id)
    os.makedirs(task_output_folder, exist_ok=True)  # Ensure task folder exists
    output_log = os.path.join(task_output_folder, f"{task_id}.log")

    # Construct command ensuring the correct working directory
    command = f"""
    source ~/miniconda3/etc/profile.d/conda.sh &&
    conda activate {CONDA_ENV} &&
    cd {WORKING_DIR} &&
    python3 {LIGANDMPNN_SCRIPT} \
        --pdb_path "{params['pdb_file']}" \
        --checkpoint_path "{MODEL_CHECKPOINT}" \
        --out_folder "{task_output_folder}" \
        --chains_to_design {params["chains_to_design"]} \
        {f'--redesigned_residues {params.get("residues_to_design")}' if params.get("residues_to_design") else ""} \
        --temperature {params["temperature"]} \
        --number_of_batches {params["number_of_batches"]} \
        > "{output_log}" 2>&1
    """

    logging.info(f"Executing LigandMPNN command:\n{command}")
    subprocess.run(command, shell=True, executable="/bin/bash")

    # Upload task outputs to Azure
    azure_result = upload_task_outputs(task_id, task_output_folder)

    return {
        "message": "LigandMPNN processing completed",
        "task_id": task_id,
        "azure_files": azure_result.get("uploaded_files", []),
        "output_log": azure_result.get("uploaded_files", [])[0] if azure_result.get("uploaded_files") else None
    }
