from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.document_service import DocumentService
from models.document import Document

document_bp = Blueprint('documents', __name__)

@document_bp.route('/workspaces/<int:workspace_id>/documents', methods=['POST'])
@jwt_required()
def create_document(workspace_id):
    current_user_id = int(get_jwt_identity())
    data = request.get_json()

    if not data or not data.get('title'):
        return jsonify({"success": False, "message": "Document title is required"}), 400

    doc, error = DocumentService.create_document(
        workspace_id=workspace_id,
        owner_id=current_user_id,
        title=data['title'],
        content=data.get('content', '')
    )

    if error:
        return jsonify({"success": False, "message": error}), 403

    return jsonify({
        "success": True,
        "message": "Document created successfully",
        "data": {
            "id": doc.id,
            "title": doc.title,
            "current_version": doc.current_version,
            "lock_version": doc.lock_version
        }
    }), 201

@document_bp.route('/documents/<int:document_id>', methods=['GET'])
@jwt_required()
def get_document(document_id):
    doc = Document.query.get(document_id)
    if not doc:
        return jsonify({"success": False, "message": "Document not found"}), 404

    return jsonify({
        "success": True,
        "data": {
            "id": doc.id,
            "title": doc.title,
            "content": doc.content,
            "current_version": doc.current_version,
            "lock_version": doc.lock_version,
            "status": doc.status
        }
    }), 200

@document_bp.route('/documents/<int:document_id>', methods=['PUT'])
@jwt_required()
def update_document(document_id):
    current_user_id = int(get_jwt_identity())
    data = request.get_json()

    if not data or 'content' not in data or 'lock_version' not in data:
        return jsonify({"success": False, "message": "Missing content or lock_version"}), 400

    doc, error = DocumentService.update_document(
        document_id=document_id,
        user_id=current_user_id,
        new_content=data['content'],
        expected_lock_version=data['lock_version'],
        change_summary=data.get('change_summary', 'Updated content')
    )

    # If there is an error, we check if it's a version conflict
    if error:
        if "Version conflict" in error:
            return jsonify({
                "success": False, 
                "message": error,
                "error_code": "VERSION_CONFLICT"
            }), 409 # 409 is the standard HTTP status code for Conflict
            
        return jsonify({"success": False, "message": error}), 400

    return jsonify({
        "success": True,
        "message": "Document updated successfully",
        "data": {
            "id": doc.id,
            "current_version": doc.current_version,
            "lock_version": doc.lock_version
        }
    }), 200
from services.workflow_engine import WorkflowEngine

@document_bp.route('/documents/<int:document_id>/submit-review', methods=['POST'])
@jwt_required()
def submit_review(document_id):
    current_user_id = int(get_jwt_identity())
    doc, error = WorkflowEngine.transition_document(document_id, current_user_id, 'submit_review')
    if error:
        return jsonify({"success": False, "message": error}), 400
    return jsonify({"success": True, "message": "Document submitted for review", "data": {"status": doc.status}}), 200

@document_bp.route('/documents/<int:document_id>/approve', methods=['POST'])
@jwt_required()
def approve_document(document_id):
    current_user_id = int(get_jwt_identity())
    doc, error = WorkflowEngine.transition_document(document_id, current_user_id, 'approve')
    if error:
        return jsonify({"success": False, "message": error}), 403
    return jsonify({"success": True, "message": "Document approved", "data": {"status": doc.status}}), 200

@document_bp.route('/documents/<int:document_id>/return-to-draft', methods=['POST'])
@jwt_required()
def return_to_draft(document_id):
    current_user_id = int(get_jwt_identity())
    doc, error = WorkflowEngine.transition_document(document_id, current_user_id, 'return_to_draft')
    if error:
        return jsonify({"success": False, "message": error}), 400
    return jsonify({"success": True, "message": "Document returned to draft", "data": {"status": doc.status}}), 200

@document_bp.route('/documents/<int:document_id>/archive', methods=['POST'])
@jwt_required()
def archive_document(document_id):
    current_user_id = int(get_jwt_identity())
    doc, error = WorkflowEngine.transition_document(document_id, current_user_id, 'archive')
    if error:
        return jsonify({"success": False, "message": error}), 400
    return jsonify({"success": True, "message": "Document archived", "data": {"status": doc.status}}), 200