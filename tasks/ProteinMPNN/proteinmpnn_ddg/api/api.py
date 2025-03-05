import os
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
import subprocess

app = Flask(__name__)

# Configure upload and output directories
UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Allowed file types
ALLOWED_EXTENSIONS = {"pdb"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS



@app.route("/predict", methods=["POST"])
def predict():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    chain = request.form.get("chain", "A")

    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        # Ensure the output directory exists
        os.makedirs(OUTPUT_FOLDER, exist_ok=True)

        output_csv = os.path.join(OUTPUT_FOLDER, f"{filename}_predictions.csv")

        # Run the ProteinMPNN-ddG Docker command
        command = [
            "docker", "run",
            "-v", f"{os.getcwd()}/uploads:/workspace",
            "-v", f"{os.getcwd()}/outputs:/outputs",  # Ensure outputs are mapped
            "--workdir", "/workspace",
            "ghcr.io/peptoneltd/proteinmpnn_ddg:1.0.0_base_cpu",
            "python3", "/app/proteinmpnn_ddg/predict.py",
            "--pdb_path", filename,
            "--chains", chain,
            "--outpath", f"/outputs/{filename}_predictions.csv"  # Use absolute path
        ]

        subprocess.run(command, check=True)

        return jsonify({"message": "Prediction complete!", "output": output_csv})

    return jsonify({"error": "Invalid file format"}), 400

if __name__ == "__main__":
    app.run(debug=True)
