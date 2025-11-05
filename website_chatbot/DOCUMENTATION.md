# Website Chatbot - Complete Documentation

A grounded Q&A chatbot that indexes websites and provides answers with source citations. Built with **Microsoft Agent Framework** and **Google Vertex AI**, deployable as a FastAPI backend on GCP Cloud Run.

## Table of Contents
- [Features](#features)
- [Quick Start](#quick-start)
- [API Endpoints](#api-endpoints)
- [Frontend Integration](#frontend-integration)
- [Docker & Deployment](#docker--deployment)
- [Configuration](#configuration)
- [Architecture](#architecture)
- [Production Tips](#production-tips)

---

## Features

- 🔍 **Whole Website Indexing** - Crawls and indexes entire websites
- 🎯 **Grounded Responses** - All answers based on indexed content with citations
- 🔗 **Source Links** - Direct links to relevant website sections
- 🤖 **Multi-Agent Architecture** - Microsoft Agent Framework orchestration
- ☁️ **Google Vertex AI** - Gemini LLM and text embeddings
- 💬 **Interactive Chat** - Conversational interface with context
- 🌐 **REST API** - FastAPI backend with streaming support
- 🐳 **Docker Ready** - Containerized for GCP Cloud Run
- 📡 **Server-Sent Events** - Real-time streaming responses

---

## Quick Start

### Prerequisites
- Python 3.9+
- Google Cloud Platform account with Vertex AI enabled
- ChromaDB Cloud account (free tier available)
- Docker (for containerized deployment)

### Local Setup

1. **Install dependencies:**
```powershell
pip install -r requirements.txt
```

2. **Configure `.env` file:**
```env
# Google Cloud
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
VERTEX_AI_MODEL=gemini-2.0-flash-001
VERTEX_AI_EMBEDDING_MODEL=text-embedding-004

# ChromaDB Cloud
CHROMADB_TENANT=your-tenant-id
CHROMADB_DATABASE=your-database-name
CHROMADB_API_KEY=your-api-key
CHROMADB_COLLECTION_NAME=website_content

# API Settings
PORT=8080
HOST=0.0.0.0
CORS_ORIGINS=*

# Optional Cloud Run deployment
CLOUD_RUN_SERVICE_NAME=website-chatbot-api
```

3. **Authenticate with Google Cloud:**
```powershell
gcloud auth application-default login
```

4. **Run the API:**
```powershell
python api.py
```

API available at `http://localhost:8080`

### Docker Local

```powershell
# Build and run
docker build -t website-chatbot-api .
docker run -d --name chatbot-api -p 8080:8080 --env-file .env website-chatbot-api

# Or use docker-compose
docker-compose up
```

---

## API Endpoints

### 1. Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "indexed": true
}
```

### 2. Chat (Non-Streaming)
```http
POST /api/chat
Content-Type: application/json
```

**Request:**
```json
{
  "query": "What services does the company offer?",
  "chat_history": [
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "Hi! How can I help?"}
  ],
  "top_k": 5
}
```

**Response:**
```json
{
  "answer": "Based on the website, the company offers...",
  "sources": [
    {
      "title": "Services Page",
      "url": "https://example.com/services",
      "heading": "Our Services",
      "sections": ["Consulting", "Development"]
    }
  ],
  "query": "What services does the company offer?"
}
```

### 3. Chat (Streaming)
```http
POST /api/chat/stream
Content-Type: application/json
```

**Request:**
```json
{
  "query": "What services does the company offer?",
  "top_k": 5
}
```

**Response:** Server-Sent Events (SSE)
```
event: sources
data: {"type": "sources", "sources": [...]}

event: token
data: {"type": "token", "content": "Based on..."}

event: complete
data: {"type": "complete", "query": "..."}
```

### 4. Search
```http
POST /api/search
Content-Type: application/json
```

**Request:**
```json
{
  "query": "pricing information",
  "top_k": 5
}
```

**Response:**
```json
{
  "query": "pricing information",
  "results": [
    {
      "title": "Pricing Page",
      "url": "https://example.com/pricing",
      "heading": "Our Plans",
      "text": "We offer flexible pricing...",
      "score": 0.95
    }
  ]
}
```

### 5. Index Website
```http
POST /api/index
Content-Type: application/json
```

**Request:**
```json
{
  "url": "https://example.com",
  "max_depth": 3,
  "max_pages": 100,
  "use_js_crawler": true
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Successfully indexed 45 pages",
  "pages_indexed": 45
}
```

---

## Frontend Integration

### JavaScript/TypeScript

#### Non-Streaming Chat
```javascript
async function chat(query, chatHistory = []) {
  const response = await fetch('http://localhost:8080/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      query: query,
      chat_history: chatHistory,
      top_k: 5
    })
  });
  
  return await response.json();
}

// Usage
const result = await chat("What services do you offer?");
console.log(result.answer);
console.log(result.sources);
```

#### Streaming Chat
```javascript
async function chatStream(query, onToken, onSources, onComplete) {
  const response = await fetch('http://localhost:8080/api/chat/stream', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query: query, top_k: 5 })
  });

  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    const chunk = decoder.decode(value);
    const lines = chunk.split('\n');

    for (const line of lines) {
      if (line.startsWith('event: ')) {
        const eventType = line.slice(7);
        const dataLine = lines[lines.indexOf(line) + 1];
        
        if (dataLine?.startsWith('data: ')) {
          const data = JSON.parse(dataLine.slice(6));
          
          if (eventType === 'sources') onSources(data.sources);
          else if (eventType === 'token') onToken(data.content);
          else if (eventType === 'complete') onComplete();
        }
      }
    }
  }
}
```

### React Example
```jsx
import { useState } from 'react';

