# Retraining Guide: Mistral-7B Upgrade

## ✅ Code Updated Successfully!

All scripts have been updated to use **Mistral-7B-Instruct-v0.2**. Now you need to retrain the model.

---

## Step 1: Check GPU Availability

```bash
# Check if CUDA is available
python -c "import torch; print(f'CUDA Available: {torch.cuda.is_available()}'); print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"CPU\"}')"
```

**Requirements:**
- **GPU:** ~14GB VRAM (RTX 3090, A100, etc.)
- **CPU:** Will work but takes 8-12 hours

---

## Step 2: Open Training Notebook

1. Open `notebooks/model_training_phase2.ipynb` in Jupyter/VS Code
2. The model is already set to `mistralai/Mistral-7B-Instruct-v0.2`
3. Run all cells sequentially

---

## Step 3: Monitor Training

The notebook will:
1. Download Mistral-7B (~14GB) - takes 5-10 minutes
2. Load and tokenize 10,000 samples - takes 2-3 minutes
3. **Train for 1000 steps** - takes **2-3 hours on GPU** or **8-12 hours on CPU**

**Expected Output:**
```
Train: 8000 | Eval: 2000
--- Setting up Model ---
✓ Model loaded successfully!
--- Starting Training ---
{'loss': 2.5, 'learning_rate': 0.0002, 'epoch': 0.1}
{'loss': 1.8, 'learning_rate': 0.00015, 'epoch': 0.2}
...
```

---

## Step 4: Verify Model Saved

After training completes, check:
```bash
ls -lh models/fine_tuned/financial_advisor_mistral/
```

You should see:
- `adapter_config.json`
- `adapter_model.bin` (or `.safetensors`)
- `training_args.bin`

---

## Step 5: Update Model Path (If Different)

If the output directory is different, update:

**In `scripts/inference.py`:**
```python
advisor = FinancialAdvisorInference(
    model_path="./models/fine_tuned/financial_advisor_mistral",  # Update this
    base_model="mistralai/Mistral-7B-Instruct-v0.2"
)
```

**In `scripts/evaluate_model.py`:**
```python
python scripts/evaluate_model.py \
    --model_path ./models/fine_tuned/financial_advisor_mistral \
    --base_model mistralai/Mistral-7B-Instruct-v0.2 \
    --num_samples 100
```

---

## Step 6: Re-Evaluate

```bash
python scripts/evaluate_model.py --num_samples 100
```

**Expected Improvement:**
- **BLEU:** 0.0068 → **0.15-0.25** (20-30x improvement)
- **ROUGE-1:** 0.25 → **0.45-0.55** (2x improvement)
- **ROUGE-L:** 0.13 → **0.30-0.40** (2-3x improvement)

---

## Troubleshooting

### Out of Memory Error
**Solution:** Reduce batch size in notebook:
```python
per_device_train_batch_size=1  # Instead of 4
gradient_accumulation_steps=16  # Instead of 4
```

### Model Download Fails
**Solution:** Use Hugging Face CLI:
```bash
huggingface-cli download mistralai/Mistral-7B-Instruct-v0.2
```

### Training Too Slow
**Solution:** Reduce steps for testing:
```python
max_steps=100  # Instead of 1000 (quick test)
```

---

## Quick Test (Without Full Retraining)

To test Mistral-7B **without fine-tuning** (baseline):

```python
# In Python
from scripts.inference import FinancialAdvisorInference

# Use base model only (no fine-tuning)
advisor = FinancialAdvisorInference(
    model_path="./nonexistent_path",  # Forces base model
    base_model="mistralai/Mistral-7B-Instruct-v0.2"
)

response = advisor.generate_response("user_1000", "What is an ETF?")
print(response)
```

This will show you Mistral-7B's **baseline** performance (should already be better than TinyLlama).

---

## Next Steps After Retraining

1. ✅ Run evaluation: `python scripts/evaluate_model.py --num_samples 100`
2. ✅ Compare results: Check `models/evaluation_results.json`
3. ✅ Test in UI: `streamlit run ui/streamlit_app.py`
4. ✅ Update documentation with new metrics

---

**Estimated Total Time:** 2-3 hours (GPU) or 8-12 hours (CPU)

**Ready to start?** Open `notebooks/model_training_phase2.ipynb` and run all cells!


