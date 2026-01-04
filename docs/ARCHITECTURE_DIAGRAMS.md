# System Architecture Diagrams
## AI-Powered Financial Advisor

**Last Updated:** January 2025

---

## 1. High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER INTERFACE LAYER                         │
│  ┌──────────────────┐  ┌──────────────────┐                   │
│  │  Streamlit UI    │  │   REST API       │                   │
│  │  (Chat Interface)│  │   (FastAPI)     │                   │
│  └────────┬─────────┘  └────────┬─────────┘                   │
└───────────┼──────────────────────┼─────────────────────────────┘
            │                      │
            ▼                      ▼
┌─────────────────────────────────────────────────────────────────┐
│              ADVISORY CHAT INTERFACE (RAG)                      │
│  ┌──────────────────┐  ┌──────────────────┐                   │
│  │ Query            │  │ Response         │                   │
│  │ Understanding    │  │ Generator        │                   │
│  └────────┬─────────┘  └────────┬─────────┘                   │
│           │                      │                              │
│           ▼                      ▼                              │
│  ┌──────────────────┐  ┌──────────────────┐                   │
│  │ RAG Retriever    │  │ Vector Store     │                   │
│  │ (Context)        │  │ (Embeddings)     │                   │
│  └──────────────────┘  └──────────────────┘                   │
└───────────┬──────────────────────┬─────────────────────────────┘
            │                      │
            ▼                      ▼
┌─────────────────────────────────────────────────────────────────┐
│              PERSONALIZATION ENGINE                             │
│  ┌──────────────────┐  ┌──────────────────┐                   │
│  │ User Profiler    │  │ Risk Assessor    │                   │
│  └────────┬─────────┘  └────────┬─────────┘                   │
│           │                      │                              │
│           ▼                      ▼                              │
│  ┌──────────────────┐  ┌──────────────────┐                   │
│  │ Recommendation  │  │ Goal Planner     │                   │
│  │ Engine           │  │                  │                   │
│  └──────────────────┘  └──────────────────┘                   │
└───────────┬──────────────────────┬─────────────────────────────┘
            │                      │
            ▼                      ▼
┌─────────────────────────────────────────────────────────────────┐
│              FINE-TUNED LLM MODEL                               │
│  ┌──────────────────┐  ┌──────────────────┐                   │
│  │ Mistral-7B      │  │ Inference       │                   │
│  │ (Fine-tuned)     │  │ Engine          │                   │
│  └────────┬─────────┘  └────────┬─────────┘                   │
└───────────┬──────────────────────┬─────────────────────────────┘
            │                      │
            ▼                      ▼
┌─────────────────────────────────────────────────────────────────┐
│              DATA COLLECTION LAYER                              │
│  ┌──────────────────┐  ┌──────────────────┐                   │
│  │ Alpha Vantage    │  │ News &           │                   │
│  │ (Market Data)    │  │ Sentiment        │                   │
│  └────────┬─────────┘  └────────┬─────────┘                   │
│           │                      │                              │
│           ▼                      ▼                              │
│  ┌──────────────────┐  ┌──────────────────┐                   │
│  │ Cache Manager    │  │ Data Validator   │                   │
│  └──────────────────┘  └──────────────────┘                   │
└───────────┬──────────────────────┬─────────────────────────────┘
            │                      │
            ▼                      ▼
┌─────────────────────────────────────────────────────────────────┐
│              COMPLIANCE & GUARDRAILS                            │
│  ┌──────────────────┐  ┌──────────────────┐                   │
│  │ Compliance       │  │ Fact Checker     │                   │
│  │ Checker          │  │                  │                   │
│  └────────┬─────────┘  └────────┬─────────┘                   │
│           │                      │                              │
│           ▼                      ▼                              │
│  ┌──────────────────┐  ┌──────────────────┐                   │
│  │ Safety Filters   │  │ Explainability    │                   │
│  └──────────────────┘  └──────────────────┘                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Data Flow Architecture

