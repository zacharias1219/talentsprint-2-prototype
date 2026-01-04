<!-- 02c06b36-da64-4017-80de-1a1125c837d3 4f74bb3e-de51-42f8-9f54-ce903e2b17c7 -->
# Financial Advisor Enhancement Pipeline

## Phase 1: Build Full Dashboard UI (Option 2)

### 1.1 Integrate Inference Script with Streamlit

- **File**: `ui/streamlit_app.py`
- Modify to use `scripts/inference.py` instead of `src.api.routes`
- Add model loading on startup (cache in session state)
- Connect `FinancialAdvisorInference` class to chat interface

### 1.2 Enhance Chat Interface

- **File**: `ui/components/chat_interface.py`
- Add typing indicators during generation
- Show context snippets (user profile, market data) in expandable sections
- Display confidence scores or model metadata

### 1.3 Add User Profile Display

- **File**: `ui/components/profile_form.py` (enhance existing)
- Load and display user recommendations from `data/processed/user_recommendations.json`
- Show risk profile score, target allocation, action plan
- Add form to create/edit user profiles

### 1.4 Portfolio Visualizations

- **File**: `ui/components/visualizations.py` (enhance existing)
- Create allocation pie chart (Stocks/Bonds/Cash) using Plotly
- Add risk-return scatter plot
- Display sector recommendations as bar chart
- Show portfolio gap analysis (current vs target)

### 1.5 Market Data Dashboard

- Add new component: `ui/components/market_dashboard.py`
- Display live market data from Alpha Vantage (using `scripts/data_acquisition.py`)
- Show stock price trends, RSI indicators
- Display news sentiment scores

### 1.6 Main App Integration

- **File**: `ui/streamlit_app.py`
- Add tabs: "Chat", "Portfolio", "Market Data", "Profile"
- Integrate all components
- Add sidebar with user selection dropdown

## Phase 2: Improve Model Quality (Option 1)

### 2.1 Upgrade Base Model

- **File**: `scripts/train_model.py`
- Change `MODEL_NAME` from `"gpt2"` to `"meta-llama/Llama-2-7b-hf"`
- Add model download verification
- Handle Hugging Face authentication if needed

### 2.2 Expand Training Data

- **File**: `scripts/train_model.py`
- Increase dataset size: `train[:500]` → `train[:5000]` or full dataset
- Combine both sentiment and QA datasets for training
- Add data validation and quality checks

### 2.3 Enhanced Training Configuration

- **File**: `scripts/train_model.py`
- Increase `max_steps` from 50 to 1000+
- Add evaluation dataset split (80/20 train/eval)
- Implement early stopping based on eval loss
- Add learning rate scheduling

### 2.4 Better Prompt Engineering

- **File**: `scripts/train_model.py` and `scripts/inference.py`
- Refine prompt template for financial domain
- Add system instructions emphasizing accuracy and compliance
- Include examples of good financial advice format

### 2.5 Model Evaluation

- Create `scripts/evaluate_model.py`
- Add BLEU/ROUGE score calculation
- Test on held-out financial QA examples
- Compare fine-tuned vs base model performance

## Phase 3: Production Deployment (Option 3)

### 3.1 Evaluation Metrics

- **File**: `scripts/evaluate_model.py` (create)
- Implement BLEU score for response quality
- Add ROUGE-L for answer completeness
- Create evaluation report generator
- Add automated testing suite

### 3.2 Compliance Layer

- **File**: `src/compliance/compliance_checker.py` (enhance existing)
- Add fact-checking against Alpha Vantage data
- Implement disclaimer injection ("This is not financial advice")
- Add risk warnings for high-risk recommendations
- Log all advice for audit trail

### 3.3 API Endpoints

- **File**: `src/api/routes.py` (enhance existing)
- Create REST API wrapper around inference script
- Add endpoints: `/chat`, `/recommendations`, `/profile`
- Add rate limiting and authentication
- Return structured JSON responses

### 3.4 Error Handling & Logging

- **File**: `src/utils/logger.py` (enhance existing)
- Add structured logging for all API calls
- Log model inference times and errors
- Add monitoring for API key usage (Alpha Vantage rate limits)

### 3.5 Documentation

- **File**: `docs/API_DOCUMENTATION.md` (create)
- Document all API endpoints
- Add usage examples
- Include deployment instructions

## Implementation Order

1. **Phase 1** (UI): Start with `ui/streamlit_app.py` integration, then add components
2. **Phase 2** (Model): Upgrade model, retrain, evaluate
3. **Phase 3** (Production): Add metrics, compliance, API endpoints

## Dependencies

- Phase 1: Requires `scripts/inference.py` (already exists)
- Phase 2: Requires GPU with ~14GB VRAM for LLaMA-2 7B
- Phase 3: Requires Phase 1 & 2 completion

## Success Criteria

- Phase 1: Interactive dashboard with all visualizations working
- Phase 2: Model achieves >70% BLEU score on test set
- Phase 3: API endpoints return structured responses with compliance disclaimers

### To-dos

- [ ] Generate analytical report
- [ ] Integrate inference script with Streamlit app (ui/streamlit_app.py)
- [ ] Enhance chat interface with context display and typing indicators
- [ ] Add user profile display component showing recommendations
- [ ] Create portfolio allocation and risk-return visualizations
- [ ] Add market data dashboard component
- [ ] Upgrade base model from GPT-2 to LLaMA-2 7B in train_model.py
- [ ] Expand training dataset from 500 to 5000+ samples
- [ ] Retrain model with 1000+ steps and evaluation split
- [ ] Create evaluation script with BLEU/ROUGE metrics
- [ ] Implement evaluation metrics and automated testing
- [ ] Enhance compliance checker with fact-checking and disclaimers
- [ ] Create REST API endpoints wrapping inference functionality