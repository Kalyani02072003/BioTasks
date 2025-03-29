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
    smarts = params.get("smarts", "").replace("(", "\(").replace(")", "\)")
    command = f"""
        python3 /home/texsols/BioTasks/tasks/Free-Wilson/free_wilson.py all \
            --scaffold {params["scaffold_file"]} \
            --in {params["input_smiles_file"]} \
            --prefix {params["prefix"]} \
            --act {params["activity_file"]} \
            --smarts "{params['smarts']}" \
            --max {params["max"]} \
            --log \
            > {output_log} 2>&1 &
    """



    logging.info(f"Starting Free-Wilson with task ID: {task_id}")
    subprocess.Popen(command, shell=True, executable="/bin/bash")

    return {
        "message": "Free-Wilson analysis started",
        "task_id": task_id,
        "output_log": output_log
    }
