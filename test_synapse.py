import pytest
import json
from app import create_app
from models import db
from models.user import User
from models.workspace import Workspace
from models.document import Document
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:' # Use in-memory DB for tests

@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_header(client):
    # Helper fixture to register and login a user, returning the token
    client.post('/api/auth/register', json={
        "username": "testadmin", "email": "admin@test.com", "password": "password123", "role": "Administrator"
    })
    res = client.post('/api/auth/login', json={"username": "testadmin", "password": "password123"})
    token = res.get_json()['data']['access_token']
    return {'Authorization': f'Bearer {token}'}

# --- AUTHENTICATION TESTS ---

def test_register_user(client):
    res = client.post('/api/auth/register', json={"username": "u1", "email": "u1@test.com", "password": "p1"})
    assert res.status_code == 201
    assert res.get_json()['success'] is True

def test_register_duplicate_user(client):
    client.post('/api/auth/register', json={"username": "u1", "email": "u1@test.com", "password": "p1"})
    res = client.post('/api/auth/register', json={"username": "u1", "email": "u1@test.com", "password": "p1"})
    assert res.status_code == 400
    assert "already exists" in res.get_json()['message']

def test_login_success(client):
    client.post('/api/auth/register', json={"username": "u1", "email": "u1@test.com", "password": "p1"})
    res = client.post('/api/auth/login', json={"username": "u1", "password": "p1"})
    assert res.status_code == 200
    assert 'access_token' in res.get_json()['data']

def test_login_invalid_password(client):
    client.post('/api/auth/register', json={"username": "u1", "email": "u1@test.com", "password": "p1"})
    res = client.post('/api/auth/login', json={"username": "u1", "password": "wrong"})
    assert res.status_code == 401

def test_protected_route_without_token(client):
    res = client.get('/api/workspaces')
    assert res.status_code == 401 # Unauthorized

# --- WORKSPACE TESTS ---

def test_create_workspace(client, auth_header):
    res = client.post('/api/workspaces', headers=auth_header, json={"name": "Test WS"})
    assert res.status_code == 201
    assert res.get_json()['data']['name'] == "Test WS"

def test_get_workspaces(client, auth_header):
    client.post('/api/workspaces', headers=auth_header, json={"name": "Test WS"})
    res = client.get('/api/workspaces', headers=auth_header)
    assert res.status_code == 200
    assert len(res.get_json()['data']) == 1

# --- DOCUMENT & CONCURRENCY TESTS ---

def test_create_document(client, auth_header):
    client.post('/api/workspaces', headers=auth_header, json={"name": "WS"})
    res = client.post('/api/workspaces/1/documents', headers=auth_header, json={"title": "Doc 1", "content": "Hello"})
    assert res.status_code == 201
    assert res.get_json()['data']['lock_version'] == 1

def test_update_document_valid_version(client, auth_header):
    client.post('/api/workspaces', headers=auth_header, json={"name": "WS"})
    client.post('/api/workspaces/1/documents', headers=auth_header, json={"title": "Doc 1", "content": "Hello"})
    res = client.put('/api/documents/1', headers=auth_header, json={"content": "Updated", "lock_version": 1})
    assert res.status_code == 200
    assert res.get_json()['data']['lock_version'] == 2

def test_update_document_stale_version_conflict(client, auth_header):
    client.post('/api/workspaces', headers=auth_header, json={"name": "WS"})
    client.post('/api/workspaces/1/documents', headers=auth_header, json={"title": "Doc 1", "content": "Hello"})
    # Attempt update with lock_version 99
    res = client.put('/api/documents/1', headers=auth_header, json={"content": "Updated", "lock_version": 99})
    assert res.status_code == 409
    assert res.get_json()['error_code'] == "VERSION_CONFLICT"

def test_update_archived_document(client, auth_header):
    # Create workspace and doc
    client.post('/api/workspaces', headers=auth_header, json={"name": "WS"})
    client.post('/api/workspaces/1/documents', headers=auth_header, json={"title": "Doc 1", "content": "Hello"})
    
    # Force status to Archived directly in DB for test
    with client.application.app_context():
        doc = Document.query.get(1)
        doc.status = 'Archived'
        db.session.commit()
        
    res = client.put('/api/documents/1', headers=auth_header, json={"content": "Updated", "lock_version": 1})
    assert res.status_code == 400
    assert "archived" in res.get_json()['message']

# --- WORKFLOW TESTS ---

def test_workflow_valid_transition(client, auth_header):
    client.post('/api/workspaces', headers=auth_header, json={"name": "WS"})
    client.post('/api/workspaces/1/documents', headers=auth_header, json={"title": "Doc 1", "content": "Hello"})
    
    res = client.post('/api/documents/1/submit-review', headers=auth_header)
    assert res.status_code == 200
    assert res.get_json()['data']['status'] == "In Review"

def test_workflow_invalid_transition(client, auth_header):
    client.post('/api/workspaces', headers=auth_header, json={"name": "WS"})
    client.post('/api/workspaces/1/documents', headers=auth_header, json={"title": "Doc 1", "content": "Hello"})
    
    # Try to archive while still in Draft status
    res = client.post('/api/documents/1/archive', headers=auth_header)
    assert res.status_code == 400
    assert "Invalid transition" in res.get_json()['message']

# --- TASK TESTS ---

def test_create_task(client, auth_header):
    client.post('/api/workspaces', headers=auth_header, json={"name": "WS"})
    res = client.post('/api/workspaces/1/tasks', headers=auth_header, json={"title": "Task 1", "priority": "High"})
    assert res.status_code == 201
    assert res.get_json()['data']['title'] == "Task 1"

def test_get_tasks(client, auth_header):
    client.post('/api/workspaces', headers=auth_header, json={"name": "WS"})
    client.post('/api/workspaces/1/tasks', headers=auth_header, json={"title": "Task 1"})
    res = client.get('/api/workspaces/1/tasks', headers=auth_header)
    assert res.status_code == 200
    assert len(res.get_json()['data']) == 1