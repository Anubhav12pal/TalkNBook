import json
import os
import uuid
from datetime import datetime, timedelta
from typing import Optional

from fastapi import HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext

from models.user import UserCreate, UserLogin, UserResponse


class AuthService:
    """Service for handling authentication operations."""
    
    SECRET_KEY = "your-secret-key-change-in-production"
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.db_path = os.path.join(os.path.dirname(__file__), "../data/users.json")
        self._ensure_db_exists()
    
    def _ensure_db_exists(self):
        """Ensure the users database file exists."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        if not os.path.exists(self.db_path):
            with open(self.db_path, 'w') as f:
                json.dump([], f)
    
    def _load_users(self) -> list:
        """Load users from JSON file."""
        try:
            with open(self.db_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_users(self, users: list):
        """Save users to JSON file."""
        with open(self.db_path, 'w') as f:
            json.dump(users, f, indent=2, default=str)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Hash a password."""
        return self.pwd_context.hash(password)
    
    def get_user_by_email(self, email: str) -> Optional[dict]:
        """Get user by email from database."""
        users = self._load_users()
        for user in users:
            if user["email"] == email:
                return user
        return None
    
    def get_user_by_username(self, username: str) -> Optional[dict]:
        """Get user by username from database."""
        users = self._load_users()
        for user in users:
            if user["username"] == username:
                return user
        return None
    
    def create_user(self, user_data: UserCreate) -> UserResponse:
        """Create a new user."""
        users = self._load_users()
        
        # Check if user already exists
        if self.get_user_by_email(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        if self.get_user_by_username(user_data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        
        # Create new user
        user_id = str(uuid.uuid4())
        hashed_password = self.get_password_hash(user_data.password)
        
        new_user = {
            "id": user_id,
            "username": user_data.username,
            "email": user_data.email,
            "hashed_password": hashed_password,
            "created_at": datetime.utcnow().isoformat()
        }
        
        users.append(new_user)
        self._save_users(users)
        
        return UserResponse(
            id=user_id,
            username=user_data.username,
            email=user_data.email,
            created_at=datetime.utcnow()
        )
    
    def authenticate_user(self, email: str, password: str) -> Optional[dict]:
        """Authenticate a user with email and password."""
        user = self.get_user_by_email(email)
        if not user:
            return None
        if not self.verify_password(password, user["hashed_password"]):
            return None
        return user
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        """Create a JWT access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[str]:
        """Verify a JWT token and return the user email."""
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            email: str = payload.get("sub")
            if email is None:
                return None
            return email
        except JWTError:
            return None