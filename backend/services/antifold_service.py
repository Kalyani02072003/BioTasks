import os
import subprocess
import uuid

ANTIFOLD_SCRIPT = os.path.abspath("/home/texsols/BioTasks/tasks/AntiFold/antifold/main.py")
OUTPUT_FOLDER = "antifold_output"
CONDA_ENV_NAME = "antifold_cpu"

def extract_chain_ids(pdb_file):
    """Extract unique chain IDs from a PDB file."""
    with open(pdb_file, "r") as f:
        chains = set(line.split()[4] for line in f if line.startswith("ATOM"))
    return list(chains)

def run_antifold(params):
    """Runs AntiFold in the background and returns a task ID."""
    pdb_file = params["pdb_file"]

    # Validate chain IDs
    valid_chains = extract_chain_ids(pdb_file)
    if params["heavy_chain"] not in valid_chains or params["light_chain"] not in valid_chains:
        return {
            "error": "Invalid chain ID",
            "valid_chains": valid_chains,
            "message": f"Your PDB file contains: {', '.join(valid_chains)}. Update your request with correct chains."
        }

    # Generate unique task ID for tracking
    task_id = str(uuid.uuid4())
    output_log = os.path.join(OUTPUT_FOLDER, f"{task_id}.log")

    # Prepare the command
    command = f"""
    source ~/miniconda3/etc/profile.d/conda.sh && conda activate {CONDA_ENV_NAME} &&
    python3 {ANTIFOLD_SCRIPT} \
        --num_seq_per_target {params.get("num_seq_per_target", 10)} \
        --sampling_temp {params.get("sampling_temp", 0.2)} \
        --regions "{','.join(params.get('regions', ['CDR1', 'CDR2', 'CDR3']))}" \
        --pdb_file {pdb_file} \
        --heavy_chain {params["heavy_chain"]} \
        --light_chain {params["light_chain"]} \
        > {output_log} 2>&1 &
    """

    # Run AntiFold in background
    subprocess.Popen(command, shell=True, executable="/bin/bash")

    return {
        "message": "AntiFold started",
        "task_id": task_id,
        "output_log": output_log
    }
