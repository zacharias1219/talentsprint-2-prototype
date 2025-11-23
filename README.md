# AI-Powered Financial Advisor

A comprehensive AI-powered financial advisor system using FinGPT/LLM, Alpha Vantage API, RAG pipeline, and personalization engine.

## Features

- **Personalized Financial Recommendations**: AI-powered investment advice tailored to user profiles
- **Real-time Market Data**: Integration with Alpha Vantage API for live market data
- **RAG Pipeline**: Retrieval-augmented generation for accurate, fact-grounded responses
- **User Profiling**: Comprehensive risk assessment and goal-based planning
- **Compliance & Guardrails**: Fact-checking, disclaimers, and regulatory compliance
- **Interactive Chat Interface**: Streamlit-based conversational UI

## Success Metrics

- **80% recommendation accuracy** vs expert benchmarks
- **60% improvement** in user engagement
- **40% reduction** in plan generation time

## Project Structure

```
project/
├── data/                    # Data files
│   ├── raw/                 # Raw API data
│   ├── processed/           # Processed datasets
│   ├── embeddings/          # Vector embeddings
│   └── cache/               # Cached API responses
├── models/                  # Model files
│   ├── fine_tuned/          # Fine-tuned model weights
│   ├── checkpoints/         # Training checkpoints
│   └── embeddings/           # Embedding models
├── src/                     # Source code
│   ├── data_collection/     # Data collection modules
│   ├── model_training/      # Model training modules
│   ├── personalization/     # Personalization engine
│   ├── rag_pipeline/        # RAG pipeline modules
│   ├── compliance/          # Compliance modules
│   ├── api/                 # API endpoints
│   └── utils/               # Utility modules
├── ui/                      # UI components
│   ├── streamlit_app.py     # Main Streamlit app
│   └── components/           # UI components
├── tests/                   # Test files
│   ├── unit/                # Unit tests
│   ├── integration/         # Integration tests
│   └── e2e/                 # End-to-end tests
├── docs/                    # Documentation
├── config/                  # Configuration files
├── notebooks/               # Jupyter notebooks
└── scripts/                 # Utility scripts
```

## Setup Instructions

### Prerequisites

- Python 3.9+ (but < 3.12)
- PostgreSQL 12+
- Redis (optional, for caching)
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd telentsprint-2-prototype
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

4. **Set up environment variables**
   ```bash
   # Copy example environment file
   cp .env.example .env
   
   # Edit .env with your API keys
   # Required:
   # - ALPHA_VANTAGE_API_KEY
   # - PINECONE_API_KEY
   # - DATABASE_URL
   ```

5. **Initialize database**
   ```bash
   # Create PostgreSQL database
   createdb financial_advisor
   
   # Run initialization script
   python scripts/init_database.py
   ```

6. **Run the application**
   ```bash
   streamlit run ui/streamlit_app.py
   ```

## Configuration

Configuration files are located in the `config/` directory:

- `config/config.yaml`: Application configuration
- `config/model_config.yaml`: Model-specific settings

Environment variables can override configuration values. See `.env.example` for available options.

## API Keys Required

- **Alpha Vantage**: Get free API key from https://www.alphavantage.co/support/#api-key
- **Pinecone**: Sign up at https://www.pinecone.io/
- **OpenAI** (optional): If using GPT models instead of FinGPT

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_data_collection.py
```

### Code Style

```bash
# Format code
black src/

# Check style
flake8 src/

# Type checking
mypy src/
```

## Documentation

- **API Documentation**: `docs/api_documentation.md`
- **Deployment Guide**: `docs/deployment_guide.md`
- **User Guide**: `docs/user_guide.md`
- **Project Documentation**: `PROJECT_DOCUMENTATION.md`
- **Project Rules**: `PROJECT_RULES.md`

## License

See LICENSE file for details.

## Contributing

1. Follow PEP 8 style guide
2. Write tests for new features
3. Update documentation
4. Ensure all tests pass before submitting

## Support

For issues and questions, please refer to the project documentation or create an issue in the repository.
