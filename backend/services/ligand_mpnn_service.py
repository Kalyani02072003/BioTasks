

import os
import subprocess
import uuid

LIGANDMPNN_SCRIPT = "/home/kalyani/Kalyani/Internship/BioTasks/tasks/LigandMPNN/run.py"
MODEL_CHECKPOINT = "/home/kalyani/Kalyani/Internship/BioTasks/tasks/LigandMPNN/model_params/proteinmpnn_v_48_020.pt"
WORKING_DIR = "/home/kalyani/Kalyani/Internship/BioTasks/tasks/LigandMPNN"
OUTPUT_FOLDER = "ligandmpnn_output"
CONDA_ENV = "ligandmpnn_env"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def run_ligandmpnn(params):
    """Runs LigandMPNN in the background and returns a task ID."""
    
    # Ensure absolute paths for inputs
    pdb_filename = os.path.basename(params["pdb_file"])
    input_pdb_path = os.path.abspath(params["pdb_file"])
    output_folder = os.path.abspath(OUTPUT_FOLDER)
    
    # Generate unique task ID
    task_id = str(uuid.uuid4())
    log_path = os.path.join(output_folder, f"{task_id}.log")
    
    # Construct command ensuring the correct working directory
    command = f"""
    source ~/miniconda3/etc/profile.d/conda.sh &&
    conda activate {CONDA_ENV} &&
    cd {WORKING_DIR} &&
    python3 {LIGANDMPNN_SCRIPT} \
        --pdb_path "{input_pdb_path}" \
        --checkpoint_path "{MODEL_CHECKPOINT}" \
        --out_folder "{output_folder}" \
        --chains_to_design {params["chains_to_design"]} \
        {f'--redesigned_residues {params.get("residues_to_design")}' if params.get("residues_to_design") else ""} \
        --temperature {params["temperature"]} \
        --number_of_batches {params["number_of_batches"]} \
        > {log_path} 2>&1 &
    """

    
    # Run LigandMPNN in the background
    subprocess.Popen(command, shell=True, executable="/bin/bash")

    return {
        "message": "LigandMPNN started",
        "task_id": task_id,
        "log_file": log_path,
        "output_folder": output_folder
    }
