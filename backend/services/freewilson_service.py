import os
import subprocess
import logging
import uuid

FREE_WILSON_SCRIPT = "/home/texsols/BioTasks/tasks/Free-Wilson/free_wilson.py"
OUTPUT_FOLDER = "outputs/freewilson_output"
CONDA_ENV_NAME = "freewilson_env"

def run_freewilson(params):
    """Runs Free-Wilson in the background and returns a task ID."""
    task_id = params["prefix"] if "prefix" in params else str(uuid.uuid4())  
    output_log = os.path.join(OUTPUT_FOLDER, f"{task_id}.log")

    # Construct command
    command = f"""
    source ~/miniconda3/etc/profile.d/conda.sh && conda activate {CONDA_ENV_NAME} &&
    python3 {FREE_WILSON_SCRIPT} all \
        --scaffold {params["scaffold"]} \
        --in {params["input_smiles"]} \
        --act {params["activity"]} \
        --prefix {task_id} \
        {f'--smarts {params["smarts"]}' if params["smarts"] else ""} \
        {f'--max {params["max_spec"]}' if params["max_spec"] else ""} \
        {f'--log' if params["log"] else ""} \
        > {output_log} 2>&1 &
    """

    logging.info(f"Executing Free-Wilson command: {command}")
    
    # Run command in the background
    subprocess.Popen(command, shell=True, executable="/bin/bash")

    return {
        "message": "Free-Wilson analysis started",
        "task_id": task_id,
        "output_log": output_log
    }
