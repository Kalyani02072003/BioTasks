import os
import subprocess
import logging
import glob
import shutil
from backend.database.azure_upload import upload_task_outputs  # Azure upload function

# Paths and Constants
ANTIFOLD_SCRIPT = "/home/texsols/BioTasks/tasks/AntiFold/antifold/main.py"
OUTPUT_FOLDER = "/home/texsols/BioTasks/outputs/antifold_output"  # Main output directory
UPLOAD_FOLDER = "/home/texsols/BioTasks/uploads"
CONDA_ENV_NAME = "antifold_cpu"
ANTIFOLD_WORKING_DIR = "/home/texsols/BioTasks/tasks/AntiFold"

# Ensure output directory exists
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def run_antifold(params):
    """Runs AntiFold and uploads outputs to Azure."""
    
    task_id = params["task_id"]
    task_output_folder = os.path.join(OUTPUT_FOLDER, task_id)
    os.makedirs(task_output_folder, exist_ok=True)  # Ensure task-specific folder exists

    output_log = os.path.join(task_output_folder, f"{task_id}.log")

    # Construct the execution command
    command = f"""
    source ~/miniconda3/etc/profile.d/conda.sh &&
    conda activate {CONDA_ENV_NAME} &&
    python3 {ANTIFOLD_SCRIPT} --pdb_file {params['pdb_file']} --heavy_chain {params['heavy_chain']} --light_chain {params['light_chain']} > "{output_log}" 2>&1
    """

    logging.info(f"Executing AntiFold command:\n{command}")
    subprocess.run(command, shell=True, executable="/bin/bash", cwd=ANTIFOLD_WORKING_DIR)

    # Move the generated output files to the task-specific folder
    move_antifold_outputs(task_id)  # Move files to the correct task folder

    # Upload task outputs to Azure
    azure_result = upload_task_outputs(task_id, task_output_folder)

    return {
        "message": "AntiFold processing completed",
        "task_id": task_id,
        "azure_files": azure_result.get("uploaded_files", []),
        "output_log": azure_result.get("uploaded_files", [])[0] if azure_result.get("uploaded_files") else None
    }


def move_antifold_outputs(task_id):
    """Moves AntiFold output files (CSV, FASTA, LOG) into the correct task folder."""
    task_output_folder = os.path.join(OUTPUT_FOLDER, task_id)  # Create task-specific folder
    os.makedirs(task_output_folder, exist_ok=True)  # Ensure the task folder exists
    misplaced_files = glob.glob(os.path.join(OUTPUT_FOLDER, "*.*"))  # Find all misplaced files

    for file_path in misplaced_files:
        if task_id in file_path:  # Ensure it's part of the current task
            correct_path = os.path.join(task_output_folder, os.path.basename(file_path))
            shutil.move(file_path, correct_path)
            logging.info(f"Moved {file_path} → {correct_path}")

