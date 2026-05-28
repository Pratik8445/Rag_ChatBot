# DS RPC 01: Internal chatbot with role based access control

This is the starter repository for Codebasics's [Resume Project Challenge](https://codebasics.io/challenge/codebasics-gen-ai-data-science-resume-project-challenge) of building a RAG based Internal Chatbot with role based access control. Please fork this repository to get started.

## Features

- **Role-Based Access Control**: Users can only access documents relevant to their department
- **RAG (Retrieval-Augmented Generation)**: AI-powered responses based on company documents
- **Document Processing**: Automatic loading and chunking of Markdown and CSV files
- **Vector Search**: ChromaDB for efficient document retrieval
- **FastAPI Backend**: Modern, async web API with automatic documentation

## Setup Instructions

### 1. Install Dependencies

Open your terminal and run:

```bash
pip install -e .
```

Or use the Makefile:

```bash
make install
```

This installs the Python packages your project needs.

### 2. Set up the Groq API Key

We are using Groq for the chatbot brain. It is free for basic use.

1. Go to https://console.groq.com/
2. Sign up for a free account
3. Create a new API key
4. Open the `.env` file and paste your key like this:

```bash
GROQ_API_KEY=gsk_your_actual_groq_api_key_here
```

### 3. (Optional) Set up HuggingFace Token

For faster downloads and higher rate limits when using HuggingFace embeddings:

1. Go to https://huggingface.co/settings/tokens
2. Create a new access token
3. Add it to your `.env` file:

```bash
HF_TOKEN=your_huggingface_token_here
```

**Note**: The app works fine without this token, but you may see rate-limit warnings.

### 4. Initialize the RAG System

Run the setup script once so the app can read your documents and build search data:

```bash
python setup_rag.py
```

Or use the Makefile:

```bash
make setup
```

What this does:
- Loads all documents from `resources/data/`
- Converts them into small chunks
- Saves those chunks into ChromaDB vector stores (centralized in `./chroma_db/`)
- Uses free HuggingFace embeddings to understand text meaning

If it works, you should see:

- `RAG system initialized successfully!`
- `Documents loaded and vector stores created`

### 5. Start the FastAPI server

Run this command:

```bash
fastapi dev app/main.py
```

Or use the Makefile:

```bash
make run
```

Then open your browser at:

- `http://127.0.0.1:8000/docs`

This page shows your API and lets you test it interactively.

### 6. Quick Test Commands

Test the endpoints with curl:

```bash
# Login test
curl -u Tony:password123 http://127.0.0.1:8000/login

# Chat query
curl -X POST "http://127.0.0.1:8000/chat" \
   -u "Tony:password123" \
   -H "Content-Type: application/json" \
   -d '{"message": "What projects are active?"}'
```

Or use Python:

```python
import requests
from requests.auth import HTTPBasicAuth

# Login
resp = requests.get('http://127.0.0.1:8000/login',
                    auth=HTTPBasicAuth('Tony', 'password123'))
print(resp.json())

# Chat
resp = requests.post('http://127.0.0.1:8000/chat',
                     json={"message": "What projects are active?"},
                     auth=HTTPBasicAuth('Tony', 'password123'))
print(resp.json())
```

## API Endpoints

### Authentication
All endpoints require HTTP Basic Authentication. Available test users:

- `Tony` / `password123` (engineering)
- `Bruce` / `securepass` (marketing)
- `Sam` / `financepass` (finance)
- `Peter` / `pete123` (engineering)
- `Sid` / `sidpass123` (marketing)
- `Natasha` / `hrpass123` (hr)

**Note**: Passwords are securely hashed using SHA256.

### Endpoints

- `GET /login` - Test authentication
- `GET /test` - Verify access
- `POST /chat` - Chat with the RAG system

### Chat Example

Here are simple examples you can copy and run.

- Curl (login check):

```bash
curl -u Tony:password123 http://127.0.0.1:8000/login
```

- Curl (chat):

```bash
curl -X POST "http://127.0.0.1:8000/chat" \
   -u "Tony:password123" \
   -H "Content-Type: application/json" \
   -d '{"message": "What technologies does FinSolve use?"}'
```

- Python `requests` example:

```python
import requests
from requests.auth import HTTPBasicAuth

# Check login
resp = requests.get(
  'http://127.0.0.1:8000/login',
  auth=HTTPBasicAuth('Tony', 'password123')
)
print(resp.status_code)
print(resp.json())

# Send a chat message
payload = {"message": "What projects are active?"}
resp = requests.post(
  'http://127.0.0.1:8000/chat',
  json=payload,
  auth=HTTPBasicAuth('Tony', 'password123')
)
print(resp.status_code)
print(resp.json())
```

