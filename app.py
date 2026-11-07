from flask import Flask, jsonify, render_template
from config import Config
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from models import db

migrate = Migrate()
jwt = JWTManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # Frontend Page Routes
    @app.route('/')
    def index():
        return render_template('login.html')

    @app.route('/dashboard')
    def dashboard():
        return render_template('dashboard.html')

    @app.route('/documents/1')
    def document_editor():
        return render_template('document.html')

    @app.route('/tasks')
    def tasks_page():
        return render_template('tasks.html')

    # Health Check
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({"success": True, "message": "SYNAPSE API is running"}), 200

    # Register API Blueprints
    from routes.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    
    from routes.workspaces import workspace_bp
    app.register_blueprint(workspace_bp, url_prefix='/api/workspaces')

    from routes.documents import document_bp
    app.register_blueprint(document_bp, url_prefix='/api')

    from routes.analytics import analytics_bp
    app.register_blueprint(analytics_bp, url_prefix='/api/analytics')

    from routes.tasks import task_bp
    app.register_blueprint(task_bp, url_prefix='/api')

    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5001, debug=True)