import subprocess
import os
import uuid

PROTEINMPNN_SCRIPT = os.path.join(os.getcwd(), "tasks", "ProteinMPNN", "proteinmpnn", "predict.py")
OUTPUT_FOLDER = os.path.join(os.getcwd(), "proteinmpnn_output")  # Output folder

# Ensure the output directory exists
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def run_proteinmpnn(params):
    """Runs ProteinMPNN in the background and returns a task ID."""
    pdb_filename = os.path.basename(params["pdb_file"])

    # Generate unique task ID
    task_id = str(uuid.uuid4())
    log_path = os.path.join(OUTPUT_FOLDER, f"{task_id}.log")  # Log file
    output_path = os.path.join(OUTPUT_FOLDER, f"{pdb_filename}_predictions.csv")  # Prediction output file

    command = f"""
    docker run \
    -v {os.getcwd()}/uploads:/workspace \
    -v {OUTPUT_FOLDER}:/outputs \
    --workdir /workspace \
    ghcr.io/peptoneltd/proteinmpnn_ddg:1.0.0_base_cpu \
    python3 /app/proteinmpnn_ddg/predict.py \
    --pdb_path /workspace/{pdb_filename} \
    --chains {params["chain"]} \
    --outpath /outputs/{pdb_filename}_predictions.csv \
    > {log_path} 2>&1 &
    """

    # Run ProteinMPNN in the background
    subprocess.Popen(command, shell=True, executable="/bin/bash")

    return {
        "message": "ProteinMPNN started",
        "task_id": task_id,
        "log_file": log_path,
        "output_file": output_path
    }