You can also use the Swagger docs page at `http://127.0.0.1:8000/docs` to try the endpoints interactively.

## Testing

### Automated Tests

Run the comprehensive test suite:

```bash
# Quick test
make test

# Verbose output
make test-verbose

# With coverage report
make test-coverage
```

Or directly with pytest:

```bash
pytest tests/ -v
```

Tests include:
- Authentication checks
- Chat endpoint validation
- Role-based access verification
- Response structure validation
- Integration workflow tests

### Using Postman

1. Import the collection: `FinSolve_Chatbot.postman_collection.json`
2. In Postman, use File → Import → Upload Files
3. Select the collection file
4. Start the FastAPI server: `make run`
5. Click "Send" on any request to test the endpoints

Pre-configured requests include:
- Login for each role (Engineering, Marketing, Finance, HR)
- Chat queries specific to each department
- Test endpoint verification

## Postman Collection

A pre-configured Postman collection is included: `FinSolve_Chatbot.postman_collection.json`

To use:
1. Open Postman
2. Click "Import" → Select `FinSolve_Chatbot.postman_collection.json`
3. Start the server: `make run`
4. Select any request and click "Send"

Pre-configured requests include:
- **Login**: All test users (Tony, Bruce, Sam, Natasha)
- **Chat Queries**: Department-specific queries
- **Test Endpoint**: Verification endpoint
- **API Docs**: Link to Swagger documentation

## Advanced Features & Improvements

### 1. Secure Authentication
- Passwords are hashed using bcrypt (not stored in plain text)
- Extensible `UserManager` class for easy database integration
- Ready for OAuth or custom auth backends

### 2. Centralized Configuration
- Chroma DB path configured via `CHROMA_DB_PATH` in `.env`
- All role-based vector stores organized under one directory
- Easy to move, backup, or scale

### 3. Environment Configuration

Key settings in `.env`:

```bash
# LLM Configuration
GROQ_API_KEY=gsk_your_api_key_here

# Optional: HuggingFace Token (faster downloads)
HF_TOKEN=your_hf_token_here

# Vector Database
CHROMA_DB_PATH=./chroma_db

# Document Processing
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

### 4. Quick Commands with Makefile

```bash
make install          # Install dependencies
make setup            # Initialize RAG system
make run              # Start FastAPI server
make test             # Run quick test suite
make test-verbose     # Detailed test output
make test-coverage    # Coverage report
make clean            # Clean cache/temp files
```

### 5. Automated Testing
- Comprehensive test suite in `tests/test_api.py`
- Tests cover: authentication, chat endpoint, role-based access, response validation
- Run with: `make test` or `pytest tests/ -v`

- **engineering**: Engineering documents, system architecture, SDLC processes
- **finance**: Financial reports, revenue analysis, expense breakdowns
- **hr**: Employee data, HR policies (CSV format)
- **marketing**: Marketing reports, campaign data, market analysis
- **general**: General company information accessible to all roles

## Project Structure

```
├── app/
│   ├── main.py                    # FastAPI application
│   ├── services/
│   │   ├── __init__.py
│   │   └── rag_service.py         # RAG implementation
│   ├── schemas/
│   │   └── __init__.py
│   └── utils/
│       ├── __init__.py
│       ├── auth.py                # Authentication & UserManager
│       └── logger.py              # Logging utility
├── tests/
│   └── test_api.py                # Automated API tests
├── resources/
│   └── data/                      # Department-specific documents
│       ├── engineering/
│       ├── finance/
│       ├── hr/
│       ├── marketing/
│       └── general/
├── chroma_db/                     # Vector database (auto-created)
│   ├── engineering/
│   ├── finance/
│   ├── hr/
│   ├── marketing/
│   └── general/
├── .env                           # Environment variables
├── .env.example                   # Example environment file
├── pyproject.toml                 # Project configuration
├── setup_rag.py                   # RAG initialization script
├── Makefile                       # Quick commands
├── FinSolve_Chatbot.postman_collection.json  # Postman collection
├── README.md                      # This file
└── requirements.txt               # Python dependencies
```

Visit the challenge page to learn more: [DS RPC-01](https://codebasics.io/challenge/codebasics-gen-ai-data-science-resume-project-challenge)

OVER ALL WORKFLOW
1. Load Documents
2. Split into Chunks
3. Convert to Embeddings
4. Store in Chroma DB
5. User asks Query
6. Retrieve Similar Chunks
7. Send Context + Query to LLM
8. Generate Answer