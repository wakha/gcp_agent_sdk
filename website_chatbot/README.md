# 🤖 Website Chatbot



> An intelligent chatbot that answers questions about your website with accurate, source-backed responses.



Built with **Microsoft Agent Framework** and **Google Vertex AI** to provide grounded answers from indexed website content.A grounded question-answering chatbot that indexes entire websites and provides answers with source links. Built using **Microsoft Agent Framework** for multi-agent orchestration and **Google Vertex AI** for LLM capabilities.



📖 **[View Complete Documentation](./DOCUMENTATION.md)** for detailed setup, API reference, and deployment guides.



---> **📖 Complete Documentation:** See [DOCUMENTATION.md](./DOCUMENTATION.md) for comprehensive setup, API reference, deployment guide, and production tips.A grounded question-answering chatbot that indexes entire websites and provides answers with source links. Built using **Microsoft Agent Framework** for multi-agent orchestration and **Google Vertex AI** for LLM capabilities.A grounded question-answering chatbot that indexes entire websites and provides answers with source links. Built using **Microsoft Agent Framework** for multi-agent orchestration and **Google Vertex AI** for LLM capabilities.



## ✨ Key Features



| Feature | Description |## Features

|---------|-------------|

| 🔍 **Full Website Indexing** | Crawls and indexes entire websites, not just single pages |

| 🎯 **Grounded Answers** | All responses backed by actual website content |

| 🔗 **Source Citations** | Provides direct links to relevant pages |- 🔍 **Whole Website Indexing**: Crawls and indexes entire websites (not just single pages)> **📖 Complete Documentation:** See [DOCUMENTATION.md](./DOCUMENTATION.md) for comprehensive setup, API reference, deployment guide, and production tips.> **📖 Complete Documentation:** See [DOCUMENTATION.md](./DOCUMENTATION.md) for comprehensive setup, API reference, deployment guide, and production tips.

| 🤖 **Multi-Agent System** | Orchestrated workflow using Microsoft Agent Framework |

| ☁️ **Cloud-Powered** | Google Vertex AI for embeddings and language understanding |- 🎯 **Grounded Responses**: All answers are based on indexed content with source citations

| 💬 **Interactive Chat** | Conversational interface with context awareness |

| 🌐 **REST API** | Easy integration with any frontend |- 🔗 **Source Links**: Provides direct links to relevant sections of the website

| 📡 **Real-time Streaming** | Live responses via Server-Sent Events |

| 🐳 **Docker Ready** | Deploy anywhere with containers |- 🤖 **Multi-Agent Architecture**: Uses Microsoft Agent Framework for agent orchestration



---- ☁️ **Google Vertex AI**: Leverages Vertex AI for embeddings and LLM responses## Features## Features



## 🏗️ How It Works- 💬 **Interactive Chat**: Conversational interface with context awareness



```- 🌐 **REST API**: FastAPI backend with endpoints for easy frontend integration

┌─────────────┐

│ User Query  │- 🐳 **Docker Ready**: Containerized for easy deployment to GCP Cloud Run

└──────┬──────┘

       │- 📡 **Streaming Support**: Real-time streaming responses with Server-Sent Events- 🔍 **Whole Website Indexing**: Crawls and indexes entire websites (not just single pages)- 🔍 **Whole Website Indexing**: Crawls and indexes entire websites (not just single pages)

       v

┌─────────────────────┐

│  Search Agent       │──────> ChromaDB Vector Search

│  (Semantic Search)  │## Architecture- 🎯 **Grounded Responses**: All answers are based on indexed content with source citations- 🎯 **Grounded Responses**: All answers are based on indexed content with source citations

└──────┬──────────────┘

       │

       v

┌─────────────────────┐```- 🔗 **Source Links**: Provides direct links to relevant sections of the website- 🔗 **Source Links**: Provides direct links to relevant sections of the website

│  Answer Agent       │──────> Vertex AI Gemini

│  (Generate Answer)  │User Query → Search Agent → ChromaDB Vector Search

