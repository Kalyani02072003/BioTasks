import os
from flask import Blueprint, request, jsonify
from backend.services.thompson_sampling_service import run_thompson_sampling

ts_bp = Blueprint("thompson_sampling", __name__)
OUTPUT_FOLDER = "outputs/ts_output"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@ts_bp.route("/run_ts", methods=["POST"])
def run_ts():
    """Starts Thompson Sampling and returns a task ID."""
    data = request.get_json()

    required_params = ["reaction_smarts", "num_warmup_trials", "num_ts_iterations", "evaluator", "ts_mode"]
    for param in required_params:
        if param not in data:
            return jsonify({"error": f"Missing required parameter: {param}"}), 400

    if data["evaluator"] not in ["FPEvaluator", "MLClassifierEvaluator", "FredEvaluator", "ROCSEvaluator"]:
        return jsonify({"error": "Invalid evaluator selected"}), 400

    result = run_thompson_sampling(data)
    return jsonify(result)

@ts_bp.route("/check_status/<task_id>", methods=["GET"])
def check_status(task_id):
    """Check if Thompson Sampling has completed and return logs."""
    output_file = os.path.join(OUTPUT_FOLDER, f"{task_id}.csv")
    output_log = os.path.join(OUTPUT_FOLDER, f"{task_id}.log")

    if not os.path.exists(output_log):
        return jsonify({"error": "Task ID not found"}), 404

    with open(output_log, "r") as f:
        logs = f.readlines()

    return jsonify({
        "task_id": task_id,
        "output_file": output_file if os.path.exists(output_file) else "Still running",
        "logs": logs
    })
