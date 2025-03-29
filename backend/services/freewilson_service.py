import os
import uuid
import logging
import subprocess

FREEWILSON_SCRIPT = os.path.abspath("/home/texsols/BioTasks/tasks/Free-Wilson/free_wilson.py")
OUTPUT_FOLDER = "outputs/freewilson_output"
CONDA_ENV_NAME = "freewilson_env"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def run_freewilson(params):
    """Runs Free-Wilson in the background and returns a task ID."""
    
    # Generate unique task ID for tracking
    task_id = str(uuid.uuid4())
    output_log = os.path.join(OUTPUT_FOLDER, f"{task_id}.log")

    # Prepare the command
    command = f"""
    source ~/miniconda3/etc/profile.d/conda.sh && conda activate {CONDA_ENV_NAME} &&
    python3 {FREEWILSON_SCRIPT} all \
        --scaffold {params['scaffold']} \
        --in {params['input_smiles']} \
        --prefix {params['prefix']} \
        --act {params['activity']} \
        {'--smarts ' + params['smarts'] if params['smarts'] else ''} \
        {'--max ' + params['max_spec'] if params['max_spec'] else ''} \
        {'--log' if params['log'] else ''} \
        > {output_log} 2>&1 &
    """

    logging.info(f"Starting Free-Wilson with task ID: {task_id}")
    subprocess.Popen(command, shell=True, executable="/bin/bash")

    return {
        "message": "Free-Wilson analysis started",
        "task_id": task_id,
        "output_log": output_log
    }