└──────┬──────────────┘

       │                ↓- 🤖 **Multi-Agent Architecture**: Uses Microsoft Agent Framework for agent orchestration- 🤖 **Multi-Agent Architecture**: Uses Microsoft Agent Framework for agent orchestration

       v

┌─────────────────────┐          Search Results → Answer Generation Agent → Vertex AI Gemini

│  Response with      │

│  Source Links       │                                    ↓- ☁️ **Google Vertex AI**: Leverages Vertex AI for embeddings and LLM responses- ☁️ **Google Vertex AI**: Leverages Vertex AI for embeddings and LLM responses

└─────────────────────┘

```                          Grounded Answer + Sources → User



**Key Components:**```- 💬 **Interactive Chat**: Conversational interface with context awareness- 💬 **Interactive Chat**: Conversational interface with context awareness

- **Search Agent** → Finds relevant content using semantic search

- **Answer Agent** → Generates accurate answers from search results

- **ChromaDB Cloud** → Vector database for fast similarity search

- **Vertex AI Gemini** → Advanced language model for understanding and generation**Components:**- 🌐 **REST API**: FastAPI backend with endpoints for easy frontend integration- 🌐 **REST API**: FastAPI backend with endpoints for easy frontend integration



---- **Search Agent** - Semantic search on indexed content



## 🚀 Quick Start- **Answer Generation Agent** - Grounded answer generation- 🐳 **Docker Ready**: Containerized for easy deployment to GCP Cloud Run- 🐳 **Docker Ready**: Containerized for easy deployment to GCP Cloud Run



### Prerequisites- **Workflow Orchestrator** - Microsoft Agent Framework coordination



- Python 3.9 or higher- **Vector Store** - ChromaDB Cloud for embeddings- 📡 **Streaming Support**: Real-time streaming responses with Server-Sent Events- 📡 **Streaming Support**: Real-time streaming responses with Server-Sent Events

