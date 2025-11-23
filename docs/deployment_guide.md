# Deployment Guide

## Prerequisites

- Python 3.9+ (but < 3.12)
- PostgreSQL 12+
- Redis (optional, for caching)
- API keys for:
  - Alpha Vantage
  - Pinecone
  - OpenAI (optional)

## Installation Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd telentsprint-2-prototype
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   - Copy `.env.example` to `.env`
   - Fill in all required API keys

5. **Initialize database**
   ```bash
   python scripts/init_database.py
   ```

6. **Run the application**
   ```bash
   streamlit run ui/streamlit_app.py
   ```

## Configuration

Edit `config/config.yaml` and `config/model_config.yaml` as needed for your environment.

## Production Deployment

For production deployment:

1. Use a production-grade WSGI server (e.g., Gunicorn)
2. Set up reverse proxy (e.g., Nginx)
3. Use environment-specific configuration
4. Set up monitoring and logging
5. Configure SSL/TLS certificates
6. Set up database backups

## Docker Deployment

Docker configuration files (Dockerfile, docker-compose.yml) can be added for containerized deployment.

