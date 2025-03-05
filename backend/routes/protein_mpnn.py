from flask import Blueprint, request, jsonify
from services.protein_mpnn_service import run_proteinmpnn

proteinmpnn_bp = Blueprint("proteinmpnn", __name__)

@proteinmpnn_bp.route("/ddg", methods=["POST"])
def ddg():
    data = request.json
    result = run_proteinmpnn(data)
    return jsonify(result)
