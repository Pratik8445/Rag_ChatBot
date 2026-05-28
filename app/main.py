import os
from dotenv import load_dotenv

# Load environment variables FIRST
load_dotenv()

# Now import other modules that depend on environment variables
from typing import Dict

from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel

from .services import RAGService
from .utils.auth import get_user_manager

app = FastAPI(
    title="FinSolve Internal Chatbot",
    description="RAG-based chatbot with role-based access control",
    version="1.0.0"
)
security = HTTPBasic()

# Initialize RAG service and user manager
rag_service = RAGService()
user_manager = get_user_manager()


class ChatRequest(BaseModel):
    message: str


# Authentication dependency
def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    username = credentials.username
    password = credentials.password
    is_valid, role = user_manager.authenticate(username, password)
    if not is_valid:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"username": username, "role": role}


# Login endpoint
@app.get("/login")
def login(user=Depends(authenticate)):
    return {"message": f"Welcome {user['username']}!", "role": user["role"]}


# Protected test endpoint
@app.get("/test")
def test(user=Depends(authenticate)):
    return {"message": f"Hello {user['username']}! You can now chat.", "role": user["role"]}


# Protected chat endpoint
@app.post("/chat")
def query(request: ChatRequest, user=Depends(authenticate)):
    """Chat with the RAG system using role-based document access"""
    try:
        result = rag_service.generate_response(
            query=request.message,
            user_role=user["role"],
            user_name=user["username"]
        )

        return {
            "user": user["username"],
            "role": user["role"],
            "message": request.message,
            "response": result["response"],
            "sources": result.get("sources", []),
            "confidence": result.get("confidence", 0.0),
            "documents_used": result.get("documents_used", 0)
        }
    except Exception as e:
        return {
            "user": user["username"],
            "role": user["role"],
            "message": request.message,
            "response": f"I apologize, but I'm experiencing technical difficulties: {str(e)}",
            "sources": [],
            "confidence": 0.0,
            "error": str(e)
        }