```
User Query
    │
    ▼
┌─────────────────────────────────────┐
│  Query Understanding                │
│  - Intent classification            │
│  - Entity extraction                │
│  - Context retrieval               │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  RAG Pipeline                       │
│  - Retrieve relevant context        │
│  - User profile context             │
│  - Market data context              │
│  - Historical recommendations        │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Personalization Engine              │
│  - User profile lookup              │
│  - Risk assessment                  │
│  - Goal alignment                   │
│  - Recommendation generation        │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  LLM Inference                      │
│  - Prompt construction              │
│  - Model generation                 │
│  - Response formatting              │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Compliance Check                   │
│  - Fact verification                │
│  - Disclaimer injection             │
│  - Safety filtering                 │
└──────────────┬──────────────────────┘
               │
               ▼
Final Response → User Interface
```

---

## 3. Component Interaction Flow

```
┌─────────────┐
│   User      │
│  (Browser)  │
└──────┬──────┘
       │ HTTP Request
       ▼
┌─────────────────────────────────────┐
│     Streamlit App                   │
│  ┌───────────────────────────────┐  │
│  │ Chat Interface Component      │  │
│  └──────────────┬────────────────┘  │
│                 │                     │
│  ┌──────────────▼────────────────┐  │
│  │ Profile Form Component        │  │
│  └──────────────┬────────────────┘  │
│                 │                     │
│  ┌──────────────▼────────────────┐  │
│  │ Visualizations Component      │  │
│  └──────────────┬────────────────┘  │
└─────────────────┼────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│     RAG Pipeline                    │
│  ┌───────────────────────────────┐  │
│  │ retrieve_context()            │  │
│  │ - User profile                │  │
│  │ - Market data                 │  │
│  │ - Historical context           │  │
│  └──────────────┬────────────────┘  │
│                 │                     │
│  ┌──────────────▼────────────────┐  │
│  │ generate_response()           │  │
│  │ - Construct prompt            │  │
│  │ - Call LLM                   │  │
│  │ - Format response            │  │
│  └──────────────┬────────────────┘  │
└─────────────────┼────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│     Inference Engine                │
│  ┌───────────────────────────────┐  │
│  │ FinancialAdvisorInference     │  │
│  │ - Load fine-tuned model       │  │
│  │ - Generate response           │  │
│  └──────────────┬────────────────┘  │
└─────────────────┼────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│     Personalization Engine           │
│  ┌───────────────────────────────┐  │
│  │ PersonalizationEngine         │  │
│  │ - Generate recommendations    │  │
│  │ - Risk assessment            │  │
│  └──────────────┬────────────────┘  │
└─────────────────┼────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│     Compliance Checker               │
│  ┌───────────────────────────────┐  │
│  │ ComplianceChecker            │  │
│  │ - Add disclaimers            │  │
│  │ - Fact check                 │  │
│  └──────────────┬────────────────┘  │
└─────────────────┼────────────────────┘
                  │
                  ▼
Response → User Interface
```

---

## 4. Model Training Pipeline

```
┌─────────────────────────────────────┐
│  Data Sources                       │
│  ┌───────────────────────────────┐  │
│  │ FinGPT/fingpt-sentiment-train │  │
│  │ FinGPT/fingpt-fiqa_qa         │  │
│  └──────────────┬─────────────────┘  │
└────────────────┼────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│  Data Preparation                   │
│  ┌───────────────────────────────┐  │
│  │ Load datasets (10K samples)   │  │
│  │ Combine sentiment + QA        │  │
│  │ Format prompts                │  │
│  └──────────────┬────────────────┘  │
└────────────────┼────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│  Tokenization                       │
│  ┌───────────────────────────────┐  │
│  │ Tokenize inputs/outputs       │  │
│  │ Create train/eval split       │  │
│  │ (80/20)                       │  │
│  └──────────────┬────────────────┘  │
└────────────────┼────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│  Model Setup                         │
│  ┌───────────────────────────────┐  │
│  │ Load Mistral-7B-Instruct      │  │
│  │ Configure LoRA                │  │
│  │ (r=16, alpha=32)              │  │
│  └──────────────┬────────────────┘  │
└────────────────┼────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│  Training                            │
│  ┌───────────────────────────────┐  │
│  │ Train for 1000 steps         │  │
│  │ Evaluate every 200 steps     │  │
│  │ Save best checkpoint         │  │
│  └──────────────┬────────────────┘  │
└────────────────┼────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│  Model Evaluation                    │
│  ┌───────────────────────────────┐  │
│  │ BLEU Score                    │  │
│  │ ROUGE Scores                   │  │
│  │ Qualitative analysis          │  │
│  └──────────────┬────────────────┘  │
└────────────────┼────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│  Fine-tuned Model                    │
│  (models/fine_tuned/financial_advisor)│
└─────────────────────────────────────┘
```