function ChatComponent() {
  const [query, setQuery] = useState('');
  const [answer, setAnswer] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    const response = await fetch('http://localhost:8080/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, top_k: 5 })
    });

    const data = await response.json();
    setAnswer(data.answer);
    setLoading(false);
  };

  return (
    <form onSubmit={handleSubmit}>
      <input 
        value={query} 
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Ask a question..."
      />
      <button type="submit" disabled={loading}>
        {loading ? 'Thinking...' : 'Send'}
      </button>
      {answer && <div>{answer}</div>}
    </form>
  );
}
```

---

## Docker & Deployment

### Build Docker Image

```powershell
# Build the image
docker build -t website-chatbot-api:latest .

# Verify
docker images | Select-String "website-chatbot-api"
```

### Test Locally

```powershell
# Run container
docker run -d `
  --name chatbot-api `
  -p 8080:8080 `
  --env-file .env `
  website-chatbot-api:latest

# Test
Invoke-RestMethod -Uri http://localhost:8080/health

# View logs
docker logs -f chatbot-api

# Stop and cleanup
docker stop chatbot-api
docker rm chatbot-api
```

### Deploy to GCP Cloud Run

#### Automated Deployment (Recommended)

```powershell
# One-command deployment - reads all config from .env
.\deploy-cloudrun.ps1

# Customize resources
.\deploy-cloudrun.ps1 -Memory "512Mi" -Cpu "1" -MaxInstances "3"
```

The script automatically:
- Reads `GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION`, `CLOUD_RUN_SERVICE_NAME` from `.env`
- Reads all environment variables from `.env`
- Deploys to Cloud Run
- Tests health endpoint
- Displays service URL

#### Manual Deployment Steps

1. **Push to Google Container Registry:**
```powershell
# Authenticate
gcloud auth configure-docker

# Tag and push
docker tag website-chatbot-api:latest gcr.io/YOUR_PROJECT_ID/website-chatbot-api:latest
docker push gcr.io/YOUR_PROJECT_ID/website-chatbot-api:latest
```

2. **Deploy to Cloud Run:**
```powershell
gcloud run deploy website-chatbot-api `
  --image gcr.io/YOUR_PROJECT_ID/website-chatbot-api:latest `
  --platform managed `
  --region us-central1 `
  --allow-unauthenticated `
  --memory 2Gi `
  --cpu 2 `
  --timeout 300 `
  --max-instances 10 `
  --min-instances 0 `
  --service-account "cloud-run-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" `
  --set-env-vars "GOOGLE_CLOUD_PROJECT=...,CHROMADB_API_KEY=..."
```

### Update Deployment

```powershell
# Rebuild and push
docker build -t website-chatbot-api:latest .
docker tag website-chatbot-api:latest gcr.io/YOUR_PROJECT_ID/website-chatbot-api:v1.0.1
docker push gcr.io/YOUR_PROJECT_ID/website-chatbot-api:v1.0.1

# Redeploy
.\deploy-cloudrun.ps1
```

### Monitor Deployment

```powershell
# Get service URL
gcloud run services describe website-chatbot-api `
  --region us-central1 `
  --format 'value(status.url)'

# View logs
gcloud run services logs read website-chatbot-api --region us-central1

# Check status
gcloud run services describe website-chatbot-api --region us-central1
```

---

## Configuration

### Environment Variables (.env)

All configuration in one file:

```env
# Required - Google Cloud
GOOGLE_CLOUD_PROJECT=your-project-id          # Also used for deployment
GOOGLE_CLOUD_LOCATION=us-central1              # Also used as Cloud Run region
VERTEX_AI_MODEL=gemini-2.0-flash-001
VERTEX_AI_EMBEDDING_MODEL=text-embedding-004

# Required - ChromaDB Cloud
CHROMADB_TENANT=your-tenant-id
CHROMADB_DATABASE=your-database-name
CHROMADB_API_KEY=your-api-key
CHROMADB_COLLECTION_NAME=website_content

# Optional - Cloud Run Deployment
CLOUD_RUN_SERVICE_NAME=website-chatbot-api    # Default if not specified

# Optional - API Settings (with defaults)
PORT=8080
HOST=0.0.0.0
CORS_ORIGINS=*
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
MAX_CRAWL_DEPTH=3
MAX_PAGES=100
```

### Project Structure