- Google Cloud account ([Get started](https://cloud.google.com))

- ChromaDB Cloud account ([Free tier available](https://www.trychroma.com))- **LLM** - Google Vertex AI Gemini

- Docker (optional, for deployment)



### Installation

## Quick Start

**Step 1: Install Dependencies**

```powershell## Architecture## Architecture

pip install -r requirements.txt

```### Prerequisites



**Step 2: Configure Settings**



Edit the `.env` file:- Python 3.9+

```env

# Google Cloud Configuration- Google Cloud Platform account with Vertex AI enabled```The chatbot uses a multi-agent workflow:

GOOGLE_CLOUD_PROJECT=your-project-id

GOOGLE_CLOUD_LOCATION=us-central1- ChromaDB Cloud account (free tier available)



# AI Models- Docker (optional, for containerized deployment)User Query → Search Agent → ChromaDB Vector Search

VERTEX_AI_MODEL=gemini-2.0-flash-001

VERTEX_AI_EMBEDDING_MODEL=text-embedding-004



# ChromaDB Cloud### Setup                ↓1. **Search Agent**: Performs semantic search on indexed website content using vector embeddings

CHROMADB_TENANT=your-tenant-id

CHROMADB_DATABASE=your-database-name

CHROMADB_API_KEY=your-api-key

CHROMADB_COLLECTION_NAME=website_content**1. Install Dependencies**          Search Results → Answer Generation Agent → Vertex AI Gemini2. **Answer Generation Agent**: Generates contextual answers using Vertex AI, grounded in search results



# API Settings

PORT=8080

CORS_ORIGINS=*```powershell                                    ↓3. **Workflow Orchestrator**: Coordinates the agents using Microsoft Agent Framework

```

pip install -r requirements.txt

**Step 3: Authenticate with Google Cloud**

```powershell```                          Grounded Answer + Sources → User

gcloud auth application-default login

```



Or use a service account:**2. Configure Environment Variables**``````

```powershell

$env:GOOGLE_APPLICATION_CREDENTIALS="path\to\service-account-key.json"

```

Edit the `.env` file with your configuration:User Query → Search Agent → Vector Store Search

**Step 4: Start the Server**

```powershell

python api.py

``````env**Components:**                ↓



Test the API:# Google Cloud

```powershell

Invoke-RestMethod -Uri http://localhost:8080/healthGOOGLE_CLOUD_PROJECT=your-project-id- **Search Agent** - Semantic search on indexed content          Search Results → Answer Generation Agent → Vertex AI LLM

```

GOOGLE_CLOUD_LOCATION=us-central1

---

VERTEX_AI_MODEL=gemini-2.0-flash-001- **Answer Generation Agent** - Grounded answer generation                                    ↓

## 💻 Usage

VERTEX_AI_EMBEDDING_MODEL=text-embedding-004

### API Endpoints

- **Workflow Orchestrator** - Microsoft Agent Framework coordination                          Grounded Answer + Source Links → User

| Endpoint | Method | Description |

|----------|--------|-------------|# ChromaDB Cloud

| `/health` | GET | Health check |

| `/api/chat` | POST | Send a question (non-streaming) |CHROMADB_TENANT=your-tenant-id- **Vector Store** - ChromaDB Cloud for embeddings```

| `/api/chat/stream` | POST | Send a question (streaming) |

| `/api/search` | POST | Search indexed content |CHROMADB_DATABASE=your-database-name

| `/api/index` | POST | Index a new website |

CHROMADB_API_KEY=your-api-key- **LLM** - Google Vertex AI Gemini

### Example: Send a Question

CHROMADB_COLLECTION_NAME=website_content

```powershell

$body = @{## Quick Start

    query = "What services do you offer?"

    top_k = 5# API Settings

} | ConvertTo-Json

PORT=8080## Quick Start

Invoke-RestMethod -Uri http://localhost:8080/api/chat `

  -Method Post `CORS_ORIGINS=*

  -ContentType "application/json" `

  -Body $body```### Prerequisites

```



### Example: Stream a Response

**3. Authenticate with Google Cloud**### Prerequisites

```javascript

const response = await fetch('http://localhost:8080/api/chat/stream', {

  method: 'POST',

  headers: { 'Content-Type': 'application/json' },```powershell- Python 3.9+

  body: JSON.stringify({ query: 'Tell me about your company' })

});gcloud auth application-default login



const reader = response.body.getReader();```- Python 3.9+- Google Cloud Platform account with Vertex AI enabled

const decoder = new TextDecoder();



while (true) {

  const { done, value } = await reader.read();Or set the path to your service account key:- Google Cloud Platform account with Vertex AI enabled- ChromaDB Cloud account (free tier available)

  if (done) break;

  

  const chunk = decoder.decode(value);

  console.log(chunk);```powershell- ChromaDB Cloud account (free tier available)- Docker (optional, for containerized deployment)

}

```$env:GOOGLE_APPLICATION_CREDENTIALS="path\to\your\service-account-key.json"



---```- Docker (optional, for containerized deployment)



## 🐳 Docker Deployment



### Run Locally with Docker**4. Run the API**### Setup



```powershell

# Build the image

docker build -t website-chatbot-api .```powershell### Setup



# Run the container# Start FastAPI server

docker run -d --name chatbot-api -p 8080:8080 --env-file .env website-chatbot-api

```python api.py### 1. Install Dependencies



Or use Docker Compose:

```powershell

docker-compose up# Test the API### 1. Install Dependencies

```

Invoke-RestMethod -Uri http://localhost:8080/health

### Deploy to Google Cloud Run

``````powershell

**One-Command Deployment:**

```powershell

.\deploy-cloudrun.ps1

```## Usage```powershellpip install -r requirements.txt



This script automatically:

- ✅ Builds a Docker image

- ✅ Tags with version and latest### REST APIpip install -r requirements.txt```

- ✅ Pushes to Google Container Registry

- ✅ Deploys to Cloud Run

- ✅ Configures all environment variables

The API provides several endpoints:```

**Custom Deployment:**

```powershell

.\deploy-cloudrun.ps1 -Memory "512Mi" -Cpu "1" -MaxInstances "3"

```- `GET /health` - Health check### 2. Configure Environment Variables



Available parameters:- `POST /api/chat` - Chat (non-streaming)

- `-Memory` → Memory allocation (default: 2Gi)

- `-Cpu` → CPU allocation (default: 2)- `POST /api/chat/stream` - Chat (streaming SSE)### 2. Configure Environment Variables

- `-MaxInstances` → Auto-scaling limit (default: 5)

- `-SkipBuild` → Skip Docker build step- `POST /api/search` - Search indexed content



---- `POST /api/index` - Index a websiteEdit the `.env` file with your configuration:



## 📁 Project Structure



```**Example chat request:**Edit the `.env` file with your configuration:

website_chatbot/

│```powershell

├── api.py                      # FastAPI application

├── main.py                     # CLI interface (optional)$body = @{```env

├── Dockerfile                  # Container definition

├── docker-compose.yml          # Local development    query = "What services do you offer?"

├── deploy-cloudrun.ps1         # Automated deployment

├── requirements.txt            # Python dependencies    top_k = 5```env# Google Cloud

├── .env                        # Configuration (DO NOT commit)

│} | ConvertTo-Json

