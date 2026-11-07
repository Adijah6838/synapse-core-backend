from werkzeug.security import generate_password_hash, check_password_hash
from models import db
from models.user import User

class AuthService:
    @staticmethod
    def register_user(username, email, password, role='Editor'):
        # 1. Check if user already exists
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            return None, "Username or email already exists"
        
        # 2. Hash the password (scramble it securely)
        hashed_password = generate_password_hash(password)
        
        # 3. Create the user and save to database
        new_user = User(username=username, email=email, password_hash=hashed_password, role=role)
        db.session.add(new_user)
        db.session.commit()
        
        return new_user, None

    @staticmethod
    def authenticate_user(username_or_email, password):
        # 1. Find the user by username or email
        user = User.query.filter((User.username == username_or_email) | (User.email == username_or_email)).first()
        
        if not user:
            return None, "User not found"
            
        # 2. Check if the provided password matches the scrambled hash
        if not check_password_hash(user.password_hash, password):
            return None, "Invalid password"
            
        return user, None