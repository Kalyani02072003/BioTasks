import os
import subprocess
import logging
import glob
import shutil
from backend.database.azure_upload import upload_task_outputs  # Azure upload function

# Paths and Constants
ANTIFOLD_SCRIPT = "/home/texsols/BioTasks/tasks/AntiFold/antifold/main.py"
OUTPUT_FOLDER = "/home/texsols/BioTasks/outputs/antifold_output"  # Main output directory
UPLOAD_FOLDER = "/home/texsols/BioTasks/uploads"
CONDA_ENV_NAME = "antifold_cpu"
ANTIFOLD_WORKING_DIR = "/home/texsols/BioTasks/tasks/AntiFold"

# Ensure output directory exists
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def extract_chain_ids(pdb_file):
    """Extract unique chain IDs from a PDB file."""
    with open(pdb_file, "r") as f:
        chains = set(line.split()[4] for line in f if line.startswith("ATOM"))
    return list(chains)


def move_antifold_outputs(task_id):
    """Moves AntiFold output files (CSV, FASTA, LOG) into the correct task folder."""
    task_output_folder = os.path.join(OUTPUT_FOLDER, task_id)  # Create task-specific folder
    os.makedirs(task_output_folder, exist_ok=True)  # Ensure the task folder exists
    misplaced_files = glob.glob(os.path.join(OUTPUT_FOLDER, "*.*"))  # Find all misplaced files

    for file_path in misplaced_files:
        if task_id in file_path:  # Ensure it's part of the current task
            correct_path = os.path.join(task_output_folder, os.path.basename(file_path))
            shutil.move(file_path, correct_path)
            logging.info(f"Moved {file_path} → {correct_path}")


def run_antifold(params):
    """Runs AntiFold, moves misplaced output files, and uploads them to Azure."""
    
    task_id = params["task_id"]
    task_output_folder = os.path.join(OUTPUT_FOLDER, task_id)
    os.makedirs(task_output_folder, exist_ok=True)  # Ensure output folder exists

    output_log = os.path.join(task_output_folder, f"{task_id}.log")
    json_path = os.path.join(task_output_folder, f"{task_id}.json")

    # Validate chain IDs
    valid_chains = extract_chain_ids(params["pdb_file"])
    if params["heavy_chain"] not in valid_chains or params["light_chain"] not in valid_chains:
        return {
            "error": "Invalid chain ID",
            "valid_chains": valid_chains,
            "message": f"Your PDB file contains: {', '.join(valid_chains)}. Update your request with correct chains."
        }

    # Prepare the JSON config file
    json_config = {
        "num_seq_per_target": params.get("num_seq_per_target", 10),
        "sampling_temp": params.get("sampling_temp", 0.2),
        "regions": params.get("regions", ["CDR1", "CDR2", "CDR3"]),
        "pdb_file": params["pdb_file"],
        "heavy_chain": params["heavy_chain"],
        "light_chain": params["light_chain"],
        "log_filename": output_log,
        "results_filename": os.path.join(task_output_folder, f"{task_id}.csv")
    }

    # Save the config JSON file
    with open(json_path, "w") as f:
        json.dump(json_config, f, indent=4)

    # Construct the execution command
    command = f"""
    source ~/miniconda3/etc/profile.d/conda.sh &&
    conda activate {CONDA_ENV_NAME} &&
    python3 {ANTIFOLD_SCRIPT} --config_file {json_path} > "{output_log}" 2>&1
    """

    logging.info(f"Executing AntiFold command:\n{command}")
    subprocess.run(command, shell=True, executable="/bin/bash", cwd=ANTIFOLD_WORKING_DIR)

    move_antifold_outputs(task_id)  # Move the generated outputs to task-specific folder

    azure_result = upload_task_outputs(task_id, task_output_folder)

    return {
        "message": "AntiFold processing completed",
        "task_id": task_id,
        "azure_files": azure_result.get("uploaded_files", []),
        "output_log": azure_result.get("uploaded_files", [])[0] if azure_result.get("uploaded_files") else None
    }