```
website_chatbot/
├── .env                    # Single configuration file
├── .dockerignore           # Docker build optimization
├── api.py                  # FastAPI application
├── main.py                 # CLI application
├── Dockerfile              # Container definition
├── docker-compose.yml      # Local Docker setup
├── requirements.txt        # Python dependencies
├── deploy-cloudrun.ps1     # Automated deployment script
├── agents/
│   ├── workflow.py         # Multi-agent orchestration
│   └── search_agent.py     # Search and answer agents
└── utils/
    ├── crawler.py          # Website crawler
    ├── vector_store.py     # ChromaDB integration
    └── vertex_chat_client.py # Vertex AI client
```

---

## Architecture

### Multi-Agent Workflow

```
User Query → Search Agent → ChromaDB Vector Search
                ↓
          Search Results → Answer Generation Agent → Vertex AI Gemini
                                    ↓
                          Grounded Answer + Sources → User
```

**Components:**

1. **Search Agent** - Performs semantic search on indexed content
2. **Answer Generation Agent** - Generates answers grounded in search results
3. **Workflow Orchestrator** - Coordinates agents using Microsoft Agent Framework
4. **Vector Store** - ChromaDB Cloud for embeddings storage
5. **LLM** - Google Vertex AI Gemini for generation

### Data Flow

1. **Indexing:**
   - Crawl website → Extract content → Chunk text
   - Generate embeddings → Store in ChromaDB

2. **Query Processing:**
   - User query → Generate query embedding
   - Search ChromaDB → Retrieve top-k chunks
   - Generate answer with Gemini → Return with sources

### Technology Stack

- **Framework:** FastAPI (REST API), Microsoft Agent Framework (orchestration)
- **LLM:** Google Vertex AI (gemini-2.0-flash-001)
- **Embeddings:** Vertex AI (text-embedding-004)
- **Vector DB:** ChromaDB Cloud
- **Deployment:** Docker, GCP Cloud Run
- **Language:** Python 3.11

---

## Production Tips

### Security

1. **Use Secret Manager** for sensitive data:
```powershell
# Create secret
echo "your-api-key" | gcloud secrets create chromadb-api-key --data-file=-

# Deploy with secret
gcloud run deploy website-chatbot-api `
  --set-secrets "CHROMADB_API_KEY=chromadb-api-key:latest"
```

2. **Set specific CORS origins:**
```env
CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
```

3. **Use service account with minimal permissions:**
```powershell
# Required roles only
gcloud projects add-iam-policy-binding PROJECT_ID `
  --member="serviceAccount:cloud-run-sa@PROJECT_ID.iam.gserviceaccount.com" `
  --role="roles/aiplatform.user"
```

### Cost Optimization

1. **Free tier settings:**
```powershell
.\deploy-cloudrun.ps1 -Memory "512Mi" -Cpu "1" -MaxInstances "3"
```

2. **Scale to zero:**
```env
# In deployment
--min-instances 0
--max-instances 3
```

3. **Monitor usage:**
- Check GCP Console → Cloud Run → Metrics
- Set billing alerts in GCP Console

### Performance

1. **Use versioned tags:**
```powershell
docker tag website-chatbot-api:latest gcr.io/PROJECT_ID/website-chatbot-api:v1.0.0
```

2. **Enable concurrency:**
```powershell
gcloud run services update website-chatbot-api `
  --concurrency 80 `
  --region us-central1
```

3. **Optimize chunk size:**
```env
CHUNK_SIZE=1000      # Balance between context and precision
CHUNK_OVERLAP=200    # Ensure context continuity
```

### Monitoring

1. **Cloud Logging:**
```powershell
# Real-time logs
gcloud run services logs tail website-chatbot-api --region us-central1

# Filter errors
gcloud run services logs read website-chatbot-api `
  --region us-central1 `
  --filter="severity>=ERROR"
```

2. **Health checks:**
```powershell
# Test endpoint
curl https://your-service-url.run.app/health
```

3. **Set up alerts:**
- GCP Console → Monitoring → Alerting
- Alert on error rate, latency, resource usage

---

## Troubleshooting

### Common Issues

**Issue:** Docker build fails with "No matching distribution for agent-framework"
- **Solution:** Ensure `requirements.txt` uses `agent-framework>=1.0.0b251001`

**Issue:** Permission denied during deployment
- **Solution:** Grant required IAM roles:
```powershell
gcloud projects add-iam-policy-binding PROJECT_ID `
  --member="user:YOUR_EMAIL" `
  --role="roles/run.admin"
```

**Issue:** ChromaDB connection fails
- **Solution:** Verify `CHROMADB_TENANT`, `CHROMADB_DATABASE`, `CHROMADB_API_KEY` in `.env`

**Issue:** Health check fails
- **Solution:** Check logs and ensure ChromaDB collection exists

### Support

- GitHub Issues: [Report bugs or request features]
- Documentation: This file
- GCP Support: https://cloud.google.com/support

---

## License

[Add your license here]

## Contributors

[Add contributors here]