---

## 5. RAG Pipeline Architecture

```
User Query: "Should I invest in tech stocks?"
    │
    ▼
┌─────────────────────────────────────┐
│  Query Understanding                 │
│  - Intent: investment_advice        │
│  - Entities: ["tech stocks"]        │
│  - Context: user profile             │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Context Retrieval                   │
│  ┌───────────────────────────────┐  │
│  │ 1. User Profile               │  │
│  │    - Risk tolerance           │  │
│  │    - Current portfolio        │  │
│  │    - Financial goals          │  │
│  │                                │  │
│  │ 2. Market Data                │  │
│  │    - Tech sector performance  │  │
│  │    - Recent news/sentiment    │  │
│  │    - Technical indicators     │  │
│  │                                │  │
│  │ 3. Knowledge Base             │  │
│  │    - Financial best practices │  │
│  │    - Diversification rules    │  │
│  └──────────────┬────────────────┘  │
└─────────────────┼────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│  Prompt Construction                 │
│  ┌───────────────────────────────┐  │
│  │ <|system|>                    │  │
│  │ You are an expert Financial   │  │
│  │ Advisor...                    │  │
│  │                                │  │
│  │ <|user|>                      │  │
│  │ User Profile: [risk: moderate]│  │
│  │ Market Context: [tech +5%]    │  │
│  │ Question: Should I invest...  │  │
│  └──────────────┬────────────────┘  │
└─────────────────┼────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│  LLM Generation                      │
│  ┌───────────────────────────────┐  │
│  │ Generate response with        │  │
│  │ context and personalization   │  │
│  └──────────────┬────────────────┘  │
└─────────────────┼────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│  Compliance Check                    │
│  ┌───────────────────────────────┐  │
│  │ - Add disclaimers             │  │
│  │ - Fact check claims           │  │
│  │ - Safety filter               │  │
│  └──────────────┬────────────────┘  │
└─────────────────┼────────────────────┘
                  │
                  ▼
Final Response with Sources & Disclaimers
```

---

## 6. Personalization Engine Flow

```
User Profile Input
    │
    ▼
┌─────────────────────────────────────┐
│  User Profiler                       │
│  - Age, income, goals               │
│  - Current portfolio                 │
│  - Investment experience             │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Risk Assessor                       │
│  - Calculate risk score             │
│  - Categorize (conservative/        │
│    moderate/aggressive)              │
│  - Consider time horizon            │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Embedding Generator                 │
│  - Generate profile embedding       │
│  - Match to investment instruments  │
│  - Calculate similarity scores      │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Recommendation Engine               │
│  - Asset allocation                 │
│  - Instrument selection             │
│  - Diversification analysis         │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Goal Planner                        │
│  - Align with financial goals       │
│  - Calculate required contributions │
│  - Project timeline                 │
└──────────────┬──────────────────────┘
               │
               ▼
Personalized Recommendations + Visualizations
```

---

## 7. API Architecture

```
┌─────────────────────────────────────┐
│  FastAPI Application                │
│  ┌───────────────────────────────┐  │
│  │ Middleware                    │  │
│  │ - CORS                        │  │
│  │ - Rate limiting              │  │
│  │ - Authentication             │  │
│  └──────────────┬────────────────┘  │
└─────────────────┼────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│  API Endpoints                       │
│  ┌───────────────────────────────┐  │
│  │ GET  /health                  │  │
│  │ POST /chat                    │  │
│  │ GET  /recommendations/{id}    │  │
│  │ GET  /profile/{id}            │  │
│  └──────────────┬────────────────┘  │
└─────────────────┼────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│  Business Logic                      │
│  ┌───────────────────────────────┐  │
│  │ FinancialAdvisorInference     │  │
│  │ PersonalizationEngine        │  │
│  │ ComplianceChecker            │  │
│  └──────────────┬────────────────┘  │
└─────────────────┼────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│  Response Formatting                 │
│  ┌───────────────────────────────┐  │
│  │ JSON response                │  │
│  │ Error handling               │  │
│  │ Logging                      │  │
│  └──────────────┬────────────────┘  │
└─────────────────┼────────────────────┘
                  │
                  ▼
HTTP Response → Client
```

