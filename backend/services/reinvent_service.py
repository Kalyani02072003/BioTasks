import os
import subprocess
import logging

from backend.database.azure_upload import upload_task_outputs

# Constants
OUTPUT_FOLDER = os.path.abspath("/home/texsols/BioTasks/outputs/reinvent_output")
UPLOAD_FOLDER = os.path.abspath("/home/texsols/BioTasks/uploads")
CONDA_ENV_NAME = "reinvent4"
MODEL_PATH = os.path.abspath("/home/texsols/BioTasks/tasks/REINVENT4/priors/reinvent.prior")
REINVENT_EXECUTABLE = "/home/texsols/BioTasks/biotaskvenv/bin/reinvent"

# Ensure output folder exists
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def run_reinvent(params):
    task_id = params["task_id"]
    smiles = params["smiles"]

    task_output_folder = os.path.join(OUTPUT_FOLDER, task_id)
    os.makedirs(task_output_folder, exist_ok=True)

    smiles_file = os.path.join(task_output_folder, f"{task_id}.smi")
    with open(smiles_file, "w") as f:
        f.write(smiles)

    output_csv_path = os.path.join(task_output_folder, "sampling.csv")
    toml_config_path = os.path.join(task_output_folder, "sampling.toml")

    # Write REINVENT-compatible TOML config
    with open(toml_config_path, "w") as f:
        f.write(f"""
        run_type = "sampling"
        device = "cpu"
        json_out_config = "_sampling.json"

        [parameters]
        model_file = "{MODEL_PATH}"
        smiles_file = "{smiles_file}"
        output_file = "{output_csv_path}"
        num_smiles = 157
        unique_molecules = true
        randomize_smiles = true
        """)

    output_log = os.path.join(task_output_folder, f"{task_id}.log")

    command = f"""
    source ~/miniconda3/etc/profile.d/conda.sh &&
    conda activate {CONDA_ENV_NAME} &&
    {REINVENT_EXECUTABLE} -l "{task_output_folder}/sampling.log" "{toml_config_path}" \
    > "{output_log}" 2>&1
    """


    logging.info(f"Running REINVENT task with command:\n{command}")
    subprocess.run(command, shell=True, executable="/bin/bash")

    # Check if sampling.csv exists
    if not os.path.exists(output_csv_path):
        logging.error("REINVENT failed: sampling.csv not found.")
    else:
        logging.info(f"REINVENT sampling completed: {output_csv_path}")

    azure_result = upload_task_outputs(task_id, task_output_folder)

    return {
        "message": "REINVENT task completed",
        "task_id": task_id,
        "azure_files": azure_result.get("uploaded_files", []),
        "output_log": output_log
    }
