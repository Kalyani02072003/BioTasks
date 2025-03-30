import os
import subprocess
import logging
import uuid
from backend.database.azure_upload import upload_task_outputs  # Import Azure upload function

# Paths and Constants
FREE_WILSON_SCRIPT = os.path.abspath("/home/texsols/BioTasks/tasks/Free-Wilson/free_wilson.py")
OUTPUT_FOLDER = os.path.abspath("/home/texsols/BioTasks/outputs/freewilson_output")
UPLOAD_FOLDER = os.path.abspath("/home/texsols/BioTasks/uploads")
CONDA_ENV_NAME = "freewilson_env"

# Ensure output directory exists
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def run_freewilson(params):
    """Runs Free-Wilson, uploads outputs to Azure, and returns task details."""

    # Generate a unique task ID
    task_id = params["prefix"] if "prefix" in params else str(uuid.uuid4())
    task_output_folder = os.path.join(OUTPUT_FOLDER, task_id)
    os.makedirs(task_output_folder, exist_ok=True)  # Ensure directory exists
    output_log = os.path.join(task_output_folder, f"{task_id}.log")

    # Ensure all file paths are absolute
    scaffold_path = os.path.abspath(params["scaffold"])
    input_smiles_path = os.path.abspath(params["input_smiles"])
    activity_path = os.path.abspath(params["activity"])

    # Construct command
    max_spec = params.get("max_spec", "")
    max_arg = f'--max "{max_spec}"' if "|" in max_spec else ""
    smarts_arg = f'--smarts "{params["smarts"]}"' if params["smarts"] else ""

    command = f"""
    source ~/miniconda3/etc/profile.d/conda.sh &&
    conda activate {CONDA_ENV_NAME} &&
    python3 {FREE_WILSON_SCRIPT} all \
        --scaffold "{scaffold_path}" \
        --in "{input_smiles_path}" \
        --act "{activity_path}" \
        --prefix "{task_output_folder}/output" \
        {smarts_arg} \
        {max_arg} \
        {f'--log' if params["log"] else ""} \
        > "{output_log}" 2>&1
    """

    logging.info(f"Executing Free-Wilson command:\n{command}")
    subprocess.run(command, shell=True, executable="/bin/bash")

    # Upload all task outputs to Azure Blob Storage
    azure_result = upload_task_outputs(task_id, task_output_folder)

    return {
        "message": "Free-Wilson analysis completed",
        "task_id": task_id,
        "azure_files": azure_result.get("uploaded_files", []),
        "output_log": azure_result.get("uploaded_files", [])[0] if azure_result.get("uploaded_files") else None
    }