---

## 8. Database Schema Relationships

```
┌──────────────┐
│    users     │
│──────────────│
│ user_id (PK) │
│ email        │
│ created_at   │
└──────┬───────┘
       │
       │ 1:N
       ▼
┌──────────────────────┐
│   user_profiles      │
│──────────────────────│
│ profile_id (PK)      │
│ user_id (FK)         │
│ age, income          │
│ risk_tolerance_score │
└──────┬───────────────┘
       │
       │ 1:N
       ▼
┌──────────────────────┐
│  financial_goals     │
│──────────────────────│
│ goal_id (PK)         │
│ user_id (FK)         │
│ goal_type            │
│ target_amount        │
│ time_horizon         │
└──────┬───────────────┘
       │
       │ 1:N
       ▼
┌──────────────────────┐
│ recommendations      │
│──────────────────────│
│ rec_id (PK)          │
│ user_id (FK)         │
│ recommendation_data  │
│ confidence_score     │
└──────────────────────┘

┌──────────────────────┐
│  interactions        │
│──────────────────────│
│ interaction_id (PK)  │
│ user_id (FK)         │
│ query_text           │
│ response_text        │
│ feedback_score       │
└──────────────────────┘

┌──────────────────────┐
│ market_data_cache    │
│──────────────────────│
│ cache_id (PK)        │
│ symbol               │
│ data_type            │
│ data (JSONB)         │
│ expires_at           │
└──────────────────────┘
```

---

## 9. Deployment Architecture

```
┌─────────────────────────────────────┐
│  Production Environment              │
│  ┌───────────────────────────────┐  │
│  │ Load Balancer                 │  │
│  └──────────────┬────────────────┘  │
│                 │                     │
│  ┌──────────────▼────────────────┐  │
│  │ Application Servers            │  │
│  │ ┌──────────┐  ┌──────────┐   │  │
│  │ │Streamlit │  │ FastAPI  │   │  │
│  │ │  App     │  │   API    │   │  │
│  │ └──────────┘  └──────────┘   │  │
│  └──────────────┬────────────────┘  │
│                 │                     │
│  ┌──────────────▼────────────────┐  │
│  │ Database                      │  │
│  │ ┌──────────┐  ┌──────────┐   │  │
│  │ │PostgreSQL│  │  Redis   │   │  │
│  │ │          │  │  Cache   │   │  │
│  │ └──────────┘  └──────────┘   │  │
│  └──────────────┬────────────────┘  │
│                 │                     │
│  ┌──────────────▼────────────────┐  │
│  │ External Services              │  │
│  │ ┌──────────┐  ┌──────────┐   │  │
│  │ │Alpha     │  │ Hugging  │   │  │
│  │ │Vantage   │  │  Face    │   │  │
│  │ └──────────┘  └──────────┘   │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
```

---

## 10. Technology Stack Diagram

```
┌─────────────────────────────────────┐
│  Frontend Layer                      │
│  ┌───────────────────────────────┐  │
│  │ Streamlit                     │  │
│  │ Plotly (Visualizations)       │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────┐
│  API Layer                          │
│  ┌───────────────────────────────┐  │
│  │ FastAPI                      │  │
│  │ Pydantic (Validation)        │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────┐
│  ML/AI Layer                        │
│  ┌───────────────────────────────┐  │
│  │ Hugging Face Transformers     │  │
│  │ PyTorch                       │  │
│  │ PEFT (LoRA)                   │  │
│  │ Sentence Transformers         │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────┐
│  Data Layer                          │
│  ┌───────────────────────────────┐  │
│  │ PostgreSQL                    │  │
│  │ Alpha Vantage API              │  │
│  │ FinGPT Datasets               │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
```

---

**Document Version:** 1.0  
**Last Updated:** January 2025