├── agents/

│   ├── workflow.py             # Multi-agent orchestration# Google CloudGOOGLE_CLOUD_PROJECT=your-project-id

│   └── search_agent.py         # Search and answer logic

│Invoke-RestMethod -Uri http://localhost:8080/api/chat `

└── utils/

    ├── crawler.py              # Website indexing  -Method Post `GOOGLE_CLOUD_PROJECT=your-project-idGOOGLE_CLOUD_LOCATION=us-central1

    ├── vector_store.py         # ChromaDB integration

    └── vertex_chat_client.py   # Vertex AI client  -ContentType "application/json" `

```

  -Body $bodyGOOGLE_CLOUD_LOCATION=us-central1VERTEX_AI_MODEL=gemini-2.0-flash-001

---

```

## ⚙️ Configuration

VERTEX_AI_MODEL=gemini-2.0-flash-001VERTEX_AI_EMBEDDING_MODEL=text-embedding-004

All settings are managed in the `.env` file:

### CLI (Optional)

### Required Settings

```envVERTEX_AI_EMBEDDING_MODEL=text-embedding-004

GOOGLE_CLOUD_PROJECT=your-project-id

GOOGLE_CLOUD_LOCATION=us-central1```powershell

CHROMADB_TENANT=your-tenant-id

CHROMADB_DATABASE=your-database-name# Interactive chat# ChromaDB Cloud

CHROMADB_API_KEY=your-api-key

```python main.py chat



### Optional Settings (with defaults)# ChromaDB CloudCHROMADB_TENANT=your-tenant-id

```env

VERTEX_AI_MODEL=gemini-2.0-flash-001# Test search

VERTEX_AI_EMBEDDING_MODEL=text-embedding-004

CHROMADB_COLLECTION_NAME=website_contentpython main.py test --query "your question"CHROMADB_TENANT=your-tenant-idCHROMADB_DATABASE=your-database-name

PORT=8080

CORS_ORIGINS=*```

CHUNK_SIZE=1000

CHUNK_OVERLAP=200CHROMADB_DATABASE=your-database-nameCHROMADB_API_KEY=your-api-key

```

## Docker & Deployment

### Deployment Settings

```envCHROMADB_API_KEY=your-api-keyCHROMADB_COLLECTION_NAME=website_content

CLOUD_RUN_SERVICE_NAME=website-chatbot-api

```### Local Docker



---CHROMADB_COLLECTION_NAME=website_content



## 📚 Documentation```powershell



- **[DOCUMENTATION.md](./DOCUMENTATION.md)** - Complete guide with:# Build and run# API Settings

  - Detailed API reference

  - Frontend integration examplesdocker build -t website-chatbot-api .

  - Production deployment guide

  - Troubleshooting tipsdocker run -d --name chatbot-api -p 8080:8080 --env-file .env website-chatbot-api# API SettingsPORT=8080

  - Configuration options



---

# Or use docker-composePORT=8080CORS_ORIGINS=*

