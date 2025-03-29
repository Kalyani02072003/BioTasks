import os
import subprocess
import logging
import uuid

FREE_WILSON_SCRIPT = os.path.abspath("/home/texsols/BioTasks/tasks/Free-Wilson/free_wilson.py")
OUTPUT_FOLDER = os.path.abspath("/home/texsols/BioTasks/outputs/freewilson_output")
UPLOAD_FOLDER = os.path.abspath("/home/texsols/BioTasks/uploads")
CONDA_ENV_NAME = "freewilson_env"

# Ensure output directory exists
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def run_freewilson(params):
    """Runs Free-Wilson in the background and returns a task ID."""

    # Generate unique task ID
    task_id = params["prefix"] if "prefix" in params else str(uuid.uuid4())  
    output_log = os.path.join(OUTPUT_FOLDER, f"{task_id}.log")

    # Ensure all file paths are absolute
    scaffold_path = os.path.abspath(params["scaffold"])
    input_smiles_path = os.path.abspath(params["input_smiles"])
    activity_path = os.path.abspath(params["activity"])

    # Ensure output files are stored in the correct directory
    output_prefix = os.path.join(OUTPUT_FOLDER, task_id)
    descriptor_file_name = f"{output_prefix}_vector.csv"
    model_file_name = f"{output_prefix}_lm.pkl"

    # Properly format --max argument
    max_spec = params.get("max_spec", "")
    max_arg = f'--max "{max_spec}"' if "|" in max_spec else ""

    # Properly quote the --smarts argument
    smarts_arg = f'--smarts "{params["smarts"]}"' if params["smarts"] else ""

    # Construct command
    command = f"""
    source ~/miniconda3/etc/profile.d/conda.sh &&
    conda activate {CONDA_ENV_NAME} &&
    python3 {FREE_WILSON_SCRIPT} all \
        --scaffold "{scaffold_path}" \
        --in "{input_smiles_path}" \
        --act "{activity_path}" \
        --prefix "{output_prefix}" \
        {smarts_arg} \
        {max_arg} \
        {f'--log' if params["log"] else ""} \
        > "{output_log}" 2>&1 &
    """

    logging.info(f"Executing Free-Wilson command:\n{command}")

    # Run command in the background
    subprocess.Popen(command, shell=True, executable="/bin/bash")

    return {
        "message": "Free-Wilson analysis started",
        "task_id": task_id,
        "log_file": output_log,
        "output_folder": OUTPUT_FOLDER
    }
