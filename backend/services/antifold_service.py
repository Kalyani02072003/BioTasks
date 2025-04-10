import os
import subprocess
import logging
import uuid
from backend.database.azure_upload import upload_task_outputs  # Azure upload function

# Paths and Constants
ANTIFOLD_SCRIPT = os.path.abspath("/home/texsols/BioTasks/tasks/AntiFold/antifold/main.py")
OUTPUT_FOLDER = os.path.abspath("/home/texsols/BioTasks/outputs/antifold_output")
UPLOAD_FOLDER = os.path.abspath("/home/texsols/BioTasks/uploads")
CONDA_ENV_NAME = "antifold_cpu"

# Ensure output directory exists
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def extract_chain_ids(pdb_file):
    """Extract unique chain IDs from a PDB file."""
    with open(pdb_file, "r") as f:
        chains = set(line.split()[4] for line in f if line.startswith("ATOM"))
    return list(chains)


def run_antifold(params):
    """Runs AntiFold, sets correct --out_dir, uploads outputs to Azure, and returns task details."""
    task_id = params["task_id"]
    task_output_folder = os.path.join(OUTPUT_FOLDER, task_id)
    os.makedirs(task_output_folder, exist_ok=True)  # Ensure output folder exists

    # Define log file
    output_log = os.path.join(task_output_folder, f"{task_id}.log")

    # Construct the command with --out_dir
    command = f"""
    source ~/miniconda3/etc/profile.d/conda.sh &&
    conda activate {CONDA_ENV_NAME} &&
    python3 {ANTIFOLD_SCRIPT} \
        --out_dir "{task_output_folder}" \
        --pdb_file "{params['pdb_file']}" \
        --heavy_chain "{params['heavy_chain']}" \
        --light_chain "{params['light_chain']}" \
        > "{output_log}" 2>&1
    """

    logging.info(f"Executing AntiFold command:\n{command}")
    subprocess.run(command, shell=True, executable="/bin/bash")
    # subprocess.run(command,shell=True,executable="/bin/bash",cwd="/home/texsols/BioTasks/tasks/AntiFold")
    
    # Upload task outputs to Azure
    azure_result = upload_task_outputs(task_id, task_output_folder)

    return {
        "message": "AntiFold processing completed",
        "task_id": task_id,
        "azure_files": azure_result.get("uploaded_files", []),
        "output_log": azure_result.get("uploaded_files", [])[0] if azure_result.get("uploaded_files") else None
    }