## 🛠️ Tech Stack

docker-compose up

- **Backend:** FastAPI (Python)

- **AI Framework:** Microsoft Agent Framework```CORS_ORIGINS=*```

- **LLM:** Google Vertex AI (Gemini)

- **Vector DB:** ChromaDB Cloud

- **Deployment:** Docker, GCP Cloud Run

- **API:** REST with SSE streaming### Deploy to GCP Cloud Run```



---



## 📝 License```powershell### 3. Authenticate with Google Cloud



This project is for demonstration purposes.# One-command deployment (reads all config from .env)



---.\deploy-cloudrun.ps1### 3. Authenticate with Google Cloud



**Questions?** See [DOCUMENTATION.md](./DOCUMENTATION.md) or open an issue on GitHub.



**Built with ❤️ using Microsoft Agent Framework and Google Vertex AI**# Or with custom resources```powershell


.\deploy-cloudrun.ps1 -Memory "512Mi" -Cpu "1" -MaxInstances "3"

``````powershellgcloud auth application-default login



See [DOCUMENTATION.md](./DOCUMENTATION.md) for detailed deployment instructions.gcloud auth application-default login```



## Project Structure```



```Or set the path to your service account key:

website_chatbot/

├── api.py                    # FastAPI applicationOr set the path to your service account key:

├── main.py                   # CLI application (optional)

├── deploy-cloudrun.ps1       # Automated deployment script```powershell

├── Dockerfile                # Container definition

├── docker-compose.yml        # Local Docker setup```powershell$env:GOOGLE_APPLICATION_CREDENTIALS="path\to\your\service-account-key.json"

├── requirements.txt          # Python dependencies

├── .env                      # Configuration (not in git)$env:GOOGLE_APPLICATION_CREDENTIALS="path\to\your\service-account-key.json"```

├── DOCUMENTATION.md          # Complete documentation

├── agents/```

│   ├── workflow.py           # Multi-agent orchestration

│   └── search_agent.py       # Search and answer agents### 4. Run the API

└── utils/

    ├── crawler.py            # Website crawler### 4. Run the API

    ├── vector_store.py       # ChromaDB integration

    └── vertex_chat_client.py # Vertex AI client```powershell

```

```powershell# Start FastAPI server

## Documentation

# Start FastAPI serverpython api.py

📖 **[DOCUMENTATION.md](./DOCUMENTATION.md)** - Complete guide including:

- Detailed API reference with examplespython api.py

- Frontend integration (JavaScript, React)

- Docker and GCP deployment# Test the API

- Production tips and troubleshooting

- Configuration options# Test the APIInvoke-RestMethod -Uri http://localhost:8080/health



## ConfigurationInvoke-RestMethod -Uri http://localhost:8080/health```



All configuration in `.env`:```



```env## Usage

# Required

GOOGLE_CLOUD_PROJECT=your-project-id## Usage

GOOGLE_CLOUD_LOCATION=us-central1

CHROMADB_TENANT=your-tenant### REST API

CHROMADB_DATABASE=your-database

CHROMADB_API_KEY=your-api-key### REST API



# Optional (with defaults)The API provides several endpoints:

VERTEX_AI_MODEL=gemini-2.0-flash-001

VERTEX_AI_EMBEDDING_MODEL=text-embedding-004The API provides several endpoints:

CHROMADB_COLLECTION_NAME=website_content

PORT=8080- `GET /health` - Health check

CORS_ORIGINS=*

CHUNK_SIZE=1000- `GET /health` - Health check- `POST /api/chat` - Chat (non-streaming)

CHUNK_OVERLAP=200

- `POST /api/chat` - Chat (non-streaming)- `POST /api/chat/stream` - Chat (streaming SSE)

# Optional Cloud Run deployment

CLOUD_RUN_SERVICE_NAME=website-chatbot-api- `POST /api/chat/stream` - Chat (streaming SSE)- `POST /api/search` - Search indexed content

