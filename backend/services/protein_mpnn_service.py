import subprocess
import os

PROTEINMPNN_SCRIPT = os.path.join(os.getcwd(), "tasks", "proteinmpnn", "predict.py")

def run_proteinmpnn(params):
    command = [
        "docker", "run",
        "-v", f"{os.getcwd()}/uploads:/workspace",
        "-v", f"{os.getcwd()}/outputs:/outputs",
        "--workdir", "/workspace",
        "ghcr.io/peptoneltd/proteinmpnn_ddg:1.0.0_base_cpu",
        "python3", "/app/proteinmpnn_ddg/predict.py",
        "--pdb_path", params["pdb_file"],
        "--chains", params["chain"],
        "--outpath", f"/outputs/{params['pdb_file']}_predictions.csv"
    ]

    try:
        process = subprocess.run(command, check=True, capture_output=True, text=True)
        return {"message": "ProteinMPNN executed", "stdout": process.stdout}

    except subprocess.CalledProcessError as e:
        return {"error": "ProteinMPNN failed", "details": str(e)}
