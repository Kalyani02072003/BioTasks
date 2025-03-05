from flask import Blueprint, request, jsonify
from services.antifold_service import run_antifold

antifold_bp = Blueprint("antifold", __name__)

@antifold_bp.route("/predict", methods=["POST"])
def predict():
    data = request.json
    result = run_antifold(data)
    return jsonify(result)
