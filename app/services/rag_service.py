import os
import pandas as pd
from typing import List, Dict, Any, Optional
from pathlib import Path

from langchain_community.document_loaders import DirectoryLoader, TextLoader, UnstructuredMarkdownLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from ..utils.logger import get_logger

logger = get_logger(__name__)

class RAGService:
    """RAG Service for document retrieval and question answering"""

    def __init__(self):
        # Check API key
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key or api_key == "your_groq_api_key_here":
            logger.error("Groq API key not configured properly")
            raise ValueError("Please set a valid GROQ_API_KEY in your .env file")

        logger.info(f"Using Groq API key: {api_key[:10]}...{api_key[-4:] if len(api_key) > 14 else api_key}")

        # Use free HuggingFace embeddings (no API key needed)
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        # Use Groq for chat
        self.llm = ChatGroq(
            model="llama3-8b-8192",
            temperature=0.1,
            groq_api_key=api_key
        )

        # Initialize vector stores for each role
        self.vector_stores = {}
        self.chunk_size = int(os.getenv("CHUNK_SIZE", "1000"))
        self.chunk_overlap = int(os.getenv("CHUNK_OVERLAP", "200"))
        self.chroma_db_path = os.getenv("CHROMA_DB_PATH", "./chroma_db")

        # Role-based document access mapping
        self.role_permissions = {
            "engineering": ["engineering"],
            "finance": ["finance"],
            "hr": ["hr"],
            "marketing": ["marketing"],
            "general": ["general"]  # General docs accessible to all
        }

        # Initialize the system
        self._initialize_vector_stores()

    def _initialize_vector_stores(self):
        """Initialize vector stores for each department"""
        resources_path = Path(__file__).parent.parent.parent / "resources" / "data"

        for role in self.role_permissions.keys():
            # Create role-specific subdirectory under centralized CHROMA_DB_PATH
            db_path = os.path.join(self.chroma_db_path, role)
            self.vector_stores[role] = Chroma(
                persist_directory=db_path,
                embedding_function=self.embeddings
            )

        # Load and process documents
        self._load_documents(resources_path)

    def _load_documents(self, resources_path: Path):
        """Load and process documents from the resources directory"""
        logger.info("Loading documents...")

        for department in os.listdir(resources_path):
            dept_path = resources_path / department
            if not dept_path.is_dir():
                continue

            logger.info(f"Processing department: {department}")

            # Load markdown files
            md_loader = DirectoryLoader(
                str(dept_path),
                glob="*.md",
                loader_cls=UnstructuredMarkdownLoader
            )

            try:
                documents = md_loader.load()
                logger.info(f"Loaded {len(documents)} markdown documents from {department}")

                # Process CSV files for HR
                if department == "hr":
                    csv_files = list(dept_path.glob("*.csv"))
                    for csv_file in csv_files:
                        df = pd.read_csv(csv_file)
                        # Convert CSV to text format
                        csv_text = f"Employee Data from {csv_file.name}:\n\n{df.to_string()}"
                        from langchain_core.documents import Document
                        csv_doc = Document(
                            page_content=csv_text,
                            metadata={"source": str(csv_file), "department": department}
                        )
                        documents.append(csv_doc)
                        logger.info(f"Loaded CSV data from {csv_file.name}")

                if documents:
                    # Split documents into chunks
                    text_splitter = RecursiveCharacterTextSplitter(
                        chunk_size=self.chunk_size,
                        chunk_overlap=self.chunk_overlap,
                        length_function=len,
                    )

                    splits = text_splitter.split_documents(documents)

                    # Add metadata
                    for split in splits:
                        split.metadata["department"] = department

                    # Store in vector database
                    self.vector_stores[department].add_documents(splits)
                    logger.info(f"Added {len(splits)} document chunks to {department} vector store")

            except Exception as e:
                logger.error(f"Error loading documents for {department}: {str(e)}")

    def get_relevant_documents(self, query: str, user_role: str, k: int = 4) -> List[str]:
        """Retrieve relevant documents based on user role and query"""
        allowed_departments = self.role_permissions.get(user_role, [])

        # Always include general documents
        if "general" not in allowed_departments:
            allowed_departments.append("general")

        all_docs = []
        for dept in allowed_departments:
            if dept in self.vector_stores:
                try:
                    docs = self.vector_stores[dept].similarity_search(query, k=k//len(allowed_departments) or 1)
                    all_docs.extend(docs)
                except Exception as e:
                    logger.error(f"Error searching {dept} vector store: {str(e)}")

        # Sort by relevance and return top k
        all_docs.sort(key=lambda x: x.metadata.get("score", 0), reverse=True)
        return [doc.page_content for doc in all_docs[:k]]

    def generate_response(self, query: str, user_role: str, user_name: str) -> Dict[str, Any]:
        """Generate a response using RAG"""
        try:
            # Retrieve relevant documents
            relevant_docs = self.get_relevant_documents(query, user_role)

            if not relevant_docs:
                return {
                    "response": f"I apologize, but I don't have access to information relevant to your query as a {user_role}. Please contact your administrator if you need access to additional resources.",
                    "sources": [],
                    "confidence": 0.0
                }

            # Create context from retrieved documents
            context = "\n\n".join(relevant_docs)

            # Create prompt template
            prompt_template = ChatPromptTemplate.from_template("""
You are an internal company chatbot assistant. You have access to company documents and should provide helpful, accurate information based on the provided context.

User: {user_name}
Role: {user_role}
Query: {query}

Context from company documents:
{context}

Instructions:
- Answer based only on the provided context
- Be professional and helpful
- If the context doesn't contain enough information to fully answer, say so
- Include specific details from the documents when relevant
- Maintain confidentiality appropriate to the user's role

Response:""")

            # Create the RAG chain
            chain = (
                {"context": lambda x: context, "query": RunnablePassthrough(), "user_name": lambda x: user_name, "user_role": lambda x: user_role}
                | prompt_template
                | self.llm
                | StrOutputParser()
            )

            # Generate response
            response = chain.invoke(query)

            return {
                "response": response,
                "sources": [doc[:200] + "..." for doc in relevant_docs],  # Truncated previews
                "confidence": 0.8,  # Placeholder confidence score
                "documents_used": len(relevant_docs)
            }

        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return {
                "response": "I apologize, but I'm experiencing technical difficulties. Please try again later.",
                "sources": [],
                "confidence": 0.0,
                "error": str(e)
            }

    def refresh_documents(self):
        """Refresh the vector stores with updated documents"""
        logger.info("Refreshing document vector stores...")
        # Clear existing stores
        for store in self.vector_stores.values():
            store.delete_collection()

        # Reinitialize
        self._initialize_vector_stores()
        logger.info("Document refresh completed")