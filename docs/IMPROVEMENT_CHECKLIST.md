# Quick Improvement Checklist

## Immediate Actions (This Week)

- [x] **Model Selection:** ✅ Analyzed documentation - **Mistral-7B + FinGPT datasets is optimal** (see `docs/MODEL_SELECTION_ANALYSIS.md`)
- [x] **Upgrade Model:** ✅ Changed `MODEL_NAME` in `notebooks/model_training_phase2.ipynb` to `"mistralai/Mistral-7B-Instruct-v0.2"`
- [x] **Update Scripts:** ✅ Updated `scripts/inference.py` and `scripts/evaluate_model.py` to use Mistral-7B
- [x] **Documentation Alignment:** ✅ Updated notebook to clarify FinGPT datasets usage (as per project docs)
- [ ] **Retrain:** ⏳ **ACTION REQUIRED:** Run `notebooks/model_training_phase2.ipynb` (expect 2-3 hours on GPU, 8-12 hours on CPU)
- [ ] **Re-evaluate:** Run `python scripts/evaluate_model.py --num_samples 100` after retraining
- [ ] **Compare:** Check if BLEU improved to >0.15

**📖 See `docs/RETRAINING_GUIDE.md` for detailed instructions**
**📖 See `docs/MODEL_SELECTION_ANALYSIS.md` for model selection rationale**

## Short-Term (Next 2 Weeks)

- [ ] **Add Few-Shot Examples:** Update prompt in `scripts/inference.py` with examples
- [ ] **Implement Caching:** Add Redis/file cache for common queries
- [ ] **Expand Training Data:** Download full FinGPT datasets (50K+ samples)

## Medium-Term (Next Month)

- [ ] **Deploy Vector Store:** Set up Pinecone account, ingest financial documents
- [ ] **Add Portfolio Simulator:** Create `scripts/portfolio_simulator.py`
- [ ] **User Feedback:** Add thumbs up/down buttons in Streamlit UI

## Long-Term (Next Quarter)

- [ ] **Beta Testing:** Deploy to 100 real users
- [ ] **Analytics Dashboard:** Track user engagement metrics
- [ ] **SaaS Preparation:** Set up billing, API keys, rate limiting

