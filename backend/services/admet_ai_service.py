import os
import subprocess
import logging

from backend.database.azure_upload import upload_task_outputs

ADMET_SCRIPT = os.path.abspath("/home/texsols/BioTasks/tasks/admet_ai/admet_ai/admet_predict.py")  # wrapper script or command
OUTPUT_FOLDER = os.path.abspath("/home/texsols/BioTasks/outputs/admet_ai_output")
CONDA_ENV_NAME = "admet_ai"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def run_admet_ai(params):
    task_id = params["task_id"]
    smiles_file = params["smiles_file"]
    task_output_folder = os.path.join(OUTPUT_FOLDER, task_id)
    os.makedirs(task_output_folder, exist_ok=True)

    output_file = os.path.join(task_output_folder, "predictions.csv")
    log_file = os.path.join(task_output_folder, f"{task_id}.log")

    command = f"""
    source ~/miniconda3/etc/profile.d/conda.sh &&
    conda activate {CONDA_ENV_NAME} &&
    admet_predict --data_path "{smiles_file}" --save_path "{output_file}" --smiles_column smiles \
    > "{log_file}" 2>&1
    """

    logging.info(f"Running ADMET prediction:\n{command}")
    subprocess.run(command, shell=True, executable="/bin/bash")

    azure_result = upload_task_outputs(task_id, task_output_folder)

    return {
        "message": "ADMET AI prediction completed",
        "task_id": task_id,
        "azure_files": azure_result.get("uploaded_files", []),
        "output_log": azure_result.get("uploaded_files", [])[0] if azure_result.get("uploaded_files") else None
    }