```

- `POST /api/search` - Search indexed content- `POST /api/index` - Index a website

## Support

- `POST /api/index` - Index a website

- **Complete Documentation:** [DOCUMENTATION.md](./DOCUMENTATION.md)

- **Issues:** Open a GitHub issue**Example chat request:**

- **GCP Support:** https://cloud.google.com/support

**Example chat request:**```powershell

---

```powershell$body = @{

**Built with Microsoft Agent Framework and Google Vertex AI**

$body = @{    query = "What services do you offer?"

    query = "What services do you offer?"    top_k = 5

    top_k = 5} | ConvertTo-Json

} | ConvertTo-Json

Invoke-RestMethod -Uri http://localhost:8080/api/chat `

Invoke-RestMethod -Uri http://localhost:8080/api/chat `  -Method Post `

  -Method Post `  -ContentType "application/json" `

  -ContentType "application/json" `  -Body $body

  -Body $body```

```

### CLI (Optional)

### CLI (Optional)

```powershell

```powershell# Interactive chat

# Interactive chatpython main.py chat

python main.py chat

# Test search

# Test searchpython main.py test --query "your question"

python main.py test --query "your question"```

```

## Docker & Deployment

## Docker & Deployment

### Local Docker

### Local Docker

```powershell

```powershell# Build and run

# Build and rundocker build -t website-chatbot-api .

docker build -t website-chatbot-api .docker run -d --name chatbot-api -p 8080:8080 --env-file .env website-chatbot-api

docker run -d --name chatbot-api -p 8080:8080 --env-file .env website-chatbot-api

# Or use docker-compose

# Or use docker-composedocker-compose up

docker-compose up```

```

### Deploy to GCP Cloud Run

### Deploy to GCP Cloud Run

```powershell

```powershell# One-command deployment (reads all config from .env)

# One-command deployment (reads all config from .env).\deploy-cloudrun.ps1

.\deploy-cloudrun.ps1

# Or with custom resources

# Or with custom resources.\deploy-cloudrun.ps1 -Memory "512Mi" -Cpu "1" -MaxInstances "3"

.\deploy-cloudrun.ps1 -Memory "512Mi" -Cpu "1" -MaxInstances "3"```

```

See [DOCUMENTATION.md](./DOCUMENTATION.md) for detailed deployment instructions.

See [DOCUMENTATION.md](./DOCUMENTATION.md) for detailed deployment instructions.

## Project Structure

## Project Structure

```text

```text```text

website_chatbot/website_chatbot/

├── api.py                    # FastAPI application├── api.py                    # FastAPI application

├── main.py                   # CLI application (optional)├── main.py                   # CLI application (optional)

├── deploy-cloudrun.ps1       # Automated deployment script├── deploy-cloudrun.ps1       # Automated deployment script

├── Dockerfile                # Container definition├── Dockerfile                # Container definition

├── docker-compose.yml        # Local Docker setup├── docker-compose.yml        # Local Docker setup

├── requirements.txt          # Python dependencies├── requirements.txt          # Python dependencies

├── .env                      # Configuration (not in git)├── .env                      # Configuration (not in git)

├── DOCUMENTATION.md          # Complete documentation├── DOCUMENTATION.md          # Complete documentation

├── agents/├── agents/

│   ├── workflow.py           # Multi-agent orchestration│   ├── workflow.py           # Multi-agent orchestration

│   └── search_agent.py       # Search and answer agents│   └── search_agent.py       # Search and answer agents

└── utils/└── utils/

    ├── crawler.py            # Website crawler    ├── crawler.py            # Website crawler

    ├── vector_store.py       # ChromaDB integration    ├── vector_store.py       # ChromaDB integration

    └── vertex_chat_client.py # Vertex AI client    └── vertex_chat_client.py # Vertex AI client

``````



## Documentation## Architecture



📖 **[DOCUMENTATION.md](./DOCUMENTATION.md)** - Complete guide including:```

- Detailed API reference with examplesUser Query → Search Agent → ChromaDB Vector Search

- Frontend integration (JavaScript, React)                ↓

- Docker and GCP deployment          Search Results → Answer Generation Agent → Vertex AI Gemini

- Production tips and troubleshooting                                    ↓

- Configuration options                          Grounded Answer + Sources → User

```

