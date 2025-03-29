import os
import subprocess
import uuid

TS_SCRIPT = os.path.abspath("/home/texsols/BioTasks/tasks/TS/ts_main.py")
OUTPUT_FOLDER = "outputs/ts_output"
CONDA_ENV_NAME = "ts_env"

def run_thompson_sampling(params):
    """Runs Thompson Sampling in the background and returns a task ID."""
    # Generate unique task ID
    task_id = str(uuid.uuid4())
    output_file = os.path.join(OUTPUT_FOLDER, f"{task_id}.csv")
    output_log = os.path.join(OUTPUT_FOLDER, f"{task_id}.log")

    # Ensure output directory exists
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    # Construct the JSON input for Thompson Sampling
    json_config = {
        "reaction_smarts": params["reaction_smarts"],
        "num_warmup_trials": params["num_warmup_trials"],
        "num_ts_iterations": params["num_ts_iterations"],
        "evaluator_class_name": params["evaluator"],
        "ts_mode": params["ts_mode"],
        "evaluator_arg": {"query_smiles": params["query_smiles"]},  # ✅ FIXED format
        "reagent_file_list": params.get("reagent_file_list", []),  # ✅ ADDED DEFAULT EMPTY LIST
        "results_filename": output_file
    }



    # Save JSON configuration
    json_path = os.path.join(OUTPUT_FOLDER, f"{task_id}.json")
    with open(json_path, "w") as f:
        import json
        json.dump(json_config, f, indent=4)

    # Prepare the command
    command = f"""
    source ~/miniconda3/etc/profile.d/conda.sh && conda activate {CONDA_ENV_NAME} &&
    python3 {TS_SCRIPT} {json_path} > {output_log} 2>&1 &
    """

    # Run Thompson Sampling in background
    subprocess.Popen(command, shell=True, executable="/bin/bash")

    return {
        "message": "Thompson Sampling started",
        "task_id": task_id,
        "output_file": output_file,
        "output_log": output_log  # Added log tracking
    }
