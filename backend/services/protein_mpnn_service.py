import subprocess
import os

PROTEINMPNN_SCRIPT = os.path.join(os.getcwd(), "tasks", "proteinmpnn", "predict.py")

def run_proteinmpnn(params):
    cmd = ["python3", PROTEINMPNN_SCRIPT, "--pdb", params["pdb_file"]]
    process = subprocess.run(cmd, capture_output=True, text=True)
    return {"output": process.stdout, "error": process.stderr}
