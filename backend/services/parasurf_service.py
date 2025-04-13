import os
import subprocess
import logging
from backend.database.azure_upload import upload_task_outputs

PARASURF_SCRIPT = os.path.abspath("/home/texsols/BioTasks/tasks/ParaSurf/blind_predict.py")
MODEL_WEIGHTS = os.path.abspath("/home/texsols/BioTasks/tasks/ParaSurf/model_weights/pecan/PECAN_best.pth")
OUTPUT_FOLDER = os.path.abspath("/home/texsols/BioTasks/outputs/parasurf_output")
CONDA_ENV_NAME = "ParaSurf"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def run_parasurf(params):
    task_id = params["task_id"]
    task_output_folder = os.path.join(OUTPUT_FOLDER, task_id)
    os.makedirs(task_output_folder, exist_ok=True)

    output_log = os.path.join(task_output_folder, f"{task_id}.log")

    command = f"""
    source ~/miniconda3/etc/profile.d/conda.sh &&
    conda activate {CONDA_ENV_NAME} &&
    PARASURF_OUTPUT_PATH="{task_output_folder}" \
    python3 {PARASURF_SCRIPT} \
        --receptor "{params['pdb_file']}" \
        --model_weights "{MODEL_WEIGHTS}" \
        --device "cpu" \
        --output_dir "{task_output_folder}" \
        > "{output_log}" 2>&1
    """

    logging.info(f"Executing ParaSurf command:\n{command}")
    subprocess.run(command, shell=True, executable="/bin/bash")

    azure_result = upload_task_outputs(task_id, task_output_folder)

    return {
        "message": "ParaSurf processing completed",
        "task_id": task_id,
        "azure_files": azure_result.get("uploaded_files", []),
        "output_log": azure_result.get("uploaded_files", [])[0] if azure_result.get("uploaded_files") else None
    }
