import json
import uuid
from typing import Optional, Dict, Any
from pathlib import Path

from models.user import UserCreate


class PhoneAuthService:
    """Service for managing phone-based authentication for voice calls."""
    
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent / "data"
        self.phone_users_file = self.data_dir / "phone_users.json"
        self._ensure_data_file()
    
    def _ensure_data_file(self):
        """Ensure the phone users data file exists."""
        if not self.phone_users_file.exists():
            with open(self.phone_users_file, 'w') as f:
                json.dump({}, f)
    
    def _load_phone_users(self) -> Dict[str, Any]:
        """Load phone users from JSON file."""
        try:
            with open(self.phone_users_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_phone_users(self, phone_users: Dict[str, Any]):
        """Save phone users to JSON file."""
        with open(self.phone_users_file, 'w') as f:
            json.dump(phone_users, f, indent=2, default=str)
    
    def link_phone_to_user(self, phone_number: str, user_id: str) -> bool:
        """
        Link a phone number to an existing user account.
        
        Args:
            phone_number: The phone number to link
            user_id: The existing user ID
            
        Returns:
            True if linked successfully, False if phone already linked
        """
        phone_users = self._load_phone_users()
        
        # Normalize phone number (remove spaces, dashes, etc.)
        normalized_phone = self._normalize_phone_number(phone_number)
        
        # Check if phone is already linked
        if normalized_phone in phone_users:
            return False
        
        phone_users[normalized_phone] = {
            "user_id": user_id,
            "phone_number": phone_number,
            "verified": True,  # For now, assume verification is done
            "linked_at": str(uuid.uuid4())  # Using UUID as timestamp placeholder
        }
        
        self._save_phone_users(phone_users)
        return True
    
    def get_user_by_phone(self, phone_number: str) -> Optional[str]:
        """
        Get user ID by phone number.
        
        Args:
            phone_number: The phone number to look up
            
        Returns:
            User ID if found, None otherwise
        """
        phone_users = self._load_phone_users()
        normalized_phone = self._normalize_phone_number(phone_number)
        
        if normalized_phone in phone_users:
            return phone_users[normalized_phone]["user_id"]
        
        return None
    
    def create_phone_user(self, phone_number: str, name: str) -> str:
        """
        Create a new user account linked to a phone number.
        
        Args:
            phone_number: The phone number
            name: User's name
            
        Returns:
            The new user ID
        """
        phone_users = self._load_phone_users()
        normalized_phone = self._normalize_phone_number(phone_number)
        
        # Check if phone is already registered
        if normalized_phone in phone_users:
            return phone_users[normalized_phone]["user_id"]
        
        # Create new user ID
        user_id = str(uuid.uuid4())
        
        phone_users[normalized_phone] = {
            "user_id": user_id,
            "phone_number": phone_number,
            "name": name,
            "verified": True,
            "created_at": str(uuid.uuid4())  # Using UUID as timestamp placeholder
        }
        
        self._save_phone_users(phone_users)
        return user_id
    
    def _normalize_phone_number(self, phone_number: str) -> str:
        """
        Normalize phone number by removing non-digits and formatting.
        
        Args:
            phone_number: Raw phone number
            
        Returns:
            Normalized phone number
        """
        # Remove all non-digit characters
        digits_only = ''.join(char for char in phone_number if char.isdigit())
        
        # If it starts with 1 and is 11 digits, it's likely US format
        if len(digits_only) == 11 and digits_only.startswith('1'):
            return digits_only
        
        # If it's 10 digits, assume US format and add country code
        if len(digits_only) == 10:
            return '1' + digits_only
        
        return digits_only
    
    def is_phone_registered(self, phone_number: str) -> bool:
        """
        Check if a phone number is already registered.
        
        Args:
            phone_number: The phone number to check
            
        Returns:
            True if registered, False otherwise
        """
        normalized_phone = self._normalize_phone_number(phone_number)
        phone_users = self._load_phone_users()
        return normalized_phone in phone_users