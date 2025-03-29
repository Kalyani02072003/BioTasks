import os
import subprocess
import uuid
import json

TS_SCRIPT = os.path.abspath("/home/texsols/BioTasks/tasks/TS/ts_main.py")
OUTPUT_FOLDER = "outputs/ts_output"
CONDA_ENV_NAME = "ts_env"

DEFAULT_REAGENTS = [
    "data/primary_amines_ok.smi",
    "data/carboxylic_acids_ok.smi"
]

EVALUATOR_ARGS = {
    "FPEvaluator": {"query_smiles": "COC(=O)[C@@H](O)CC(=O)Nc1nncc2ccccc12"},
    "MLClassifierEvaluator": {"model_filename": "mapk1_modl.pkl"},
    "FredEvaluator": {"design_unit_file": "data/2zdt_receptor.oedu"},
    "ROCSEvaluator": {"query_molfile": "data/2chw_lig.sdf"}
}

def run_thompson_sampling(params):
    """Runs Thompson Sampling in the background and returns a task ID."""
    task_id = str(uuid.uuid4())
    output_file = os.path.join(OUTPUT_FOLDER, f"{task_id}.csv")
    output_log = os.path.join(OUTPUT_FOLDER, f"{task_id}.log")
    json_path = os.path.join(OUTPUT_FOLDER, f"{task_id}.json")

    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    evaluator = params["evaluator"]
    evaluator_arg = params.get("evaluator_arg", EVALUATOR_ARGS.get(evaluator, {}))

    json_config = {
        "reagent_file_list": params.get("reagent_file_list", DEFAULT_REAGENTS),
        "reaction_smarts": params["reaction_smarts"],
        "num_warmup_trials": params["num_warmup_trials"],
        "num_ts_iterations": params["num_ts_iterations"],
        "evaluator_class_name": evaluator,
        "evaluator_arg": evaluator_arg,
        "ts_mode": params["ts_mode"],
        "log_filename": output_log,
        "results_filename": output_file
    }

    with open(json_path, "w") as f:
        json.dump(json_config, f, indent=4)

    command = f"""
    source ~/miniconda3/etc/profile.d/conda.sh && conda activate {CONDA_ENV_NAME} &&
    python3 {TS_SCRIPT} {json_path} > {output_log} 2>&1 &
    """

    subprocess.Popen(command, shell=True, executable="/bin/bash")

    return {
        "message": "Thompson Sampling started",
        "task_id": task_id,
        "output_file": output_file,
        "output_log": output_log
    }
