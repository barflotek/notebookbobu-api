# NotebookBobu API Service

A production-ready FastAPI service for document processing and AI analysis, designed to integrate with inbox-zero.

## 🌟 Features

- **Document Processing**: PDF, TXT, MD file analysis
- **AI-Powered Chat**: Query documents with natural language
- **Podcast Generation**: Convert documents to audio content
- **Supabase Integration**: Secure data storage and user management
- **Vercel Optimized**: Serverless deployment ready

## 🏗️ Architecture

```
┌─────────────────┐    REST API     ┌──────────────────┐
│   Inbox-Zero    │ ──────────────► │   NotebookBobu   │
│   (Next.js)     │                 │   API Service    │
│                 │                 │   (FastAPI)      │
└─────────────────┘                 └──────────────────┘
         │                                    │
         ▼                                    ▼
┌─────────────────────────────────────────────────────┐
│                 Supabase                            │
│         (Shared Database & Storage)                 │
└─────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your API keys

# Run the service
uvicorn app.main:app --reload --port 8000
```

### Vercel Deployment

```bash
# Deploy to Vercel
vercel --prod
```

## 📡 API Endpoints

- `POST /api/process` - Process a document
- `POST /api/query` - Query processed documents
- `POST /api/podcast` - Generate podcast from documents
- `GET /api/documents` - List user documents
- `DELETE /api/documents/{id}` - Delete document
- `GET /api/health` - Service health check

## 🔧 Environment Variables

```bash
# AI Services
OPENAI_API_KEY=sk-...
LLAMACLOUD_API_KEY=llx-...
ELEVENLABS_API_KEY=sk_...

# Database
SUPABASE_URL=https://...
SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_ROLE_KEY=eyJ...

# Security
JWT_SECRET=your-jwt-secret
API_KEY=your-internal-api-key
```

## 📚 Documentation

- API Documentation: `/docs` (Swagger UI)
- Health Check: `/health`
- Metrics: `/metrics`

## 🛡️ Security

- JWT authentication
- Row Level Security (RLS) with Supabase
- API key validation
- Rate limiting
- CORS configuration

## 🧪 Testing

```bash
# Run tests
pytest

# Run integration tests
pytest tests/integration/

# Test API endpoints
python scripts/test_api.py
```