## Configuration

**Components:**

All configuration in `.env`:- **Search Agent** - Semantic search on indexed content

- **Answer Generation Agent** - Grounded answer generation

```env- **Workflow Orchestrator** - Microsoft Agent Framework coordination

# Required- **Vector Store** - ChromaDB Cloud for embeddings

GOOGLE_CLOUD_PROJECT=your-project-id- **LLM** - Google Vertex AI Gemini

GOOGLE_CLOUD_LOCATION=us-central1

CHROMADB_TENANT=your-tenant## Documentation

CHROMADB_DATABASE=your-database

CHROMADB_API_KEY=your-api-key📖 **[DOCUMENTATION.md](./DOCUMENTATION.md)** - Complete guide including:

- Detailed API reference with examples

# Optional (with defaults)- Frontend integration (JavaScript, React)

VERTEX_AI_MODEL=gemini-2.0-flash-001- Docker and GCP deployment

VERTEX_AI_EMBEDDING_MODEL=text-embedding-004- Production tips and troubleshooting

CHROMADB_COLLECTION_NAME=website_content- Configuration options

PORT=8080

CORS_ORIGINS=*## Configuration

CHUNK_SIZE=1000

CHUNK_OVERLAP=200All configuration in `.env`:



# Optional Cloud Run deployment```env

CLOUD_RUN_SERVICE_NAME=website-chatbot-api# Required

```GOOGLE_CLOUD_PROJECT=your-project-id

GOOGLE_CLOUD_LOCATION=us-central1

## SupportCHROMADB_TENANT=your-tenant

CHROMADB_DATABASE=your-database

- **Complete Documentation:** [DOCUMENTATION.md](./DOCUMENTATION.md)CHROMADB_API_KEY=your-api-key

- **Issues:** Open a GitHub issue

- **GCP Support:** https://cloud.google.com/support# Optional (with defaults)

VERTEX_AI_MODEL=gemini-2.0-flash-001

---VERTEX_AI_EMBEDDING_MODEL=text-embedding-004

CHROMADB_COLLECTION_NAME=website_content

**Built with Microsoft Agent Framework and Google Vertex AI**PORT=8080

CORS_ORIGINS=*
CHUNK_SIZE=1000
CHUNK_OVERLAP=200

# Optional Cloud Run deployment
CLOUD_RUN_SERVICE_NAME=website-chatbot-api
```

## Support

- **Complete Documentation:** [DOCUMENTATION.md](./DOCUMENTATION.md)
- **Issues:** Open a GitHub issue
- **GCP Support:** https://cloud.google.com/support

---

**Built with Microsoft Agent Framework and Google Vertex AI**

The crawler (utils/crawler.py):
- Starts from the base URL
- Follows links within the same domain
- Respects depth limits and maximum page count
- Extracts text content, headings, and links
- Filters out non-HTML content (PDFs, images, etc.)

### 2. Vector Indexing

The vector store (utils/vector_store.py):
- Chunks text content with overlapping windows
- Generates embeddings using Vertex AI's 	ext-embedding-004`n- Stores embeddings with FAISS for efficient similarity search
- Maintains metadata (URL, title, headings) for each chunk

### 3. Multi-Agent Workflow

Using Microsoft Agent Framework:

**Search Agent** (gents/search_agent.py):
- Receives user query
- Performs semantic search on vector store
- Returns top-k most relevant chunks with URLs

**Answer Generation Agent** (gents/search_agent.py):
- Takes search results as context
- Constructs a prompt with sources
- Uses Vertex AI Gemini to generate grounded answers
- Cites sources inline in the response

**Workflow Orchestrator** (gents/workflow.py):
- Coordinates agent execution
- Manages data flow between agents
- Handles chat history for context

