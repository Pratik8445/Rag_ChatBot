"""Integration tests for the RAG chatbot API endpoints"""
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import app, user_manager

# Test client
client = TestClient(app)

# Test users
TEST_USERS = {
    "engineering": ("Tony", "password123"),
    "marketing": ("Bruce", "securepass"),
    "finance": ("Sam", "financepass"),
    "hr": ("Natasha", "hrpass123")
}


class TestAuthentication:
    """Test authentication endpoints"""

    def test_login_valid_credentials(self):
        """Test login with valid credentials"""
        username, password = TEST_USERS["engineering"]
        response = client.get("/login", auth=(username, password))
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == f"Welcome {username}!"
        assert data["role"] == "engineering"

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        response = client.get("/login", auth=("InvalidUser", "wrongpass"))
        assert response.status_code == 401

    def test_login_missing_credentials(self):
        """Test login without credentials"""
        response = client.get("/login")
        assert response.status_code == 401

    def test_multiple_users_login(self):
        """Test login for multiple users"""
        for role, (username, password) in TEST_USERS.items():
            response = client.get("/login", auth=(username, password))
            assert response.status_code == 200
            data = response.json()
            assert data["role"] == role


class TestChatEndpoint:
    """Test chat endpoint"""

    def test_chat_valid_message(self):
        """Test chat with valid message"""
        username, password = TEST_USERS["engineering"]
        payload = {"message": "What projects are active?"}
        response = client.post("/chat", json=payload, auth=(username, password))
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert data["user"] == username
        assert data["role"] == "engineering"
        assert data["message"] == payload["message"]

    def test_chat_unauthorized(self):
        """Test chat without authentication"""
        payload = {"message": "What projects are active?"}
        response = client.post("/chat", json=payload)
        assert response.status_code == 401

    def test_chat_role_based_access(self):
        """Test that different roles get appropriate responses"""
        # Test engineering access
        username, password = TEST_USERS["engineering"]
        payload = {"message": "Tell me about the engineering team"}
        response = client.post("/chat", json=payload, auth=(username, password))
        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "engineering"

        # Test finance access
        username, password = TEST_USERS["finance"]
        payload = {"message": "What are the quarterly results?"}
        response = client.post("/chat", json=payload, auth=(username, password))
        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "finance"

    def test_chat_response_structure(self):
        """Test that chat response has all required fields"""
        username, password = TEST_USERS["engineering"]
        payload = {"message": "Test query"}
        response = client.post("/chat", json=payload, auth=(username, password))
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields
        required_fields = ["user", "role", "message", "response", "sources", "confidence"]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"


class TestTestEndpoint:
    """Test the /test endpoint"""

    def test_test_endpoint_authorized(self):
        """Test /test endpoint with valid auth"""
        username, password = TEST_USERS["engineering"]
        response = client.get("/test", auth=(username, password))
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert username in data["message"]

    def test_test_endpoint_unauthorized(self):
        """Test /test endpoint without auth"""
        response = client.get("/test")
        assert response.status_code == 401


class TestUserManager:
    """Test the UserManager class"""

    def test_user_authentication(self):
        """Test user authentication through UserManager"""
        is_valid, role = user_manager.authenticate("Tony", "password123")
        assert is_valid is True
        assert role == "engineering"

    def test_invalid_password(self):
        """Test authentication with invalid password"""
        is_valid, role = user_manager.authenticate("Tony", "wrongpassword")
        assert is_valid is False
        assert role is None

    def test_nonexistent_user(self):
        """Test authentication for non-existent user"""
        is_valid, role = user_manager.authenticate("NonExistent", "password")
        assert is_valid is False
        assert role is None

    def test_add_user(self):
        """Test adding a new user"""
        success = user_manager.add_user("TestUser", "testpass", "engineering")
        assert success is True
        
        # Verify the user can authenticate
        is_valid, role = user_manager.authenticate("TestUser", "testpass")
        assert is_valid is True
        assert role == "engineering"

    def test_add_duplicate_user(self):
        """Test adding a duplicate user returns False"""
        user_manager.add_user("DuplicateTest", "pass", "hr")
        success = user_manager.add_user("DuplicateTest", "newpass", "finance")
        assert success is False


class TestEndpointIntegration:
    """Integration tests for multiple endpoints"""

    def test_full_workflow(self):
        """Test complete workflow: login -> chat"""
        username, password = TEST_USERS["engineering"]
        
        # Step 1: Login
        login_response = client.get("/login", auth=(username, password))
        assert login_response.status_code == 200
        
        # Step 2: Chat
        chat_payload = {"message": "What is the engineering department working on?"}
        chat_response = client.post("/chat", json=chat_payload, auth=(username, password))
        assert chat_response.status_code == 200
        
        # Step 3: Verify response structure
        chat_data = chat_response.json()
        assert chat_data["user"] == username
        assert "response" in chat_data

    def test_multiple_queries_same_user(self):
        """Test multiple queries from the same user"""
        username, password = TEST_USERS["engineering"]
        queries = [
            "What projects are active?",
            "Tell me about the engineering team",
            "What technologies do we use?"
        ]
        
        for query in queries:
            payload = {"message": query}
            response = client.post("/chat", json=payload, auth=(username, password))
            assert response.status_code == 200
            data = response.json()
            assert data["role"] == "engineering"


if __name__ == "__main__":
    # Run tests with: pytest tests/test_api.py -v
    pytest.main([__file__, "-v"])
