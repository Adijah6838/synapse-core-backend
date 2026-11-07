from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from services.analytics_service import AnalyticsService

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/overview', methods=['GET'])
@jwt_required()
def get_overview():
    data = AnalyticsService.get_overview()
    return jsonify({
        "success": True,
        "message": "Analytics retrieved successfully",
        "data": data
    }), 200