## Configuration Options

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| GOOGLE_CLOUD_PROJECT | GCP project ID | Required |
| GOOGLE_CLOUD_LOCATION | GCP region | us-central1 |
| VERTEX_AI_MODEL | LLM model name | gemini-1.5-pro |
| VERTEX_AI_EMBEDDING_MODEL | Embedding model | 	ext-embedding-004 |
| TARGET_WEBSITE_URL | Default website to index | None |
| MAX_CRAWL_DEPTH | Maximum crawl depth | 3 |
| MAX_PAGES | Maximum pages to crawl | 100 |
| CHUNK_SIZE | Text chunk size (chars) | 1000 |
| CHUNK_OVERLAP | Chunk overlap (chars) | 200 |

### Crawling Parameters

- **Depth**: Controls how deep to follow links from the base URL
  -  : Only index the base page
  - 1: Base page + direct links
  - 2: Base page + 2 levels of links
  - Higher values index more pages but take longer

- **Max Pages**: Safety limit to prevent excessive crawling
  - Adjust based on website size
  - Larger sites may need higher limits

### Chunking Strategy

- **Chunk Size**: Affects granularity of search results
  - Smaller chunks: More precise, but may lose context
  - Larger chunks: More context, but less precise

- **Overlap**: Helps maintain context across chunks
  - Prevents information from being split at boundaries

## Troubleshooting

### Authentication Issues

`powershell
# Verify authentication
gcloud auth application-default login

# Check current project
gcloud config get-value project

# Set project if needed
gcloud config set project YOUR_PROJECT_ID
```n
### API Not Enabled

Enable required APIs:

```powershell
gcloud services enable aiplatform.googleapis.com
```n
### Import Errors

If you get import errors for gent_framework:

```powershell
pip install --upgrade agent-framework
```n
### Memory Issues

For large websites:
- Reduce MAX_PAGES
- Reduce CHUNK_SIZE
- Process in batches

## Limitations

- Only crawls publicly accessible pages (no authentication)
- Respects same-domain restriction (doesn't follow external links)
- Text-only content (skips images, PDFs, videos)
- Rate limited by crawl delay (respectful crawling)

## 🚀 API & Deployment

### FastAPI Backend

Run the REST API server:

```powershell
python api.py
```

The API will be available at `http://localhost:8080` with the following endpoints:
- `GET /health` - Health check
- `POST /api/chat` - Chat endpoint (non-streaming)
- `POST /api/chat/stream` - Chat endpoint (streaming SSE)
- `POST /api/search` - Search indexed content
- `POST /api/index` - Index a new website

### Docker Deployment

**Build and test locally:**

```powershell
# Build Docker image
docker build -t website-chatbot-api:latest .

# Run locally
docker run -d --name chatbot-api -p 8080:8080 --env-file .env website-chatbot-api:latest

# Test the API
Invoke-RestMethod -Uri http://localhost:8080/health

# View logs
docker logs chatbot-api

# Stop container
docker stop chatbot-api && docker rm chatbot-api
```

**Deploy to GCP Cloud Run:**

```powershell
# Automated deployment (recommended - reads .env automatically)
.\deploy-cloudrun.ps1

# Or step by step:
# 1. Set your project ID
$PROJECT_ID = "your-project-id"

# 2. Tag and push to Container Registry
docker tag website-chatbot-api:latest gcr.io/$PROJECT_ID/website-chatbot-api:latest
docker push gcr.io/$PROJECT_ID/website-chatbot-api:latest

# 3. Deploy (reads .env file)
.\deploy-cloudrun.ps1
```

**📚 Complete deployment guide:** See [DEPLOYMENT.md](./DEPLOYMENT.md)

**📡 API documentation:** See [API_DOCUMENTATION.md](./API_DOCUMENTATION.md)

## Future Enhancements

- [ ] Support for PDF and document parsing
- [ ] Distributed vector storage (e.g., Vertex AI Vector Search)
- [ ] Multi-language support
- [ ] Scheduled re-indexing for fresh content
- [ ] Support for authenticated websites
- [ ] Image and multimedia understanding
- [x] REST API for frontend integration
- [x] Docker containerization
- [x] GCP Cloud Run deployment

## License

MIT

## Contributing

Contributions welcome! Please feel free to submit issues and pull requests.

