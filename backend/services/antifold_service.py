import os
import subprocess
import logging
import uuid
from backend.database.azure_upload import upload_task_outputs  # Azure upload function

# Paths and Constants
ANTIFOLD_SCRIPT = os.path.abspath("/home/texsols/BioTasks/tasks/AntiFold/antifold/main.py")
OUTPUT_FOLDER = os.path.abspath("/home/texsols/BioTasks/outputs/antifold_output")
UPLOAD_FOLDER = os.path.abspath("/home/texsols/BioTasks/uploads")
CONDA_ENV_NAME = "antifold_cpu"

# Ensure output directory exists
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def extract_chain_ids(pdb_file):
    """Extract unique chain IDs from a PDB file."""
    with open(pdb_file, "r") as f:
        chains = set(line.split()[4] for line in f if line.startswith("ATOM"))
    return list(chains)


import glob  # Add this import to find the misplaced FASTA file

import glob  # Import to find misplaced FASTA files

def run_antifold(params):
    """Runs AntiFold, moves misplaced output files, and uploads them to Azure."""
    task_id = params["task_id"]
    task_output_folder = os.path.join(OUTPUT_FOLDER, task_id)
    os.makedirs(task_output_folder, exist_ok=True)  # Ensure output folder exists
    output_log = os.path.join(task_output_folder, f"{task_id}.log")

    # Validate chain IDs
    valid_chains = extract_chain_ids(params["pdb_file"])
    if params["heavy_chain"] not in valid_chains or params["light_chain"] not in valid_chains:
        return {
            "error": "Invalid chain ID",
            "valid_chains": valid_chains,
            "message": f"Your PDB file contains: {', '.join(valid_chains)}. Update your request with correct chains."
        }

    # Construct command
    command = f"""
    source ~/miniconda3/etc/profile.d/conda.sh &&
    conda activate {CONDA_ENV_NAME} &&
    python3 {ANTIFOLD_SCRIPT} \
        --num_seq_per_target {params.get("num_seq_per_target", 10)} \
        --sampling_temp {params.get("sampling_temp", 0.2)} \
        --regions "{','.join(params.get('regions', ['CDR1', 'CDR2', 'CDR3']))}" \
        --pdb_file "{params['pdb_file']}" \
        --heavy_chain "{params['heavy_chain']}" \
        --light_chain "{params['light_chain']}" \
        > "{output_log}" 2>&1
    """

    logging.info(f"Executing AntiFold command:\n{command}")
    subprocess.run(command, shell=True, executable="/bin/bash")

    # Move misplaced FASTA file to the correct task folder
    misplaced_fasta = glob.glob(os.path.join(OUTPUT_FOLDER, "*.fasta"))  # Find FASTA files in the main directory
    for fasta_file in misplaced_fasta:
        correct_fasta_path = os.path.join(task_output_folder, os.path.basename(fasta_file))
        os.rename(fasta_file, correct_fasta_path)  # Move FASTA file
        logging.info(f"Moved {fasta_file} to {correct_fasta_path}")

    # Move log file to task folder (if not already there)
    if os.path.exists(output_log):
        correct_log_path = os.path.join(task_output_folder, f"{task_id}.log")
        os.rename(output_log, correct_log_path)
        logging.info(f"Moved log file to {correct_log_path}")

    # Upload task outputs to Azure
    azure_result = upload_task_outputs(task_id, task_output_folder)

    return {
        "message": "AntiFold processing completed",
        "task_id": task_id,
        "azure_files": azure_result.get("uploaded_files", []),
        "output_log": azure_result.get("uploaded_files", [])[0] if azure_result.get("uploaded_files") else None
    }
