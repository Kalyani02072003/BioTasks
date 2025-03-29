import os
import subprocess
import logging
import uuid

FREE_WILSON_SCRIPT = os.path.abspath("/home/texsols/BioTasks/tasks/Free-Wilson/free_wilson.py")
OUTPUT_FOLDER = os.path.abspath("/home/texsols/BioTasks/outputs/freewilson_output")
UPLOAD_FOLDER = os.path.abspath("/home/texsols/BioTasks/uploads")
CONDA_ENV_NAME = "freewilson_env"

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def run_freewilson(params):
    """Runs Free-Wilson in the background and returns a task ID."""
    task_id = params["prefix"] if "prefix" in params else str(uuid.uuid4())  
    output_log = os.path.join(OUTPUT_FOLDER, f"{task_id}.log")

    # Ensure all file paths are absolute
    scaffold_path = os.path.abspath(params["scaffold"])
    input_smiles_path = os.path.abspath(params["input_smiles"])
    activity_path = os.path.abspath(params["activity"])

    # Ensure output files are written inside the correct directory
    output_dir = OUTPUT_FOLDER
    descriptor_file_name = os.path.join(output_dir, f"{task_id}_vector.csv")
    model_file_name = os.path.join(output_dir, f"{task_id}_lm.pkl")

    # Properly format --max argument
    max_spec = params.get("max_spec", "")
    max_arg = f'--max "{max_spec}"' if max_spec and "|" in max_spec else ""

    # Properly quote the --smarts argument
    smarts_arg = f'--smarts "{params["smarts"]}"' if params["smarts"] else ""

    # Construct command
    command = f"""
    source ~/miniconda3/etc/profile.d/conda.sh && conda activate {CONDA_ENV_NAME} &&
    python3 {FREE_WILSON_SCRIPT} all \
        --scaffold {scaffold_path} \
        --in {input_smiles_path} \
        --act {activity_path} \
        --prefix {task_id} \
        {smarts_arg} \
        {max_arg} \
        {f'--log' if params["log"] else ""} \
        > {output_log} 2>&1
    """

    logging.info(f"Executing Free-Wilson command:\n{command}")

    # Run command in the background
    process = subprocess.Popen(command, shell=True, executable="/bin/bash", stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    return {
        "message": "Free-Wilson analysis started",
        "task_id": task_id,
        "output_log": output_log
    }
