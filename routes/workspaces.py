from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.workspace_service import WorkspaceService

workspace_bp = Blueprint('workspaces', __name__)

@workspace_bp.route('', methods=['POST'])
@jwt_required()
def create_workspace():
    # Get the user ID from the JWT token
    current_user_id = int(get_jwt_identity())
    data = request.get_json()

    if not data or not data.get('name'):
        return jsonify({"success": False, "message": "Workspace name is required"}), 400

    workspace, error = WorkspaceService.create_workspace(
        owner_id=current_user_id,
        name=data['name'],
        description=data.get('description', ''),
        visibility=data.get('visibility', 'Private')
    )

    if error:
        return jsonify({"success": False, "message": error}), 400

    return jsonify({
        "success": True,
        "message": "Workspace created successfully",
        "data": {
            "id": workspace.id,
            "name": workspace.name,
            "owner_id": workspace.owner_id
        }
    }), 201

@workspace_bp.route('', methods=['GET'])
@jwt_required()
def list_workspaces():
    current_user_id = int(get_jwt_identity())
    
    workspaces = WorkspaceService.get_user_workspaces(current_user_id)
    
    workspace_list = []
    for ws in workspaces:
        workspace_list.append({
            "id": ws.id,
            "name": ws.name,
            "description": ws.description,
            "visibility": ws.visibility
        })

    return jsonify({
        "success": True,
        "message": "Workspaces retrieved successfully",
        "data": workspace_list
    }), 200