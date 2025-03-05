


from flask import Flask, request, jsonify, send_from_directory, send_file
import os
import subprocess
import zipfile

app = Flask(__name__)

# Define directory paths
BASE_DIR = os.path.abspath(os.path.join(os.getcwd(), ".."))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")  
OUTPUT_FOLDER = os.path.join(BASE_DIR, "antifold_output")
ANTIFOLD_SCRIPT = os.path.join(BASE_DIR, "antifold/main.py")

# Ensure required directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def run_antifold(task_type, pdb_file=None, heavy_chain=None, light_chain=None, nanobody_chain=None, antigen_chain=None, num_seq_per_target=10, temp=0.2, regions=None):
    """Run AntiFold with user-defined parameters."""
    if task_type not in ["antibody", "monobody"]:
        return {"error": "Invalid task type. Choose 'antibody' or 'monobody'."}, 400

    if regions is None:
        regions = ["CDR1", "CDR2", "CDR3"]

    command = [
        "python", ANTIFOLD_SCRIPT,
        "--num_seq_per_target", str(num_seq_per_target),
        "--sampling_temp", str(temp),
        "--regions", " ".join(regions),
        "--pdb_file", pdb_file
    ]

    # Antibody Mode (VH/VL paired)
    if task_type == "antibody":
        if not heavy_chain or not light_chain:
            return {"error": "Heavy and light chains are required for antibodies."}, 400
        command.extend(["--heavy_chain", heavy_chain, "--light_chain", light_chain])

        if antigen_chain:
            command.extend(["--antigen_chain", antigen_chain])  # Optional antigen chain

    # Monobody Mode (Single-chain nanobody)
    elif task_type == "monobody":
        if not nanobody_chain:
            return {"error": "Nanobody chain ID is required for monobody."}, 400
        command.extend(["--nanobody_chain", nanobody_chain])

    print("Running command:", " ".join(command))

    try:
        subprocess.run(command, check=True)
        return {"message": "AntiFold run successfully.", "output_files": output_files}

    except subprocess.CalledProcessError as e:
        return {"error": "AntiFold failed", "details": str(e)}, 500


@app.route('/antifold', methods=['POST'])
def run():
    """Run AntiFold endpoint"""
    task_type = request.form.get("task_type")  # 'antibody' or 'monobody'
    pdb_file = request.files.get("pdb_file")
    heavy_chain = request.form.get("heavy_chain")
    light_chain = request.form.get("light_chain")
    nanobody_chain = request.form.get("nanobody_chain")
    antigen_chain = request.form.get("antigen_chain")
    num_seq_per_target = request.form.get("num_seq_per_target", 10, type=int)
    temp = request.form.get("sampling_temp", 0.2, type=float)
    regions = request.form.getlist("regions") or ["CDR1", "CDR2", "CDR3"]

    # Handle PDB file upload
    filepath = None
    if pdb_file:
        filepath = os.path.join(UPLOAD_FOLDER, pdb_file.filename)
        pdb_file.save(filepath)

    # Run AntiFold
    result, status_code = run_antifold(task_type, filepath, heavy_chain, light_chain, nanobody_chain, antigen_chain, num_seq_per_target, temp, regions)
    return jsonify(result), status_code


@app.route("/download/<filename>", methods=['GET'])
def download(filename):
    """Download a single output file"""
    return send_from_directory(OUTPUT_FOLDER, filename, as_attachment=True)


@app.route("/download_zip", methods=['GET'])
def download_zip():
    """Compress `antifold_output` folder into a ZIP and send it"""
    zip_filename = "antifold_output.zip"
    zip_path = os.path.join(BASE_DIR, zip_filename)

    if os.path.exists(zip_path):
        os.remove(zip_path)

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(OUTPUT_FOLDER):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, OUTPUT_FOLDER)
                zipf.write(file_path, arcname)

    return send_file(zip_path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)


