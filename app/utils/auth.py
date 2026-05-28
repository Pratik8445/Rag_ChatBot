"""Authentication utilities for the RAG chatbot"""
from typing import Dict, Optional, Tuple
import hashlib
import os

def hash_password(password: str) -> str:
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()


class UserManager:
    """Manages user authentication and roles"""

    def __init__(self, users_dict: Optional[Dict[str, Dict[str, str]]] = None):
        """
        Initialize UserManager with user database

        Args:
            users_dict: Dictionary mapping usernames to {"password": "...", "role": "..."}
                       Passwords can be plain text (will be hashed) or already hashed
        """
        self.users = {}
        if users_dict:
            for username, user_data in users_dict.items():
                password = user_data.get("password", "")
                # Hash password if it's not already hashed (SHA256 hashes are 64 hex characters)
                if not (len(password) == 64 and all(c in '0123456789abcdef' for c in password)):
                    password = hash_password(password)
                self.users[username] = {
                    "password": password,
                    "role": user_data.get("role", "user")
                }

    def authenticate(self, username: str, password: str) -> Tuple[bool, Optional[str]]:
        """
        Authenticate user credentials

        Returns:
            (success: bool, role: Optional[str]) - Returns (True, role) if successful, (False, None) otherwise
        """
        user = self.users.get(username)
        if not user:
            return False, None

        # Hash the provided password and compare
        password_hash = hash_password(password)
        if password_hash == user["password"]:
            return True, user["role"]
        return False, None

    def add_user(self, username: str, password: str, role: str) -> bool:
        """Add a new user to the database"""
        if username in self.users:
            return False  # User already exists
        self.users[username] = {
            "password": hash_password(password),
            "role": role
        }
        return True

    def update_user_role(self, username: str, role: str) -> bool:
        """Update a user's role"""
        if username not in self.users:
            return False
        self.users[username]["role"] = role
        return True

    def list_users(self) -> Dict[str, str]:
        """List all users and their roles (passwords excluded)"""
        return {username: user["role"] for username, user in self.users.items()}


# Default test users for development
DEFAULT_USERS = {
    "Tony": {"password": "password123", "role": "engineering"},
    "Bruce": {"password": "securepass", "role": "marketing"},
    "Sam": {"password": "financepass", "role": "finance"},
    "Peter": {"password": "pete123", "role": "engineering"},
    "Sid": {"password": "sidpass123", "role": "marketing"},
    "Natasha": {"password": "hrpass123", "role": "hr"}
}


def get_user_manager() -> UserManager:
    """
    Factory function to get UserManager instance
    In the future, this can be extended to load from database or environment
    """
    # TODO: Add support for loading from database or external auth service
    return UserManager(DEFAULT_USERS)
