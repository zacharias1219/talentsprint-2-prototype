"""
Model Evaluation Script.

Evaluates the fine-tuned financial advisor model using BLEU and ROUGE metrics.
"""

import os
import sys
import torch
import json
from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from rouge_score import rouge_scorer

# Add scripts directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def load_model_and_tokenizer(model_path="./models/fine_tuned/financial_advisor", base_model="mistralai/Mistral-7B-Instruct-v0.2"):
    """Load fine-tuned model and tokenizer."""
    print(f"Loading model from {model_path}...")
    
    tokenizer = AutoTokenizer.from_pretrained(base_model)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    # Load with FP16 if available (better for TinyLlama)
    dtype = torch.float16 if torch.cuda.is_available() else torch.float32
    device_map = "auto" if torch.cuda.is_available() else None
    
    base_model_obj = AutoModelForCausalLM.from_pretrained(
        base_model,
        torch_dtype=dtype,
        device_map=device_map,
        trust_remote_code=True
    )
    
    if os.path.exists(model_path):
        model = PeftModel.from_pretrained(base_model_obj, model_path)
        print("✓ Fine-tuned adapter loaded")
    else:
        print("⚠ Using base model (adapter not found)")
        model = base_model_obj
    
    # Ensure model is in eval mode
    model.eval()
    return model, tokenizer


def generate_response(model, tokenizer, prompt, max_length=300, temperature=0.3):
    """Generate response from model."""
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=1024)
    
    # Move inputs to model device
    device = model.device
    inputs = {k: v.to(device) for k, v in inputs.items()}
    
    # Define stop tokens
    stop_token_ids = [
        tokenizer.eos_token_id,
        tokenizer.convert_tokens_to_ids("<|user|>"),
        tokenizer.convert_tokens_to_ids("###")
    ]
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_length,
            temperature=temperature,
            do_sample=True,
            top_p=0.9,
            repetition_penalty=1.2,
            pad_token_id=tokenizer.eos_token_id,
            eos_token_id=stop_token_ids,  # Pass list of stop tokens here
        )
    
    full_response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # Extract response part
    if "### Response:" in full_response:
        response = full_response.split("### Response:")[-1]
    elif "<|user|>" in full_response:
        response = full_response.split("<|user|>")[-1]
    else:
        response = full_response[len(prompt):]
    
    # Clean up any trailing artifacts
    response = response.split("###")[0].strip()
    response = response.split("<|user|>")[0].strip()
    
    return response


def calculate_bleu(reference, candidate):
    """Calculate BLEU score."""
    try:
        # Tokenize
        ref_tokens = reference.lower().split()
        cand_tokens = candidate.lower().split()
        
        # Use smoothing function for better scores
        smoothing = SmoothingFunction().method1
        score = sentence_bleu([ref_tokens], cand_tokens, smoothing_function=smoothing)
        return score
    except:
        return 0.0


def calculate_rouge(reference, candidate):
    """Calculate ROUGE scores."""
    try:
        scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
        scores = scorer.score(reference, candidate)
        return {
            'rouge1': scores['rouge1'].fmeasure,
            'rouge2': scores['rouge2'].fmeasure,
            'rougeL': scores['rougeL'].fmeasure
        }
    except Exception as e:
        print(f"Error calculating ROUGE: {e}")
        return {'rouge1': 0.0, 'rouge2': 0.0, 'rougeL': 0.0}


