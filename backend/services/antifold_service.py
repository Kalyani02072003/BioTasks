import subprocess
import os

ANTIFOLD_SCRIPT = os.path.join(os.getcwd(), "tasks", "antifold", "main.py")

def run_antifold(params):
    cmd = ["python3", ANTIFOLD_SCRIPT, "--input", params["pdb_file"]]
    process = subprocess.run(cmd, capture_output=True, text=True)
    return {"output": process.stdout, "error": process.stderr}
