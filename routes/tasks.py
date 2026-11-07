from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.task_service import TaskService

task_bp = Blueprint('tasks', __name__)

@task_bp.route('/workspaces/<int:workspace_id>/tasks', methods=['POST'])
@jwt_required()
def create_task(workspace_id):
    current_user_id = int(get_jwt_identity())
    data = request.get_json()

    if not data or not data.get('title'):
        return jsonify({"success": False, "message": "Task title is required"}), 400

    task, error = TaskService.create_task(
        workspace_id=workspace_id,
        creator_id=current_user_id,
        title=data['title'],
        description=data.get('description', ''),
        priority=data.get('priority', 'Medium')
    )

    if error:
        return jsonify({"success": False, "message": error}), 403

    return jsonify({
        "success": True,
        "message": "Task created successfully",
        "data": {"id": task.id, "title": task.title, "status": task.status}
    }), 201

@task_bp.route('/workspaces/<int:workspace_id>/tasks', methods=['GET'])
@jwt_required()
def list_tasks(workspace_id):
    tasks = TaskService.get_workspace_tasks(workspace_id)
    task_list = [{
        "id": t.id, 
        "title": t.title, 
        "status": t.status, 
        "priority": t.priority
    } for t in tasks]

    return jsonify({
        "success": True,
        "message": "Tasks retrieved successfully",
        "data": task_list
    }), 200