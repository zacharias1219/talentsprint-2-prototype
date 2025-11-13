# PROJECT 16: PERSONALIZED FINANCIAL ADVISOR USING LLM
## Master Documentation & Reference Guide

**Last Updated:** January 2025
**Project Status:** Planning Phase
**Team:** Richard Abishai

---

## TABLE OF CONTENTS
1. [Project Overview](#project-overview)
2. [Business Context](#business-context)
3. [Technical Architecture](#technical-architecture)
4. [Phase-by-Phase Breakdown with Inputs/Outputs](#phase-breakdown)
5. [Data Specifications](#data-specifications)
6. [API Specifications](#api-specifications)
7. [Model Specifications](#model-specifications)
8. [Success Metrics & Evaluation](#success-metrics)
9. [Deliverables Checklist](#deliverables-checklist)
10. [Technical Stack](#technical-stack)
11. [Existing Solutions & Research](#existing-solutions-research)
12. [Implementation Best Practices](#implementation-best-practices)
13. [Assumptions & Constraints](#assumptions-constraints)
14. [Quick Reference Guide](#quick-reference-guide)

---

## PROJECT OVERVIEW

### Business Challenge
Most individuals lack access to high-quality, personalized financial advice. Traditional advisory services are:
- Expensive
- Limited in scalability
- Often generic in recommendations

**User Need:** Real-time, tailored guidance across:
- Investments
- Savings
- Insurance
- Retirement planning

### Project Objective
Build an AI-powered Intelligent Financial Advisor using LLM that provides:
- Personalized, data-driven financial insights
- Real-time recommendations
- Processing of user profiles, goals, and market data
- Advice on investments, budgeting, and long-term planning

### Key Success Metrics
| Metric | Target | Measurement |
|--------|--------|-------------|
| Recommendation Accuracy | 80% | vs. expert benchmarks |
| User Engagement Improvement | 60% | Pre/post comparison |
| Time Reduction | 40% | Plan generation time |
| User Satisfaction | High | Survey scores |

---

## TECHNICAL ARCHITECTURE

### High-Level System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERFACE LAYER                     │
│  (Streamlit Chat Interface / Voice Assistant)               │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│              ADVISORY CHAT INTERFACE (RAG)                  │
│  • Query Understanding                                      │
│  • RAG Pipeline (LangChain + Pinecone)                      │
│  • LLM Response Generation                                  │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│              PERSONALIZATION ENGINE                         │
│  • User Profiling                                           │
│  • Embedding System                                         │
│  • Recommendation Logic                                     │
│  • Visualization Components                                 │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│              FINE-TUNED LLM MODEL                           │
│  • FinGPT / GPT-4                                           │
│  • Financial Domain Knowledge                               │
│  • Risk Models                                              │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│              DATA COLLECTION LAYER                          │
│  • Alpha Vantage API                                        │
│  • Financial News APIs                                      │
│  • Market Data Processing                                   │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│              COMPLIANCE & GUARDRAILS                        │
│  • Hallucination Prevention                                 │
│  • Regulatory Compliance                                    │
│  • Explainability Layer                                     │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow Architecture

```
User Query → Query Understanding → RAG Retrieval → Context Assembly
    ↓
User Profile → Personalization Engine → Recommendation Logic
    ↓
Market Data → Data Processing → Real-time Context
    ↓
Fine-tuned LLM → Response Generation → Fact-checking → Compliance Check
    ↓
Final Response → Visualization → User Interface
```

---

## PHASE-BY-PHASE BREAKDOWN WITH INPUTS/OUTPUTS

### PHASE 1: PROJECT SETUP AND INFRASTRUCTURE
**Duration:** Week 1-2

#### INPUTS:
- Project requirements document
- API keys (Alpha Vantage, OpenAI/FinGPT)
- Development environment specifications
- Database requirements

#### PROCESSES:
1. Create project repository structure
2. Set up virtual environment
3. Configure API keys securely
4. Design database schema
5. Set up Docker (optional)
6. Initialize version control

#### OUTPUTS:
- ✅ Repository structure:
  ```
  project/
  ├── data/
  │   ├── raw/           # Raw API data
  │   ├── processed/     # Processed datasets
  │   ├── embeddings/    # Vector embeddings
  │   └── cache/         # Cached API responses
  ├── models/
  │   ├── fine_tuned/    # Fine-tuned model weights
  │   ├── checkpoints/   # Training checkpoints
  │   └── embeddings/    # Embedding models
  ├── src/
  │   ├── data_collection/
  │   │   ├── __init__.py
  │   │   ├── alpha_vantage_client.py
  │   │   ├── stock_data_fetcher.py
  │   │   ├── indicator_calculator.py
  │   │   ├── news_aggregator.py
  │   │   └── sentiment_analyzer.py
  │   ├── model_training/
  │   │   ├── __init__.py
  │   │   ├── data_preparation.py
  │   │   ├── fine_tuning.py
  │   │   ├── evaluation.py
  │   │   └── inference.py
  │   ├── personalization/
  │   │   ├── __init__.py
  │   │   ├── user_profiler.py
  │   │   ├── risk_assessor.py
  │   │   ├── recommendation_engine.py
  │   │   ├── embedding_generator.py
  │   │   └── visualization_generator.py
  │   ├── rag_pipeline/
  │   │   ├── __init__.py
  │   │   ├── vector_store.py
  │   │   ├── retriever.py
  │   │   ├── query_understanding.py
  │   │   └── response_generator.py
  │   ├── compliance/
  │   │   ├── __init__.py
  │   │   ├── fact_checker.py
  │   │   ├── compliance_checker.py
  │   │   ├── explainability.py
  │   │   └── safety_filters.py
  │   ├── api/
  │   │   ├── __init__.py
  │   │   ├── routes.py
  │   │   ├── middleware.py
  │   │   └── auth.py
  │   └── utils/
  │       ├── __init__.py
  │       ├── database.py
  │       ├── config.py
  │       └── logger.py
  ├── ui/
  │   ├── streamlit_app.py
  │   ├── components/
  │   │   ├── chat_interface.py
  │   │   ├── profile_form.py
  │   │   └── visualizations.py
  │   └── assets/
  ├── tests/
  │   ├── unit/
  │   ├── integration/
  │   └── e2e/
  ├── docs/
  │   ├── api_documentation.md
  │   ├── deployment_guide.md
  │   └── user_guide.md
  ├── config/
  │   ├── config.yaml
  │   └── model_config.yaml
  ├── notebooks/
  │   ├── data_exploration.ipynb
  │   ├── model_experiments.ipynb
  │   └── analysis.ipynb
  ├── scripts/
  │   ├── setup.sh
  │   ├── train_model.py
  │   └── deploy.py
  ├── requirements.txt
  ├── requirements-dev.txt
  ├── .env.example
  ├── .gitignore
  ├── docker-compose.yml
  ├── Dockerfile
  └── README.md
  ```
- ✅ Database schema (SQL/NoSQL):
  ```sql
  -- Users table
  CREATE TABLE users (
      user_id VARCHAR(255) PRIMARY KEY,
      email VARCHAR(255) UNIQUE,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      consent_given BOOLEAN DEFAULT FALSE,
      consent_date TIMESTAMP
  );

  -- User profiles table
  CREATE TABLE user_profiles (
      profile_id SERIAL PRIMARY KEY,
      user_id VARCHAR(255) REFERENCES users(user_id),
      age INTEGER,
      income DECIMAL(15, 2),
      employment_status VARCHAR(50),
      location VARCHAR(255),
      risk_tolerance_score DECIMAL(3, 2),
      risk_category VARCHAR(50),
      investment_experience VARCHAR(50),
      profile_data JSONB,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  );

  -- Financial goals table
  CREATE TABLE financial_goals (
      goal_id SERIAL PRIMARY KEY,
      user_id VARCHAR(255) REFERENCES users(user_id),
      goal_type VARCHAR(50),
      target_amount DECIMAL(15, 2),
      time_horizon INTEGER,
      priority VARCHAR(20),
      current_progress DECIMAL(15, 2) DEFAULT 0,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  );

  -- Recommendations table
  CREATE TABLE recommendations (
      rec_id SERIAL PRIMARY KEY,
      user_id VARCHAR(255) REFERENCES users(user_id),
      recommendation_data JSONB,
      confidence_score DECIMAL(3, 2),
      generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      status VARCHAR(50) DEFAULT 'active'
  );

  -- Interactions table
  CREATE TABLE interactions (
      interaction_id SERIAL PRIMARY KEY,
      user_id VARCHAR(255) REFERENCES users(user_id),
      query_text TEXT,
      response_text TEXT,
      response_data JSONB,
      feedback_score INTEGER,
      feedback_comment TEXT,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  );

  -- Market data cache table
  CREATE TABLE market_data_cache (
      cache_id SERIAL PRIMARY KEY,
      symbol VARCHAR(50),
      data_type VARCHAR(50),
      data JSONB,
      fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      expires_at TIMESTAMP
  );

  -- Indexes
  CREATE INDEX idx_user_profiles_user_id ON user_profiles(user_id);
  CREATE INDEX idx_recommendations_user_id ON recommendations(user_id);
  CREATE INDEX idx_interactions_user_id ON interactions(user_id);
  CREATE INDEX idx_market_data_symbol ON market_data_cache(symbol);
  ```
- ✅ Configuration files:
  - `config/config.yaml`: Application configuration
  - `config/model_config.yaml`: Model-specific settings
  - `.env.example`: Environment variables template
- ✅ Environment setup documentation
- ✅ API key management system

#### DELIVERABLES:
- Project repository with complete structure
- Database schema documentation
- Setup guide (README.md)
- Configuration templates

---

### PHASE 2: DATA COLLECTION AND INTEGRATION
**Duration:** Week 2-3

#### INPUTS:
- Alpha Vantage API key
- Financial news API credentials (NewsAPI, Alpha Vantage News)
- Data requirements specification
- Rate limiting constraints

#### PROCESSES:
1. Integrate Alpha Vantage API
2. Fetch real-time stock data
3. Fetch historical data
4. Extract technical indicators
5. Collect sector performance data
6. Fetch exchange rates, mutual funds, ETFs
7. Integrate financial news APIs
8. Implement sentiment analysis
9. Set up data caching
10. Implement error handling and retry logic
11. Data validation and cleaning

#### OUTPUTS:
- ✅ Data Collection Module (`src/data_collection/`):
  - `alpha_vantage_client.py`: API wrapper with rate limiting
  - `stock_data_fetcher.py`: Stock price fetcher
  - `indicator_calculator.py`: Technical indicators
  - `news_aggregator.py`: News collection
  - `sentiment_analyzer.py`: Sentiment analysis
  - `data_validator.py`: Data validation
  - `cache_manager.py`: Caching system
- ✅ Data Schema:
  ```python
  # StockData schema
  StockData = {
      "symbol": str,  # e.g., "AAPL"
      "timestamp": datetime,
      "open": float,
      "high": float,
      "low": float,
      "close": float,
      "volume": int,
      "adjusted_close": float,
      "indicators": {
          "RSI": float,  # Relative Strength Index
          "MACD": float,  # Moving Average Convergence Divergence
          "MACD_signal": float,
          "MACD_histogram": float,
          "Bollinger_Upper": float,
          "Bollinger_Middle": float,
          "Bollinger_Lower": float,
          "SMA_20": float,  # Simple Moving Average 20-day
          "SMA_50": float,  # Simple Moving Average 50-day
          "EMA_12": float,  # Exponential Moving Average 12-day
          "EMA_26": float,  # Exponential Moving Average 26-day
          "Stochastic_K": float,
          "Stochastic_D": float
      },
      "metadata": {
          "timezone": str,
          "currency": str,
          "exchange": str
      }
  }
  
  # SectorData schema
  SectorData = {
      "sector": str,  # e.g., "Technology", "Healthcare"
      "performance": float,  # Percentage change
      "timestamp": datetime,
      "ranking": int,
      "top_stocks": List[str]
  }
  
  # NewsData schema
  NewsData = {
      "news_id": str,
      "title": str,
      "content": str,
      "summary": str,
      "source": str,
      "author": str,
      "url": str,
      "published_at": datetime,
      "sentiment_score": float,  # -1 to 1
      "sentiment_label": str,  # "positive", "negative", "neutral"
      "related_symbols": List[str],
      "topics": List[str],
      "relevance_score": float
  }
  
  # MutualFundData schema
  MutualFundData = {
      "symbol": str,
      "name": str,
      "nav": float,  # Net Asset Value
      "nav_date": datetime,
      "expense_ratio": float,
      "category": str,
      "risk_level": str,
      "returns": {
          "1_year": float,
          "3_year": float,
          "5_year": float,
          "10_year": float
      },
      "holdings": List[dict]
  }
  
  # ETFData schema
  ETFData = {
      "symbol": str,
      "name": str,
      "price": float,
      "price_date": datetime,
      "expense_ratio": float,
      "category": str,
      "underlying_index": str,
      "assets_under_management": float,
      "returns": {
          "1_year": float,
          "3_year": float,
          "5_year": float
      },
      "holdings": List[dict]
  }
  
  # ExchangeRateData schema
  ExchangeRateData = {
      "from_currency": str,  # e.g., "USD"
      "to_currency": str,  # e.g., "EUR"
      "rate": float,
      "timestamp": datetime,
      "bid": float,
      "ask": float
  }
  ```
- ✅ Sample datasets (CSV/JSON files)
- ✅ Data validation reports
- ✅ API integration documentation
- ✅ Rate limiting implementation
- ✅ Caching strategy documentation

#### DELIVERABLES:
- Functional data collection modules
- Sample datasets
- Data collection documentation
- API integration guide
- Data pipeline documentation

---

### PHASE 3: MODEL TRAINING AND FINE-TUNING
**Duration:** Week 3-5

#### INPUTS:
- Base LLM model (FinGPT/GPT-4)
- Financial corpus dataset
- Market data from Phase 2
- Expert financial advice examples
- Risk model documentation

#### PROCESSES:
1. Prepare financial corpus
2. Format market data for training
3. Create training examples
4. Set up fine-tuning pipeline
5. Configure training parameters
6. Train model on financial domain
7. Evaluate model performance
8. Iterate and improve
9. Implement reinforcement learning from expert feedback (RLEF)

#### OUTPUTS:
- ✅ Training Data:
  ```python
  TrainingExample = {
      "input": str,  # User query or context
      "output": str,  # Financial advice response
      "domain": str,  # "investment", "retirement", "savings", "insurance"
      "risk_level": str,  # "low", "medium", "high"
      "source": str,  # "expert", "market_data", "corpus"
      "metadata": {
          "user_profile_context": dict,
          "market_context": dict,
          "expert_rating": float
      }
  }
  
  # Training dataset structure
  TrainingDataset = {
      "investment_advice": List[TrainingExample],
      "retirement_planning": List[TrainingExample],
      "savings_strategies": List[TrainingExample],
      "risk_assessment": List[TrainingExample],
      "portfolio_optimization": List[TrainingExample],
      "market_analysis": List[TrainingExample]
  }
  ```
- ✅ Fine-tuned Model:
  - Model weights file (`.bin` or `.safetensors`)
  - Tokenizer files (`tokenizer.json`, `vocab.json`)
  - Configuration files (`config.json`)
  - Model metadata (`model_info.json`)
- ✅ Training Scripts:
  - `train_financial_model.py`: Main training script
  - `evaluate_model.py`: Evaluation script
  - `inference.py`: Inference script
  - `data_preparation.py`: Data preprocessing
- ✅ Evaluation Metrics:
  ```python
  ModelMetrics = {
      "overall_accuracy": float,  # Target: 80%
      "financial_qa_score": float,
      "domain_knowledge_score": float,
      "benchmark_comparison": {
          "expert_alignment": float,
          "factual_accuracy": float,
          "recommendation_quality": float
      },
      "per_category_accuracy": {
          "investment": float,
          "retirement": float,
          "savings": float,
          "risk_assessment": float
      },
      "hallucination_rate": float,  # Should be low
      "response_time": float,
      "training_loss": List[float],
      "validation_loss": List[float]
  }
  ```
- ✅ Model performance report
- ✅ Fine-tuning configuration:
  ```python
  TrainingConfig = {
      "base_model": "FinGPT/fingpt-forecaster_dow30_llama2-7b-lora",
      "learning_rate": 2e-5,
      "batch_size": 8,
      "gradient_accumulation_steps": 4,
      "num_epochs": 5,
      "max_seq_length": 1024,
      "warmup_steps": 100,
      "weight_decay": 0.01,
      "optimizer": "AdamW",
      "lr_scheduler": "cosine",
      "save_steps": 500,
      "eval_steps": 250,
      "logging_steps": 50
  }
  ```

#### DELIVERABLES:
- Fine-tuned model artifacts
- Training documentation
- Model evaluation report
- Benchmark comparison results
- Training scripts and configurations

---

### PHASE 4: PERSONALIZATION ENGINE
**Duration:** Week 5-6

#### INPUTS:
- User profile data (income, age, risk tolerance, goals)
- Investment instrument database
- Fine-tuned model from Phase 3
- Market data from Phase 2

#### PROCESSES:
1. Design user profile schema
2. Create risk assessment questionnaire
3. Build embedding system
4. Implement recommendation algorithms
5. Create visualization components
6. Integrate goal tracking
7. Implement asset allocation logic
8. Build diversification calculator

#### OUTPUTS:
- ✅ User Profile Schema:
  ```python
  UserProfile = {
      "user_id": str,
      "demographics": {
          "age": int,
          "income": float,
          "employment_status": str,  # "employed", "self_employed", "retired", "unemployed"
          "location": str,
          "marital_status": str,
          "dependents": int
      },
      "risk_tolerance": {
          "score": float,  # 0-1 scale
          "category": str,  # "conservative", "moderate", "aggressive"
          "assessment_date": datetime,
          "factors": {
              "investment_experience": str,  # "beginner", "intermediate", "advanced"
              "time_horizon": str,  # "short", "medium", "long"
              "loss_tolerance": str,  # "low", "medium", "high"
              "volatility_comfort": str
          }
      },
      "financial_goals": [
          {
              "goal_id": str,
              "type": str,  # "retirement", "savings", "education", "house", "emergency"
              "target_amount": float,
              "current_amount": float,
              "time_horizon": int,  # years
              "priority": str,  # "high", "medium", "low"
              "deadline": datetime,
              "status": str  # "active", "completed", "paused"
          }
      ],
      "current_portfolio": {
          "total_value": float,
          "allocations": {
              "stocks": float,  # percentage
              "bonds": float,
              "mutual_funds": float,
              "etfs": float,
              "cash": float,
              "real_estate": float,
              "commodities": float,
              "crypto": float
          },
          "holdings": [
              {
                  "symbol": str,
                  "type": str,
                  "quantity": float,
                  "current_value": float,
                  "purchase_price": float,
                  "gain_loss": float,
                  "gain_loss_percent": float
              }
          ]
      },
      "financial_situation": {
          "monthly_income": float,
          "monthly_expenses": float,
          "savings_rate": float,
          "debt": {
              "total": float,
              "credit_cards": float,
              "mortgage": float,
              "student_loans": float,
              "other": float
          },
          "emergency_fund": float,
          "insurance_coverage": {
              "life_insurance": float,
              "health_insurance": bool,
              "disability_insurance": bool
          }
      },
      "investment_experience": str,  # "beginner", "intermediate", "advanced"
      "preferences": {
          "investment_style": str,  # "active", "passive", "mixed"
          "geographic_preference": List[str],
          "sector_preferences": List[str],
          "esg_preferences": bool
      },
      "created_at": datetime,
      "updated_at": datetime
  }
  ```
- ✅ Embedding System:
  ```python
  # User profile embedding (vector: 768-dim or 384-dim)
  ProfileEmbedding = {
      "user_id": str,
      "embedding": List[float],  # Vector representation
      "metadata": {
          "model": str,  # Embedding model name
          "dimension": int,
          "created_at": datetime
      }
  }
  
  # Investment instrument embedding
  InstrumentEmbedding = {
      "symbol": str,
      "instrument_type": str,
      "embedding": List[float],
      "metadata": {
          "risk_level": str,
          "category": str,
          "expected_return": float
      }
  }
  ```
- ✅ Recommendation Output:
  ```python
  Recommendation = {
      "user_id": str,
      "recommendation_id": str,
      "timestamp": datetime,
      "recommendations": [
          {
              "instrument": str,  # "AAPL", "SPY", "VTI"
              "instrument_name": str,
              "instrument_type": str,  # "stock", "etf", "mutual_fund", "bond"
              "allocation_percentage": float,
              "allocation_amount": float,  # Based on user's investable capital
              "reasoning": str,
              "expected_return": float,  # Annual percentage
              "risk_level": str,
              "time_horizon": str,  # "short", "medium", "long"
              "diversification_benefit": str,
              "pros": List[str],
              "cons": List[str],
              "alternatives": List[str]
          }
      ],
      "portfolio_allocation": {
          "stocks": float,
          "bonds": float,
          "mutual_funds": float,
          "etfs": float,
          "cash": float,
          "rebalancing_needed": bool,
          "current_allocation": dict,
          "target_allocation": dict
      },
      "risk_assessment": {
          "overall_risk": str,
          "risk_score": float,
          "diversification_score": float,  # 0-1
          "risk_factors": List[str],
          "risk_mitigation": List[str]
      },
      "goal_alignment": [
          {
              "goal_id": str,
              "goal_type": str,
              "projected_achievement": bool,
              "projected_date": datetime,
              "projected_amount": float,
              "confidence": float,
              "required_monthly_contribution": float,
              "recommended_instruments": List[str]
          }
      ],
      "visualizations": {
          "allocation_chart": str,  # file path or base64
          "risk_return_chart": str,
          "timeline_projection": str,
          "goal_progress_chart": str,
          "diversification_chart": str
      },
      "next_steps": List[str],
      "warnings": List[str],
      "disclaimers": List[str]
  }
  ```
- ✅ Personalization Module:
  - `user_profiler.py`: Profile creation and management
  - `risk_assessor.py`: Risk tolerance assessment
  - `recommendation_engine.py`: Core recommendation logic
  - `embedding_generator.py`: Generate embeddings
  - `similarity_matcher.py`: Match users to instruments
  - `asset_allocator.py`: Asset allocation logic
  - `diversification_calculator.py`: Diversification metrics
  - `goal_planner.py`: Goal-based planning
  - `visualization_generator.py`: Create charts and graphs

#### DELIVERABLES:
- Personalization engine code
- User profiling system
- Recommendation generation module
- Visualization components
- Personalization documentation
- Risk assessment questionnaire

---

### PHASE 5: RAG PIPELINE AND CHAT INTERFACE
**Duration:** Week 6-7

#### INPUTS:
- Fine-tuned model (Phase 3)
- Market data (Phase 2)
- User profiles (Phase 4)
- Financial knowledge base
- User queries

#### PROCESSES:
1. Set up vector database (Pinecone)
2. Create knowledge base embeddings
3. Implement retrieval mechanism
4. Build query understanding module
5. Integrate LLM for response generation
6. Build Streamlit chat interface
7. Implement conversation history
8. Add response streaming
9. Implement context window management

#### OUTPUTS:
- ✅ RAG Pipeline:
  ```python
  RAGPipeline = {
      "vector_store": {
          "type": "Pinecone",  # or "Chroma", "FAISS"
          "index_name": str,
          "embedding_model": str,
          "dimension": int
      },
      "retrieval_strategy": {
          "top_k": int,  # Number of documents to retrieve (e.g., 5)
          "similarity_threshold": float,  # Minimum similarity score
          "reranking": bool,
          "reranking_model": str,  # Optional reranking model
          "diversity_penalty": float  # For diverse results
      },
      "context_injection": {
          "market_data": bool,
          "user_profile": bool,
          "historical_recommendations": bool,
          "recent_news": bool,
          "max_context_length": int  # Tokens
      },
      "knowledge_sources": [
          "financial_corpus",
          "market_data",
          "user_profiles",
          "expert_advice",
          "regulatory_guidelines"
      ]
  }
  ```
- ✅ Query Understanding:
  ```python
  QueryAnalysis = {
      "original_query": str,
      "intent": str,  # "investment_advice", "portfolio_review", "goal_planning", "market_analysis", "risk_assessment"
      "entities": {
          "instruments": List[str],  # ["AAPL", "SPY"]
          "timeframes": List[str],  # ["1 year", "5 years"]
          "amounts": List[float],  # [10000, 50000]
          "goals": List[str],  # ["retirement", "savings"]
          "risk_keywords": List[str]
      },
      "user_context": UserProfile,
      "retrieved_context": [
          {
              "source": str,
              "content": str,
              "relevance_score": float,
              "metadata": dict
          }
      ],
      "query_embedding": List[float],
      "confidence": float
  }
  ```
- ✅ LLM Response:
  ```python
  LLMResponse = {
      "response_text": str,
      "response_type": str,  # "advice", "analysis", "recommendation", "explanation"
      "sources": [
          {
              "type": str,  # "market_data", "knowledge_base", "user_profile", "expert_advice"
              "content": str,
              "relevance_score": float,
              "citation": str
          }
      ],
      "confidence_score": float,  # 0-1
      "recommendations": List[Recommendation],  # If applicable
      "disclaimers": List[str],
      "follow_up_questions": List[str],
      "suggested_actions": List[str],
      "metadata": {
          "tokens_used": int,
          "response_time": float,
          "model_version": str
      }
  }
  ```
- ✅ Chat Interface:
  ```python
  ChatMessage = {
      "message_id": str,
      "user_id": str,
      "role": str,  # "user" or "assistant"
      "content": str,
      "timestamp": datetime,
      "metadata": {
          "query_analysis": QueryAnalysis,
          "response_data": LLMResponse,
          "feedback": dict  # User feedback if available
      }
  }
  
  ConversationHistory = {
      "conversation_id": str,
      "user_id": str,
      "messages": List[ChatMessage],
      "context_summary": str,
      "created_at": datetime,
      "updated_at": datetime
  }
  ```
- ✅ Chat Interface Components:
  - `streamlit_app.py`: Main UI application
  - `chat_interface.py`: Chat UI component
  - `message_renderer.py`: Message display
  - `response_streamer.py`: Streaming responses
  - `conversation_manager.py`: History management
  - `feedback_collector.py`: User feedback

#### DELIVERABLES:
- Functional RAG pipeline
- Chat interface (Streamlit)
- Query understanding module
- Response generation system
- RAG documentation
- Conversation management system

---

### PHASE 6: COMPLIANCE AND GUARDRAILS
**Duration:** Week 7-8

#### INPUTS:
- LLM responses from Phase 5
- Financial regulations documentation
- User consent requirements
- Recommendation outputs

#### PROCESSES:
1. Implement fact-checking module
2. Add source verification
3. Create disclaimers system
4. Implement user consent management
5. Build explainability features
6. Add safety filters
7. Create compliance documentation
8. Implement audit logging

#### OUTPUTS:
- ✅ Fact-Checking Module:
  ```python
  FactCheckResult = {
      "claim": str,
      "verified": bool,
      "verification_method": str,  # "api_check", "knowledge_base", "expert_review"
      "source": str,
      "confidence": float,
      "alternative_facts": List[str],
      "warnings": List[str],
      "requires_human_review": bool
  }
  ```
- ✅ Compliance System:
  ```python
  ComplianceCheck = {
      "disclaimers": [
          "This is not financial advice. Please consult a qualified financial advisor.",
          "Past performance does not guarantee future results.",
          "Investments carry risk of loss. Only invest what you can afford to lose.",
          "This information is for educational purposes only.",
          "Market conditions can change rapidly. Recommendations may become outdated."
      ],
      "user_consent": {
          "data_collection": bool,
          "recommendations": bool,
          "data_sharing": bool,
          "analytics": bool,
          "consent_date": datetime,
          "consent_version": str
      },
      "regulatory_alignment": {
          "gdpr_compliant": bool,
          "financial_regulations": List[str],  # ["SEC", "FINRA", etc.]
          "data_retention_policy": str,
          "privacy_policy_url": str,
          "terms_of_service_url": str
      },
      "audit_log": {
          "recommendations_given": int,
          "disclaimers_shown": int,
          "user_consents": int,
          "compliance_violations": int
      }
  }
  ```
- ✅ Explainability Output:
  ```python
  Explanation = {
      "recommendation_id": str,
      "reasoning": str,
      "factors_considered": [
          {
              "factor": str,
              "weight": float,
              "impact": str
          }
      ],
      "risk_factors": [
          {
              "risk": str,
              "severity": str,
              "mitigation": str
          }
      ],
      "alternative_scenarios": [
          {
              "scenario": str,
              "outcome": str,
              "probability": float,
              "conditions": List[str]
          }
      ],
      "visual_explanation": str,  # Chart/image path
      "comparison": {
          "vs_market_average": dict,
          "vs_user_current_portfolio": dict,
          "vs_alternatives": dict
      }
  }
  ```
- ✅ Safety Filters:
  ```python
  SafetyFilterResult = {
      "passed": bool,
      "checks": [
          {
              "check_type": str,  # "content_moderation", "risk_warning", "unrealistic_expectation"
              "passed": bool,
              "message": str,
              "severity": str  # "low", "medium", "high"
          }
      ],
      "filtered_content": str,
      "original_content": str
  }
  ```

#### DELIVERABLES:
- Compliance module
- Fact-checking system
- Explainability features
- Safety filters
- Compliance documentation
- Audit logging system

---

### PHASE 7: INTEGRATION AND TESTING
**Duration:** Week 8-9

#### INPUTS:
- All modules from Phases 1-6
- Test cases
- User scenarios
- Performance benchmarks

#### PROCESSES:
1. Integrate all modules
2. End-to-end testing
3. Performance testing
4. User acceptance testing
5. Bug fixing
6. Optimization
7. Security testing
8. Load testing

#### OUTPUTS:
- ✅ Integrated System:
  - All modules connected
  - API endpoints functional
  - UI fully integrated
  - Database populated
  - Error handling comprehensive
- ✅ Test Results:
  ```python
  TestResults = {
      "unit_tests": {
          "total": int,
          "passed": int,
          "failed": int,
          "coverage": float,  # Target: >80%
          "details": List[dict]
      },
      "integration_tests": {
          "scenarios_tested": int,
          "success_rate": float,
          "failed_scenarios": List[dict]
      },
      "performance_tests": {
          "response_time": {
              "average": float,  # seconds
              "p50": float,
              "p95": float,
              "p99": float
          },
          "throughput": float,  # requests/second
          "concurrent_users": int,
          "resource_usage": {
              "cpu_percent": float,
              "memory_mb": float,
              "gpu_usage": float
          }
      },
      "user_acceptance": {
          "scenarios_passed": int,
          "scenarios_failed": int,
          "user_satisfaction": float,
          "feedback": List[str]
      },
      "security_tests": {
          "vulnerabilities_found": int,
          "vulnerabilities_fixed": int,
          "security_score": float
      }
  }
  ```
- ✅ Bug Reports
- ✅ Performance Optimization Report
- ✅ Integration documentation

#### DELIVERABLES:
- Fully integrated system
- Test suite
- Test results report
- Bug fixes documentation
- Performance optimization report

---

### PHASE 8: ANALYTICS AND EVALUATION
**Duration:** Week 9-10

#### INPUTS:
- System usage data
- User interactions
- Recommendations generated
- Expert benchmarks
- User feedback

#### PROCESSES:
1. Collect usage analytics
2. Calculate recommendation accuracy
3. Measure user engagement
4. Analyze performance metrics
5. Generate evaluation report
6. Create dashboards

#### OUTPUTS:
- ✅ Analytics Dashboard:
  ```python
  AnalyticsData = {
      "recommendation_accuracy": {
          "overall_accuracy": float,  # Target: 80%
          "by_category": {
              "investment": float,
              "retirement": float,
              "savings": float,
              "risk_assessment": float
          },
          "expert_alignment": float,
          "benchmark_comparison": {
              "traditional_advisor": float,
              "baseline_model": float,
              "improvement": float
          },
          "false_positives": int,
          "false_negatives": int
      },
      "user_engagement": {
          "active_users": int,
          "total_users": int,
          "sessions_per_user": float,
          "queries_per_session": float,
          "avg_session_duration": float,  # minutes
          "engagement_score": float,  # Target: 60% improvement
          "retention_rate": {
              "day_1": float,
              "day_7": float,
              "day_30": float
          },
          "feature_usage": {
              "chat_interface": int,
              "recommendations": int,
              "portfolio_review": int,
              "goal_tracking": int
          }
      },
      "performance_metrics": {
          "avg_response_time": float,  # seconds
          "plan_generation_time": {
              "before": float,
              "after": float,
              "reduction": float  # Target: 40%
          },
          "api_efficiency": {
              "calls_per_day": int,
              "cache_hit_rate": float,
              "error_rate": float
          },
          "system_uptime": float  # percentage
      },
      "user_satisfaction": {
          "overall_score": float,  # 1-5 scale
          "recommendation_quality": float,
          "usability": float,
          "trust": float,
          "response_accuracy": float,
          "nps_score": float,  # Net Promoter Score
          "feedback_summary": {
              "positive": List[str],
              "negative": List[str],
              "suggestions": List[str]
          }
      },
      "decision_making_effectiveness": {
          "recommendation_adoption_rate": float,
          "goal_achievement_rate": float,
          "portfolio_changes_made": int,
          "user_confidence": float
      }
  }
  ```
- ✅ Evaluation Report (see Final Deliverables section)

#### DELIVERABLES:
- Analytics dashboard
- Evaluation metrics
- Comparative analysis
- Final evaluation report
- Visualization dashboards

---

## DATA SPECIFICATIONS

### Alpha Vantage API Data Requirements

#### Stock Data:
- **Endpoints:** 
  - `TIME_SERIES_INTRADAY`: Real-time intraday data
  - `TIME_SERIES_DAILY`: Daily historical data
  - `TIME_SERIES_DAILY_ADJUSTED`: Adjusted daily data
- **Fields:** open, high, low, close, volume, adjusted_close
- **Frequency:** Real-time (1min, 5min, 15min, 30min, 60min) and daily
- **Symbols:** Major stocks (S&P 500, NASDAQ 100, Dow Jones)
- **Rate Limits:** 5 calls per minute, 500 calls per day (free tier)

#### Technical Indicators:
- **Endpoints:** 
  - `RSI`: Relative Strength Index
  - `MACD`: Moving Average Convergence Divergence
  - `BBANDS`: Bollinger Bands
  - `STOCH`: Stochastic Oscillator
  - `ADX`: Average Directional Index
  - `CCI`: Commodity Channel Index
- **Parameters:** Period, interval, series_type

#### Sector Performance:
- **Endpoint:** `SECTOR`
- **Data:** Real-time and historical sector performance percentages
- **Sectors:** Technology, Healthcare, Financial, Energy, etc.

#### Mutual Funds & ETFs:
- **Endpoints:** 
  - `MUTUAL_FUND`: Mutual fund data
  - `ETF`: ETF data
- **Data:** NAV, performance, holdings, expense ratios

#### Exchange Rates:
- **Endpoints:** 
  - `FX_INTRADAY`: Real-time FX data
  - `CURRENCY_EXCHANGE_RATE`: Exchange rate
  - `FX_DAILY`: Daily FX data
- **Pairs:** Major currency pairs (USD/EUR, USD/GBP, etc.)

#### Economic Indicators:
- **Endpoints:**
  - `REAL_GDP`: Real GDP
  - `INFLATION`: Inflation rate
  - `UNEMPLOYMENT`: Unemployment rate

### Financial News Data:
- **Sources:** 
  - Alpha Vantage News & Sentiment API
  - NewsAPI (financial news)
  - Financial Modeling Prep News API
- **Fields:** title, content, source, timestamp, sentiment
- **Frequency:** Real-time updates
- **Sentiment Analysis:** Positive, negative, neutral scores

### User Profile Data:
- **Collection Method:** Questionnaire, API input, form-based
- **Storage:** Database (encrypted)
- **Privacy:** GDPR compliant
- **Retention:** Per user consent and regulations

---

## API SPECIFICATIONS

### Internal API Endpoints

#### User Profile API:
```
POST /api/user/profile
  Request Body: {
    "email": str,
    "demographics": dict,
    "financial_goals": List[dict],
    "risk_tolerance": dict
  }
  Response: {
    "user_id": str,
    "profile_id": str,
    "status": "created"
  }

GET /api/user/profile/{user_id}
  Response: UserProfile

PUT /api/user/profile/{user_id}
  Request Body: Partial UserProfile
  Response: Updated UserProfile

DELETE /api/user/profile/{user_id}
  Response: {"status": "deleted"}
```

#### Recommendation API:
```
POST /api/recommendations/generate
  Request Body: {
    "user_id": str,
    "goal_id": str (optional),
    "context": dict (optional)
  }
  Response: Recommendation

GET /api/recommendations/{user_id}
  Query Params: limit, offset, status
  Response: {
    "recommendations": List[Recommendation],
    "total": int
  }

GET /api/recommendations/{rec_id}
  Response: Recommendation

PUT /api/recommendations/{rec_id}/feedback
  Request Body: {
    "feedback_score": int,
    "feedback_comment": str
  }
  Response: {"status": "updated"}
```

#### Chat API:
```
POST /api/chat/message
  Request Body: {
    "user_id": str,
    "message": str,
    "conversation_id": str (optional)
  }
  Response: {
    "conversation_id": str,
    "response": LLMResponse,
    "message_id": str
  }

GET /api/chat/history/{user_id}
  Query Params: limit, offset
  Response: {
    "conversations": List[ConversationHistory],
    "total": int
  }

GET /api/chat/conversation/{conversation_id}
  Response: ConversationHistory

DELETE /api/chat/conversation/{conversation_id}
  Response: {"status": "deleted"}
```

#### Market Data API:
```
GET /api/market/stock/{symbol}
  Query Params: interval, outputsize
  Response: StockData

GET /api/market/sector
  Response: List[SectorData]

GET /api/market/news
  Query Params: symbols, limit
  Response: List[NewsData]

GET /api/market/indicators/{symbol}
  Query Params: function (RSI, MACD, etc.), interval
  Response: IndicatorData

GET /api/market/etf/{symbol}
  Response: ETFData

GET /api/market/mutual-fund/{symbol}
  Response: MutualFundData
```

#### Analytics API:
```
GET /api/analytics/dashboard
  Query Params: start_date, end_date
  Response: AnalyticsData

GET /api/analytics/user/{user_id}
  Response: UserAnalytics
```

### External APIs:
- **Alpha Vantage API**: https://www.alphavantage.co/documentation/
- **OpenAI/FinGPT API**: Model inference
- **Pinecone API**: Vector database operations
- **NewsAPI**: Financial news (optional)
- **Financial Modeling Prep**: Additional market data (optional)

### API Authentication:
- **Method:** API keys or JWT tokens
- **Rate Limiting:** Per user/IP
- **Error Handling:** Standard HTTP status codes
- **Response Format:** JSON

---

## MODEL SPECIFICATIONS

### Base Model Options:

#### 1. FinGPT (Recommended)
- **Models Available:**
  - `FinGPT/fingpt-forecaster_dow30_llama2-7b-lora`: For forecasting
  - `FinGPT/fingpt-analyzer`: For analysis
  - `FinGPT/fingpt-sentiment`: For sentiment analysis
- **Advantages:**
  - Pre-trained on financial data
  - Open-source
  - Fine-tuning support
  - Cost-effective
- **Repository:** https://github.com/AI4Finance-Foundation/FinGPT
- **Fine-tuning:** LoRA (Low-Rank Adaptation) recommended

#### 2. GPT-4 (Alternative)
- **Advantages:**
  - Strong general capabilities
  - Excellent reasoning
  - API-based (no local training needed)
- **Disadvantages:**
  - Higher cost
  - API dependency
  - Less financial domain-specific

#### 3. Other Options:
- **BloombergGPT**: Not publicly available
- **FinBERT**: For sentiment analysis
- **Custom fine-tuned models**: Based on specific needs

### Fine-Tuning Parameters:
```python
TrainingConfig = {
    "base_model": "FinGPT/fingpt-forecaster_dow30_llama2-7b-lora",
    "learning_rate": 2e-5,
    "batch_size": 8,
    "gradient_accumulation_steps": 4,
    "num_epochs": 5,
    "max_seq_length": 1024,
    "warmup_steps": 100,
    "weight_decay": 0.01,
    "optimizer": "AdamW",
    "lr_scheduler": "cosine",
    "save_steps": 500,
    "eval_steps": 250,
    "logging_steps": 50,
    "fp16": True,  # Mixed precision training
    "gradient_checkpointing": True
}
```

### Embedding Model:
- **Model:** `sentence-transformers/all-MiniLM-L6-v2` or `all-mpnet-base-v2`
- **Dimension:** 384 (MiniLM) or 768 (mpnet)
- **Use Case:** User profiles, investment instruments, knowledge base
- **Alternative:** OpenAI embeddings (`text-embedding-ada-002`)

### Model Evaluation Metrics:
- **Accuracy:** Percentage of correct recommendations
- **BLEU Score:** For text generation quality
- **ROUGE Score:** For summarization
- **Perplexity:** Model confidence
- **Hallucination Rate:** Factual errors
- **Response Time:** Inference speed

---

## SUCCESS METRICS & EVALUATION

### Recommendation Accuracy (Target: 80%)
**Measurement:**
- Compare recommendations with expert financial advisor benchmarks
- Use test dataset with known optimal recommendations
- Calculate accuracy = (correct_recommendations / total_recommendations) * 100

**Evaluation Dataset:**
- 100+ scenarios with expert-validated recommendations
- Diverse user profiles and goals
- Multiple market conditions
- Different risk profiles

**Evaluation Method:**
1. Create test scenarios with known optimal recommendations
2. Generate recommendations using the system
3. Compare with expert benchmarks
4. Calculate accuracy metrics
5. Analyze false positives and false negatives

### User Engagement Improvement (Target: 60%)
**Baseline Metrics:**
- Average sessions per user
- Queries per session
- Time spent on platform
- Return rate
- Feature usage

**Measurement:**
- Track pre/post implementation metrics
- Improvement = ((new_metric - baseline_metric) / baseline_metric) * 100

**Tracking:**
- User activity logs
- Session analytics
- Feature usage statistics
- Retention rates

### Time Reduction (Target: 40%)
**Measurement:**
- Time to generate investment plan (before vs. after)
- Reduction = ((old_time - new_time) / old_time) * 100

**Baseline:**
- Traditional advisor consultation: ~2-4 hours
- Manual research: ~4-8 hours

**Target:**
- AI system: ~15-30 minutes
- Reduction: 40-60%

### User Satisfaction
**Measurement:**
- Survey scores (1-5 scale)
- Net Promoter Score (NPS)
- User feedback analysis
- Recommendation adoption rate

**Survey Questions:**
1. How satisfied are you with the recommendations? (1-5)
2. How accurate were the recommendations? (1-5)
3. How easy was it to use the system? (1-5)
4. Would you recommend this to others? (NPS)
5. How likely are you to follow the recommendations? (1-5)

---

## DELIVERABLES CHECKLIST

### Final Deliverable 1: Functional System
- [ ] Complete codebase with all modules
- [ ] Deployed application (Streamlit/web interface)
- [ ] API endpoints functional
- [ ] Database with sample data
- [ ] User interface (Streamlit) fully functional
- [ ] All modules integrated
- [ ] Error handling implemented
- [ ] Logging system
- [ ] Authentication system
- [ ] Data caching system
- [ ] Rate limiting implemented
- [ ] Documentation strings in code

### Final Deliverable 2: Comprehensive Documentation
- [ ] Executive Summary
- [ ] System Architecture Document
  - [ ] High-level architecture diagram
  - [ ] Component interaction flows
  - [ ] Data flow diagrams
  - [ ] Technology stack justification
- [ ] Dataset Sources Documentation
  - [ ] Alpha Vantage API usage
  - [ ] Data collection methodology
  - [ ] Data preprocessing steps
  - [ ] Sample data examples
- [ ] Model Fine-Tuning Methodology
  - [ ] Base model selection rationale
  - [ ] Training data preparation
  - [ ] Fine-tuning process
  - [ ] Hyperparameters and configuration
  - [ ] Evaluation metrics and results
- [ ] Personalization and Recommendation Logic
  - [ ] User profiling approach
  - [ ] Embedding methodology
  - [ ] Recommendation algorithms
  - [ ] Asset allocation logic
  - [ ] Risk assessment models
- [ ] RAG Pipeline Architecture
  - [ ] Retrieval strategy
  - [ ] Context injection mechanism
  - [ ] Prompt engineering approach
  - [ ] Response generation process
- [ ] Compliance and Guardrails
  - [ ] Regulatory compliance measures
  - [ ] Hallucination prevention strategies
  - [ ] Safety filters implementation
  - [ ] Explainability features
- [ ] API Documentation
  - [ ] Endpoint specifications
  - [ ] Request/response formats
  - [ ] Authentication methods
  - [ ] Rate limiting policies
  - [ ] Error codes
- [ ] User Guide
  - [ ] System usage instructions
  - [ ] Feature walkthrough
  - [ ] FAQ section
  - [ ] Troubleshooting guide
- [ ] Deployment Guide
  - [ ] Environment setup
  - [ ] Installation steps
  - [ ] Configuration instructions
  - [ ] Troubleshooting guide
- [ ] Code comments and docstrings

### Final Deliverable 3: Analytical Report
- [ ] Executive Summary
  - [ ] Key findings
  - [ ] Success metrics achievement
  - [ ] Business impact
- [ ] Recommendation Accuracy Analysis
  - [ ] Methodology for accuracy measurement
  - [ ] Expert benchmark comparison
  - [ ] Accuracy percentage achieved (target: 80%)
  - [ ] Case studies of recommendations
  - [ ] False positive/negative analysis
  - [ ] Per-category accuracy breakdown
- [ ] User Engagement Metrics
  - [ ] Engagement tracking methodology
  - [ ] User satisfaction scores (target: 60% improvement)
  - [ ] Active user statistics
  - [ ] Feature usage analytics
  - [ ] User feedback summary
  - [ ] Retention rates
- [ ] Performance Metrics
  - [ ] Time-to-generate-plan analysis (target: 40% reduction)
  - [ ] System response times
  - [ ] API efficiency metrics
  - [ ] Resource utilization
  - [ ] Scalability analysis
- [ ] Decision-Making Effectiveness
  - [ ] User decision outcomes
  - [ ] Recommendation adoption rates
  - [ ] Goal achievement tracking
  - [ ] Financial outcome analysis (if available)
- [ ] Comparative Analysis
  - [ ] Before/after comparison
  - [ ] Traditional advisor vs. AI advisor
  - [ ] Cost-benefit analysis
  - [ ] Competitive analysis
- [ ] Limitations and Future Work
  - [ ] Current limitations
  - [ ] Areas for improvement
  - [ ] Future enhancement roadmap
- [ ] Visualizations
  - [ ] Charts and graphs for all metrics
  - [ ] Dashboard screenshots
  - [ ] Trend analysis visualizations
  - [ ] Comparative charts

---

## TECHNICAL STACK

### Core Technologies:
- **Language:** Python 3.9+
- **LLM Framework:** LangChain
- **Model:** FinGPT / GPT-4
- **Vector DB:** Pinecone / Chroma
- **UI Framework:** Streamlit
- **Data Processing:** Pandas, NumPy
- **ML Framework:** Hugging Face Transformers, PyTorch
- **API Integration:** Requests, Alpha Vantage SDK
- **Database:** PostgreSQL / MongoDB
- **Visualization:** Plotly, Matplotlib, Seaborn
- **Automation:** N8N (optional)
- **Testing:** pytest, unittest
- **Logging:** Python logging, Loguru

### Libraries and Packages:
```python
# Core dependencies
langchain>=0.1.0
openai>=1.0.0
pinecone-client>=2.0.0
streamlit>=1.28.0
pandas>=2.0.0
numpy>=1.24.0

# ML/AI
transformers>=4.35.0
torch>=2.1.0
sentence-transformers>=2.2.0
accelerate>=0.24.0
peft>=0.6.0  # For LoRA fine-tuning

# Data collection
alpha-vantage>=2.3.0
requests>=2.31.0
beautifulsoup4>=4.12.0
feedparser>=6.0.0

# Database
psycopg2-binary>=2.9.0  # PostgreSQL
pymongo>=4.5.0  # MongoDB
sqlalchemy>=2.0.0

# Visualization
plotly>=5.17.0
matplotlib>=3.7.0
seaborn>=0.12.0

# Utilities
python-dotenv>=1.0.0
pydantic>=2.0.0
pyyaml>=6.0.0
tqdm>=4.66.0

# Testing
pytest>=7.4.0
pytest-cov>=4.1.0
```

### Infrastructure:
- **Version Control:** Git
- **Containerization:** Docker, Docker Compose
- **Environment Management:** venv / conda
- **Configuration:** YAML files
- **Secrets Management:** .env files, environment variables
- **CI/CD:** GitHub Actions (optional)
- **Monitoring:** Logging, basic metrics

### Development Tools:
- **IDE:** VS Code, PyCharm
- **Notebooks:** Jupyter, Google Colab
- **API Testing:** Postman, curl
- **Database Management:** pgAdmin, MongoDB Compass

---

## EXISTING SOLUTIONS & RESEARCH

### Research Findings (Updated January 2025)

#### Financial LLM Models:

1. **FinGPT** (AI4Finance Foundation) - **RECOMMENDED**
   - **GitHub:** https://github.com/AI4Finance-Foundation/FinGPT
   - **Description:** Open-source financial LLM emphasizing data-centric approach
   - **Models Available:**
     - `FinGPT/fingpt-forecaster_dow30_llama2-7b-lora`: For forecasting
     - `FinGPT/fingpt-analyzer`: For financial analysis
     - `FinGPT/fingpt-sentiment`: For sentiment analysis
   - **Advantages:**
     - Pre-trained on financial data
     - Open-source and free
     - Supports LoRA fine-tuning
     - Multiple specialized variants
   - **Use Case:** Primary model for fine-tuning
   - **Paper:** https://arxiv.org/abs/2306.06031

2. **Fin-Ally**
   - **Description:** Advanced conversational AI for financial matters
   - **Features:**
     - Multi-turn financial conversational dataset (Fin-Vault)
     - Commonsense reasoning integration
     - Human-like conversational dynamics
     - Personalized budgeting and financial planning
   - **Technology:** COMET-BART-embedded commonsense context
   - **Optimization:** Direct Preference Optimization (DPO)
   - **Paper:** https://arxiv.org/abs/2509.24342
   - **Use Case:** Reference for conversational design patterns

3. **WeaverBird**
   - **Description:** Intelligent dialogue system for finance domain
   - **Features:**
     - GPT-based LLM fine-tuned on finance text
     - Local knowledge base integration
     - Search engine for information retrieval
     - Proper citation system
   - **Advantages:**
     - Superior performance on complex financial queries
     - Information retrieval with citations
   - **Paper:** https://arxiv.org/abs/2308.05361
   - **Use Case:** Reference for RAG implementation patterns

4. **BloombergGPT**
   - Proprietary model by Bloomberg
   - Not publicly available
   - Trained on extensive financial data
   - **Note:** Cannot be used directly, but serves as benchmark

5. **FinBERT**
   - Financial sentiment analysis model
   - Based on BERT architecture
   - Available on Hugging Face
   - **Use Case:** Sentiment analysis for news and market data

6. **ConFIRM (Conversational Factor Information Retrieval Model)**
   - **Description:** Fine-tuning approach for domain-specific retrieval
   - **Method:** Uses Five-Factor Model of personality for synthetic dataset generation
   - **Performance:** 91% accuracy in classifying financial queries
   - **Paper:** https://arxiv.org/abs/2310.13001
   - **Use Case:** Reference for query classification and personalization

#### Open-Source Platforms and Tools:

1. **FinWorld**
   - **Description:** Open-source platform for end-to-end financial AI workflow
   - **Features:**
     - Data acquisition to deployment support
     - Heterogeneous financial data integration
     - Multiple AI paradigms (LLMs, RL, etc.)
     - Reproducibility and benchmarking
   - **Paper:** https://arxiv.org/abs/2508.02292
   - **GitHub:** Check for availability
   - **Use Case:** Reference architecture for financial AI systems

2. **FinRobot**
   - **Description:** AI agent platform for financial applications using LLMs
   - **Features:** Structured approach to financial analysis tasks
   - **Paper:** https://arxiv.org/abs/2405.14767
   - **Use Case:** Reference for agent-based architecture

3. **FinCon**
   - **Description:** LLM-based multi-agent framework for financial tasks
   - **Features:** Conceptual verbal reinforcement for decision-making
   - **Paper:** https://arxiv.org/abs/2407.06567
   - **Use Case:** Multi-agent system reference

#### Commercial AI Financial Advisory Tools (Reference):

1. **Anthropic's Claude for Financial Services**
   - Specialized AI platform for financial industry
   - Features: Market research, due diligence, investment decisions
   - Integration: Databricks, Snowflake
   - **Key Learning:** Enterprise data integration patterns
   - **Source:** https://www.techradar.com/pro/anthropic-launches-claude-for-financial-services

2. **Vise AI**
   - Automated portfolio management
   - Personalized portfolios and rebalancing
   - **Key Learning:** Portfolio automation patterns

3. **Orion Advisor Solutions**
   - Integrated reporting, planning, and CRM
   - AI-enhanced reporting accuracy
   - **Key Learning:** Integration patterns for advisor tools

4. **Wealthfront**
   - Robo-advisor with automated portfolios
   - Goal-based planning
   - Tax-loss harvesting
   - **Key Learning:** Robo-advisor UX patterns

5. **Ellevest**
   - Gender-aware investment algorithm
   - Goal-based planning
   - **Key Learning:** Personalization approaches

6. **SigFig**
   - Robo-advisory platform
   - White-label solutions
   - **Key Learning:** Scalable architecture patterns

#### RAG Implementation Resources:

1. **LangChain RAG Patterns**
   - **Documentation:** https://python.langchain.com/docs/use_cases/question_answering/
   - **Components:**
     - Document loaders
     - Text splitters
     - Vector stores (Pinecone, Chroma, FAISS)
     - Retrievers
     - Chains
   - **Best Practices:**
     - Use appropriate chunk sizes (500-1000 tokens)
     - Implement reranking for better results
     - Combine multiple retrieval strategies
     - Add metadata filtering

2. **LlamaIndex for Financial Data**
   - **Use Case:** Financial document indexing and retrieval
   - **Features:** Specialized for structured data queries
   - **Documentation:** https://docs.llamaindex.ai/

3. **Pinecone Vector Database**
   - **Documentation:** https://docs.pinecone.io/
   - **Features:**
     - Managed vector database
     - High scalability
     - Metadata filtering
     - Hybrid search support
   - **Best Practices:**
     - Use appropriate dimensions (384 or 768)
     - Implement metadata filtering
     - Set up proper indexing
     - Monitor usage and costs

#### Alpha Vantage API Integration:

1. **Official Python SDK**
   - **Package:** `alpha_vantage`
   - **Installation:** `pip install alpha-vantage`
   - **Documentation:** https://www.alphavantage.co/documentation/
   - **Rate Limits:**
     - Free tier: 5 calls/minute, 500 calls/day
     - Premium tiers available

2. **Best Practices:**
   - **Caching:** Implement Redis or file-based caching
   - **Rate Limiting:** Use token bucket or sliding window
   - **Error Handling:** Implement retry logic with exponential backoff
   - **Data Validation:** Validate API responses
   - **Batch Processing:** Group requests when possible

3. **Example Implementation:**
   ```python
   from alpha_vantage.timeseries import TimeSeries
   import time
   
   class AlphaVantageClient:
       def __init__(self, api_key):
           self.ts = TimeSeries(key=api_key)
           self.last_call_time = 0
           self.min_interval = 12  # 5 calls per minute = 12 seconds
       
       def get_stock_data(self, symbol):
           # Rate limiting
           elapsed = time.time() - self.last_call_time
           if elapsed < self.min_interval:
               time.sleep(self.min_interval - elapsed)
           
           data, meta = self.ts.get_daily(symbol=symbol)
           self.last_call_time = time.time()
           return data
   ```

#### Additional Data Sources:

1. **QuantConnect**
   - **Description:** Platform for financial datasets
   - **Data Types:** Equities, FX, futures, options, cryptocurrencies
   - **Use Case:** Additional data source for training

2. **Financial Modeling Prep**
   - **Description:** Financial data API
   - **Features:** Stock data, financial statements, news
   - **Use Case:** Alternative/complementary data source

3. **NewsAPI**
   - **Description:** News aggregation API
   - **Features:** Financial news filtering
   - **Use Case:** News sentiment analysis

#### Implementation Patterns to Adopt:

1. **From Fin-Ally:**
   - Multi-turn conversation handling
   - Commonsense reasoning integration
   - Human-like conversational dynamics

2. **From WeaverBird:**
   - Local knowledge base integration
   - Search engine for information retrieval
   - Citation system for responses

3. **From FinWorld:**
   - End-to-end workflow design
   - Heterogeneous data integration
   - Reproducibility patterns

4. **From ConFIRM:**
   - Query classification approach
   - Personality-based personalization
   - Synthetic dataset generation

#### Compliance and Regulatory Resources:

1. **SEC Regulations:**
   - Investment Advisers Act of 1940
   - Robo-advisor guidance
   - Fiduciary duty requirements

2. **FINRA Regulations:**
   - Suitability requirements
   - Disclosure obligations
   - Record-keeping requirements

3. **GDPR Compliance:**
   - Data protection requirements
   - User consent management
   - Right to deletion

#### Useful GitHub Repositories:

1. **FinGPT:** https://github.com/AI4Finance-Foundation/FinGPT
2. **LangChain Examples:** https://github.com/langchain-ai/langchain
3. **Financial Data Tools:** Search GitHub for "financial-data", "stock-analysis"
4. **RAG Implementations:** Search for "rag-pipeline", "retrieval-augmented-generation"

#### Research Papers to Reference:

1. FinGPT: https://arxiv.org/abs/2306.06031
2. Fin-Ally: https://arxiv.org/abs/2509.24342
3. WeaverBird: https://arxiv.org/abs/2308.05361
4. FinWorld: https://arxiv.org/abs/2508.02292
5. ConFIRM: https://arxiv.org/abs/2310.13001
6. FinRobot: https://arxiv.org/abs/2405.14767
7. FinCon: https://arxiv.org/abs/2407.06567

#### Key Takeaways for Implementation:

1. **Leverage FinGPT:** Use as base model for fine-tuning
2. **Implement RAG:** Use LangChain + Pinecone for factual grounding
3. **Adopt Conversational Patterns:** Learn from Fin-Ally and WeaverBird
4. **Integrate Multiple Data Sources:** Alpha Vantage + News APIs
5. **Focus on Personalization:** Use ConFIRM approach for user profiling
6. **Ensure Compliance:** Follow SEC/FINRA guidelines
7. **Build Scalable Architecture:** Reference FinWorld patterns
8. **Implement Proper Citations:** Like WeaverBird for transparency

---

## IMPLEMENTATION BEST PRACTICES

### Code Quality:
- Follow PEP 8 style guide
- Use type hints
- Write comprehensive docstrings
- Implement error handling
- Add logging throughout

### Security:
- Never commit API keys
- Use environment variables
- Encrypt sensitive data
- Implement authentication
- Validate all inputs

### Performance:
- Implement caching
- Optimize database queries
- Use async/await where appropriate
- Monitor resource usage
- Profile code for bottlenecks

### Testing:
- Write unit tests for all modules
- Implement integration tests
- Test edge cases
- Maintain >80% code coverage
- Use mocking for external APIs

### Documentation:
- Keep documentation updated
- Include examples
- Document API endpoints
- Provide user guides
- Maintain changelog

---

## ASSUMPTIONS & CONSTRAINTS

### Assumptions:
1. Alpha Vantage API access available (free tier sufficient for development)
2. Sufficient API rate limits for testing
3. User provides accurate profile information
4. Market data is reliable and timely
5. Financial regulations allow AI advisory (with disclaimers)
6. Users have basic financial literacy
7. Internet connectivity available
8. Sufficient computational resources for model inference

### Constraints:
1. **API Rate Limits:**
   - Alpha Vantage: 5 calls/min, 500 calls/day (free tier)
   - OpenAI: Rate limits based on tier
   - Pinecone: Based on plan

2. **Model Inference Costs:**
   - GPT-4 API: Pay per token
   - FinGPT: Local inference (compute costs)
   - Embeddings: Cost per request

3. **Data Storage:**
   - Database size limits
   - Vector database storage limits
   - File storage for models

4. **Real-time Data:**
   - API availability
   - Network latency
   - Data freshness

5. **Compliance Requirements:**
   - Vary by region
   - GDPR, SEC, FINRA regulations
   - Data retention policies

### Risks & Mitigations:
| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| API rate limits | High | Medium | Implement caching, batch processing, upgrade API tier |
| Model hallucinations | High | Medium | RAG pipeline, fact-checking, source verification |
| Data quality issues | Medium | Medium | Data validation, multiple sources, error handling |
| Regulatory compliance | High | Low | Legal review, disclaimers, compliance checks |
| User privacy concerns | Medium | Medium | GDPR compliance, encryption, consent management |
| Model performance | High | Medium | Extensive testing, fine-tuning, evaluation |
| Scalability issues | Medium | Low | Load testing, optimization, cloud deployment |
| Cost overruns | Medium | Medium | Monitor usage, optimize API calls, use caching |

---

## PROJECT TIMELINE

| Phase | Duration | Start Week | End Week | Dependencies |
|-------|----------|------------|----------|--------------|
| Phase 1: Setup | 2 weeks | Week 1 | Week 2 | None |
| Phase 2: Data Collection | 1 week | Week 2 | Week 3 | Phase 1 |
| Phase 3: Model Training | 2 weeks | Week 3 | Week 5 | Phase 2 |
| Phase 4: Personalization | 1 week | Week 5 | Week 6 | Phase 3 |
| Phase 5: RAG & Chat | 1 week | Week 6 | Week 7 | Phase 3, 4 |
| Phase 6: Compliance | 1 week | Week 7 | Week 8 | Phase 5 |
| Phase 7: Integration | 1 week | Week 8 | Week 9 | All phases |
| Phase 8: Analytics | 1 week | Week 9 | Week 10 | Phase 7 |

**Total Duration:** 10 weeks

### Critical Path:
Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5 → Phase 6 → Phase 7 → Phase 8

### Parallel Work:
- Phase 4 and Phase 5 can partially overlap
- Documentation can be written in parallel with development
- Testing can start early with unit tests

---

## KEY DECISIONS LOG

### Decision 1: Model Selection
**Date:** 13-11-2025
**Decision:** Use FinGPT for domain-specific knowledge
**Rationale:** Pre-trained on financial data, open-source, cost-effective
**Alternatives Considered:** GPT-4, Claude, Custom model
**Impact:** Affects fine-tuning approach and costs

### Decision 2: Vector Database
**Date:** 13-11-2025
**Decision:** Use Pinecone for production, Chroma for development
**Rationale:** Pinecone offers better scalability and performance
**Alternatives Considered:** FAISS, Weaviate, Qdrant
**Impact:** Affects RAG pipeline implementation

### Decision 3: UI Framework
**Date:** 13-11-2025
**Decision:** Streamlit for rapid prototyping
**Rationale:** Fast development, good for ML apps, easy deployment
**Alternatives Considered:** Flask, React, Vue.js
**Impact:** Affects development speed and user experience

### Decision 4: Database Choice
**Date:** 13-11-2025
**Decision:** PostgreSQL for structured data
**Rationale:** Robust, ACID compliant, good for financial data
**Alternatives Considered:** MongoDB, SQLite
**Impact:** Affects data modeling and queries

---

## NOTES & OBSERVATIONS

### Technical Notes:
- [Add any technical insights, challenges, solutions as project progresses]

### Business Notes:
- [Add business considerations, market insights]

### Future Enhancements:
- Voice assistant integration
- Mobile app development
- Multi-language support
- Advanced portfolio optimization
- Real-time alerts and notifications
- Integration with banking APIs
- Tax optimization features
- Estate planning capabilities

---

## CONTACTS & RESOURCES

### API Documentation:
- **Alpha Vantage:** https://www.alphavantage.co/documentation/
- **OpenAI:** https://platform.openai.com/docs
- **LangChain:** https://python.langchain.com/
- **Pinecone:** https://docs.pinecone.io/
- **FinGPT:** https://github.com/AI4Finance-Foundation/FinGPT
- **Hugging Face:** https://huggingface.co/docs

### Reference Materials:
- Financial regulations: [To be added]
- Expert benchmarks: [To be added]
- Training datasets: [To be added]
- Research papers: [To be added]

### Community Resources:
- FinGPT Discord/Community
- LangChain Discord
- Financial AI forums
- Stack Overflow

---

**Document Version:** 1.0
**Maintained By:** Richard
**Last Review:** 13-11-2025
**Next Review:** 15-11-2025

---

## QUICK REFERENCE GUIDE

### Essential Code Snippets

#### 1. Alpha Vantage Client Setup
```python
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.techindicators import TechIndicators
import time
import os

class AlphaVantageClient:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('ALPHA_VANTAGE_API_KEY')
        self.ts = TimeSeries(key=self.api_key)
        self.ti = TechIndicators(key=self.api_key)
        self.last_call_time = 0
        self.min_interval = 12  # 5 calls per minute
    
    def get_daily_data(self, symbol):
        """Get daily stock data with rate limiting"""
        elapsed = time.time() - self.last_call_time
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        
        data, meta = self.ts.get_daily(symbol=symbol, outputsize='full')
        self.last_call_time = time.time()
        return data, meta
    
    def get_rsi(self, symbol, interval='daily', time_period=14):
        """Get RSI indicator"""
        elapsed = time.time() - self.last_call_time
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        
        data, meta = self.ti.get_rsi(symbol=symbol, interval=interval, 
                                     time_period=time_period, series_type='close')
        self.last_call_time = time.time()
        return data, meta
```

#### 2. LangChain RAG Setup
```python
from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Pinecone
from langchain.llms import OpenAI
from langchain.chains import RetrievalQA
import pinecone

# Initialize embeddings
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Initialize Pinecone
pinecone.init(
    api_key=os.getenv('PINECONE_API_KEY'),
    environment=os.getenv('PINECONE_ENV')
)

# Create vector store
vectorstore = Pinecone.from_existing_index(
    index_name="financial-advisor",
    embedding=embeddings
)

# Create retriever
retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 5}
)

# Create QA chain
llm = OpenAI(temperature=0)
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever,
    return_source_documents=True
)
```

#### 3. User Profile Embedding
```python
from sentence_transformers import SentenceTransformer
import json

class UserProfileEmbedder:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
    
    def create_profile_text(self, profile):
        """Convert profile to text for embedding"""
        text_parts = [
            f"Age: {profile['demographics']['age']}",
            f"Income: ${profile['demographics']['income']:,.0f}",
            f"Risk tolerance: {profile['risk_tolerance']['category']}",
            f"Investment experience: {profile['investment_experience']}"
        ]
        
        for goal in profile['financial_goals']:
            text_parts.append(
                f"Goal: {goal['type']}, "
                f"Target: ${goal['target_amount']:,.0f}, "
                f"Timeframe: {goal['time_horizon']} years"
            )
        
        return " ".join(text_parts)
    
    def embed_profile(self, profile):
        """Generate embedding for user profile"""
        profile_text = self.create_profile_text(profile)
        embedding = self.model.encode(profile_text)
        return embedding.tolist()
```

#### 4. FinGPT Fine-Tuning Setup
```python
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import LoraConfig, get_peft_model, TaskType
import torch

def setup_fingpt_model(model_name="FinGPT/fingpt-forecaster_dow30_llama2-7b-lora"):
    """Setup FinGPT model with LoRA for fine-tuning"""
    
    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    
    # Load model
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16,
        device_map="auto"
    )
    
    # Configure LoRA
    lora_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=16,
        lora_alpha=32,
        lora_dropout=0.1,
        target_modules=["q_proj", "v_proj"]
    )
    
    # Apply LoRA
    model = get_peft_model(model, lora_config)
    
    return model, tokenizer
```

#### 5. Streamlit Chat Interface
```python
import streamlit as st
from src.rag_pipeline.response_generator import generate_response

st.title("AI Financial Advisor")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask me about your finances..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate response
    with st.chat_message("assistant"):
        response = generate_response(prompt, st.session_state.get("user_id"))
        st.markdown(response["text"])
        if response.get("sources"):
            with st.expander("Sources"):
                for source in response["sources"]:
                    st.write(f"- {source}")
    
    st.session_state.messages.append({
        "role": "assistant", 
        "content": response["text"]
    })
```

#### 6. Recommendation Engine
```python
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class RecommendationEngine:
    def __init__(self, embedding_model):
        self.embedding_model = embedding_model
        self.instruments = self.load_instruments()
    
    def load_instruments(self):
        """Load investment instruments with embeddings"""
        # Load from database or file
        return [
            {"symbol": "SPY", "type": "ETF", "embedding": [...], "risk": "medium"},
            # ... more instruments
        ]
    
    def recommend(self, user_profile, top_k=5):
        """Generate recommendations based on user profile"""
        # Get user embedding
        user_embedding = self.embedding_model.embed_profile(user_profile)
        
        # Calculate similarities
        similarities = []
        for instrument in self.instruments:
            sim = cosine_similarity(
                [user_embedding],
                [instrument["embedding"]]
            )[0][0]
            similarities.append({
                "instrument": instrument,
                "similarity": sim
            })
        
        # Sort by similarity
        similarities.sort(key=lambda x: x["similarity"], reverse=True)
        
        # Return top recommendations
        return similarities[:top_k]
```

### Quick Start Commands

#### Environment Setup
```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

#### Database Setup
```bash
# PostgreSQL
createdb financial_advisor
psql financial_advisor < schema.sql

# Or using SQLAlchemy
python scripts/init_database.py
```

#### Run Application
```bash
# Development
streamlit run ui/streamlit_app.py

# Production
gunicorn api.app:app
```

### Key File Locations Reference

- **Configuration:** `config/config.yaml`
- **Environment Variables:** `.env`
- **API Keys:** `.env` (never commit)
- **Database Schema:** `docs/schema.sql`
- **Model Weights:** `models/fine_tuned/`
- **Data Cache:** `data/cache/`
- **Logs:** `logs/`

### Common Tasks

#### Add New Data Source
1. Create client in `src/data_collection/`
2. Add to data pipeline
3. Update data schema
4. Add caching logic

#### Fine-tune Model
1. Prepare training data in `data/processed/`
2. Run `python scripts/train_model.py`
3. Evaluate with `python scripts/evaluate_model.py`
4. Deploy updated model

#### Add New Recommendation Type
1. Update recommendation engine
2. Add visualization component
3. Update API endpoints
4. Add tests

---

## APPENDIX

### A. Glossary of Terms
- **LLM:** Large Language Model
- **RAG:** Retrieval-Augmented Generation
- **ETF:** Exchange-Traded Fund
- **NAV:** Net Asset Value
- **RSI:** Relative Strength Index
- **MACD:** Moving Average Convergence Divergence
- **LoRA:** Low-Rank Adaptation
- **API:** Application Programming Interface
- **GDPR:** General Data Protection Regulation
- **SEC:** Securities and Exchange Commission
- **FINRA:** Financial Industry Regulatory Authority

### B. Abbreviations
- **QA:** Question Answering
- **NPS:** Net Promoter Score
- **UI:** User Interface
- **UX:** User Experience
- **ML:** Machine Learning
- **AI:** Artificial Intelligence
- **NLP:** Natural Language Processing

### C. File Naming Conventions
- Python files: `snake_case.py`
- Configuration files: `kebab-case.yaml`
- Documentation: `UPPER_SNAKE_CASE.md`
- Test files: `test_*.py`

---

*End of Documentation*