def evaluate_model(model_path="./models/fine_tuned/financial_advisor", base_model="mistralai/Mistral-7B-Instruct-v0.2", num_samples=100):
    """Evaluate model on test dataset."""
    print("=== Model Evaluation ===")
    
    # Load model
    model, tokenizer = load_model_and_tokenizer(model_path, base_model)
    
    # Load test dataset
    print("\n--- Loading Test Dataset ---")
    try:
        test_ds = load_dataset("FinGPT/fingpt-fiqa_qa", split=f"train[{num_samples}:{num_samples+100}]")
        print(f"Loaded {len(test_ds)} test samples")
    except Exception as e:
        print(f"Error loading dataset: {e}")
        return
    
    # Evaluation metrics
    bleu_scores = []
    rouge_scores = {'rouge1': [], 'rouge2': [], 'rougeL': []}
    
    # Store examples for qualitative analysis
    examples_log = []
    
    print("\n--- Evaluating Model ---")
    for i, example in enumerate(test_ds):
        if i >= num_samples:
            break
        
        instruction = example.get("instruction", "")
        input_text = example.get("input", "")
        reference = example.get("output", "")
        
        # Create prompt
        prompt = f"""<|system|>
You are an expert Financial Advisor AI. Provide accurate, compliant financial advice.
<|user|>
### Instruction:
{instruction}

### Input:
{input_text}

### Response:
"""
        
        # Generate response
        candidate = generate_response(model, tokenizer, prompt)
        
        # Calculate metrics
        bleu = calculate_bleu(reference, candidate)
        rouge = calculate_rouge(reference, candidate)
        
        bleu_scores.append(bleu)
        for key in rouge_scores:
            rouge_scores[key].append(rouge[key])
        
        # Log first 5 examples and then every 10th example
        if i < 5 or (i + 1) % 10 == 0:
            examples_log.append({
                "instruction": instruction,
                "input": input_text,
                "reference": reference,
                "candidate": candidate,
                "bleu": bleu,
                "rouge1": rouge['rouge1']
            })
            print(f"Processed {i + 1}/{num_samples} samples...")
            
    # Save detailed log
    log_path = "models/evaluation_log.json"
    with open(log_path, 'w') as f:
        json.dump(examples_log, f, indent=2)
    print(f"\nDetailed comparison log saved to {log_path}")
    
    # Calculate averages
    avg_bleu = sum(bleu_scores) / len(bleu_scores) if bleu_scores else 0.0
    avg_rouge = {
        key: sum(scores) / len(scores) if scores else 0.0
        for key, scores in rouge_scores.items()
    }
    
    # Print results
    print("\n=== Evaluation Results ===")
    print(f"BLEU Score: {avg_bleu:.4f}")
    print(f"ROUGE-1: {avg_rouge['rouge1']:.4f}")
    print(f"ROUGE-2: {avg_rouge['rouge2']:.4f}")
    print(f"ROUGE-L: {avg_rouge['rougeL']:.4f}")
    
    # Save results
    results = {
        "model_path": model_path,
        "base_model": base_model,
        "num_samples": num_samples,
        "metrics": {
            "bleu": avg_bleu,
            "rouge1": avg_rouge['rouge1'],
            "rouge2": avg_rouge['rouge2'],
            "rougeL": avg_rouge['rougeL']
        }
    }
    
    results_path = "models/evaluation_results.json"
    os.makedirs(os.path.dirname(results_path), exist_ok=True)
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to {results_path}")
    
    return results


def compare_models(base_model_path=None, fine_tuned_path="./models/fine_tuned/financial_advisor"):
    """Compare base model vs fine-tuned model."""
    print("=== Model Comparison ===")
    
    # Must match the base model used for training (TinyLlama)
    base_model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
    
    print("\n1. Evaluating Base Model...")
    base_results = evaluate_model(model_path=None, base_model=base_model_name, num_samples=50)
    
    print("\n2. Evaluating Fine-Tuned Model...")
    ft_results = evaluate_model(model_path=fine_tuned_path, base_model=base_model_name, num_samples=50)
    
    print("\n=== Comparison Summary ===")
    if base_results and ft_results:
        print(f"BLEU Improvement: {ft_results['metrics']['bleu'] - base_results['metrics']['bleu']:.4f}")
        print(f"ROUGE-L Improvement: {ft_results['metrics']['rougeL'] - base_results['metrics']['rougeL']:.4f}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Evaluate fine-tuned financial advisor model")
    parser.add_argument("--model_path", type=str, default="./models/fine_tuned/financial_advisor",
                       help="Path to fine-tuned model")
    parser.add_argument("--base_model", type=str, default="mistralai/Mistral-7B-Instruct-v0.2",
                       help="Base model name")
    parser.add_argument("--num_samples", type=int, default=100,
                       help="Number of test samples")
    parser.add_argument("--compare", action="store_true",
                       help="Compare base vs fine-tuned model")
    
    args = parser.parse_args()
    
    if args.compare:
        compare_models(fine_tuned_path=args.model_path)
    else:
        evaluate_model(args.model_path, args.base_model, args.num_samples)

