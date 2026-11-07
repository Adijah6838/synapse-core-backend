from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from services.auth_service import AuthService

# Create a Blueprint for authentication routes
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # Basic validation
    if not data or not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({"success": False, "message": "Missing required fields"}), 400
        
    user, error = AuthService.register_user(
        username=data['username'],
        email=data['email'],
        password=data['password'],
        role=data.get('role', 'Editor') # Default to Editor if not provided
    )
    
    if error:
        return jsonify({"success": False, "message": error}), 400
        
    return jsonify({
        "success": True, 
        "message": "User registered successfully",
        "data": {"user_id": user.id, "username": user.username}
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({"success": False, "message": "Missing username or password"}), 400
        
    user, error = AuthService.authenticate_user(data['username'], data['password'])
    
    if error:
        return jsonify({"success": False, "message": error}), 401
        
    # Generate the JWT Access Token
    # Note: JWT requires the identity to be a string in newer versions
    access_token = create_access_token(identity=str(user.id))
    
    return jsonify({
        "success": True,
        "message": "Login successful",
        "data": {
            "access_token": access_token,
            "user": {"id": user.id, "username": user.username, "role": user.role}
        }
    }), 200