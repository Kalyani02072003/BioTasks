import os
import subprocess
import uuid

LIGANDMPNN_SCRIPT = os.path.abspath("/home/kalyani/Kalyani/Internship/BioTasks/tasks/LigandMPNN/ligandmpnn/run.py")
OUTPUT_FOLDER = "ligandmpnn_output"
CONDA_ENV_NAME = "ligandmpnn_cpu"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def run_ligandmpnn(params):
    """Runs LigandMPNN in the background and returns a task ID."""
    pdb_file = params["pdb_file"]
    designed_chains = params["designed_chains"]
    fixed_residues = params["fixed_residues"]
    residues_to_design = params["residues_to_design"]
    temperature = params["temperature"]
    num_sequences = params["num_sequences"]

    task_id = str(uuid.uuid4())
    output_log = os.path.join(OUTPUT_FOLDER, f"{task_id}.log")

    # Prepare the command
    command = f"""
    source ~/miniconda3/etc/profile.d/conda.sh && conda activate {CONDA_ENV_NAME} &&
    python3 {LIGANDMPNN_SCRIPT} \
        --pdb_path {pdb_file} \
        --designed_chains "{designed_chains}" \
        --fixed_residues "{fixed_residues}" \
        --residues_to_design "{residues_to_design}" \
        --temperature {temperature} \
        --num_sequences {num_sequences} \
        > {output_log} 2>&1 &
    """

    subprocess.Popen(command, shell=True, executable="/bin/bash")

    return {
        "message": "LigandMPNN started",
        "task_id": task_id,
        "output_log": output_log
    }
