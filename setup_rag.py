#!/usr/bin/env python3
"""
Script to initialize the RAG system and load documents into vector stores.
Run this once after setting up your Groq API key.
"""

import os
import sys
from pathlib import Path

# Add the current directory and app directory to Python path
current_dir = Path(__file__).parent
app_dir = current_dir / "app"
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(app_dir))

from dotenv import load_dotenv
from app.services import RAGService
from app.utils.logger import get_logger

def main():
    # Load environment variables
    load_dotenv()

    # Check if Groq API key is set
    if not os.getenv("GROQ_API_KEY") or os.getenv("GROQ_API_KEY") == "your_groq_api_key_here":
        print("❌ Error: Please set your Groq API key in the .env file")
        print("   Edit .env and replace 'your_groq_api_key_here' with your actual API key")
        print("   Get a free API key at: https://console.groq.com/")
        return

    print("🚀 Initializing RAG system...")

    try:
        # Initialize RAG service (this will load documents and create vector stores)
        rag_service = RAGService()
        print("✅ RAG system initialized successfully!")
        print("📚 Documents loaded and vector stores created")

        # Test the system with a simple query
        print("\n🧪 Testing the system...")
        test_result = rag_service.generate_response(
            query="What is FinSolve Technologies?",
            user_role="general",
            user_name="TestUser"
        )

        if test_result.get("response"):
            print("✅ Test query successful!")
            print(f"Response: {test_result['response'][:200]}...")
        else:
            print("⚠️  Test query returned empty response")

    except Exception as e:
        print(f"❌ Error initializing RAG system: {str(e)}")
        return

    print("\n🎉 Setup complete! You can now run the FastAPI server:")
    print("   fastapi dev app/main.py")

if __name__ == "__main__":
    main()