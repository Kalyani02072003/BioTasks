import os
import subprocess
import logging
from backend.database.azure_upload import upload_task_outputs

COLABDOCK_SCRIPT = "/home/texsols/BioTasks/tasks/ColabDock/main.py"
COLABDOCK_DIR = "/home/texsols/BioTasks/tasks/ColabDock"
OUTPUT_FOLDER = "/home/texsols/BioTasks/outputs/colabdock_output"
CONDA_ENV_NAME = "colabdock"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def run_colabdock(params):
    task_id = params["task_id"]
    task_output_folder = os.path.join(OUTPUT_FOLDER, task_id)
    os.makedirs(task_output_folder, exist_ok=True)

    output_log = os.path.join(task_output_folder, f"{task_id}.log")

    command = f"""
    source ~/miniconda3/etc/profile.d/conda.sh && \
    conda activate {CONDA_ENV_NAME} && \
    cd {COLABDOCK_DIR} && \
    cp "{params['pdb_file']}" ./input.pdb && \
    python main.py -c config.py > "{output_log}" 2>&1 && \
    mv results/* "{task_output_folder}/"
    """

    logging.info(f"Executing ColabDock command:\n{command}")
    subprocess.run(command, shell=True, executable="/bin/bash")

    azure_result = upload_task_outputs(task_id, task_output_folder)

    return {
        "message": "ColabDock docking completed",
        "task_id": task_id,
        "azure_files": azure_result.get("uploaded_files", []),
        "output_log": azure_result.get("uploaded_files", [])[0] if azure_result.get("uploaded_files") else None
    }
