"""
Financial LLM Fine-tuning Script.

This script implements the fine-tuning pipeline for the Financial Advisor LLM using the FinGPT framework approach.
It is a standalone version of the logic in notebooks/fine_tuning_pipeline.ipynb.
"""

import os
import torch
from datasets import load_dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
    DataCollatorForSeq2Seq
)
from peft import LoraConfig, get_peft_model, TaskType

# Disable external logging to avoid configuration errors on local environment
os.environ["WANDB_DISABLED"] = "true"
os.environ["CLEARML_LOGGED_IN"] = "false"
os.environ["MLFLOW_TRACKING_URI"] = "" 

def main():
    print("=== Financial Advisor Model Training ===")
    
    # Configuration
    # Using TinyLlama for efficient training (matches the current fine-tuned adapter)
    # To upgrade to Mistral-7B, retrain with MODEL_NAME = "mistralai/Mistral-7B-Instruct-v0.2"
    MODEL_NAME = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
    OUTPUT_DIR = "./models/fine_tuned/financial_advisor"
    MAX_LENGTH = 512
    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {DEVICE}")
    
    # Check if model download is needed
    print(f"\n⚠️  Note: LLaMA-2 requires Hugging Face authentication.")
    print(f"   If this is your first time, you may need to:")
    print(f"   1. Request access at https://huggingface.co/meta-llama/Llama-2-7b-hf")
    print(f"   2. Run: huggingface-cli login")
    print(f"   3. Accept the model license\n")

    # 1. Load Datasets
    print("\n--- Loading Datasets ---")
    # Expanded dataset size for better training
    try:
        sentiment_ds = load_dataset("FinGPT/fingpt-sentiment-train", split="train[:5000]")
        qa_ds = load_dataset("FinGPT/fingpt-fiqa_qa", split="train[:5000]")
        print(f"Loaded {len(sentiment_ds)} sentiment samples")
        print(f"Loaded {len(qa_ds)} QA samples")
        
        # Combine datasets for training
        from datasets import concatenate_datasets
        combined_ds = concatenate_datasets([sentiment_ds, qa_ds])
        print(f"Combined dataset size: {len(combined_ds)} samples")
    except Exception as e:
        print(f"Error loading datasets: {e}")
        return

    # 2. Tokenization
    print("\n--- Tokenizing Data ---")
    try:
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        # LLaMA-2 uses a different pad token setup
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
            tokenizer.pad_token_id = tokenizer.eos_token_id
    except Exception as e:
        print(f"Error loading tokenizer: {e}")
        print("This may require Hugging Face authentication. Run: huggingface-cli login")
        return

    def preprocess_function(examples):
        # Enhanced prompt template for financial domain
        # Emphasizes accuracy, compliance, and structured responses
        inputs = [
            f"""<|system|>
You are an expert Financial Advisor AI. Provide accurate, compliant financial advice based on the user's question and context.
Always include appropriate disclaimers and cite specific data when available.
<|user|>
### Instruction:
{inst}

### Input:
{inp}

### Response:
"""
            for inst, inp in zip(examples["instruction"], examples["input"])
        ]
        targets = examples["output"]
        
        # Tokenize inputs
        model_inputs = tokenizer(inputs, max_length=MAX_LENGTH, truncation=True, padding="max_length")
        labels = tokenizer(targets, max_length=MAX_LENGTH, truncation=True, padding="max_length")
        
        model_inputs["labels"] = labels["input_ids"]
        return model_inputs

    # Tokenize combined dataset
    tokenized_ds = combined_ds.map(preprocess_function, batched=True)

    # Split into train/eval (80/20)
    split_dataset = tokenized_ds.train_test_split(test_size=0.2, seed=42)
    train_dataset = split_dataset["train"]
    eval_dataset = split_dataset["test"]

    print(f"Train samples: {len(train_dataset)}")
    print(f"Eval samples: {len(eval_dataset)}")

    # 3. Model Setup (LoRA)
    print("\n--- Setting up Model (LoRA) ---")
    try:
        # Load model with appropriate settings for LLaMA-2
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME,
            torch_dtype=torch.float16 if DEVICE == "cuda" else torch.float32,
            device_map="auto" if DEVICE == "cuda" else None,
            trust_remote_code=True
        )
    except Exception as e:
        print(f"Error loading model: {e}")
        print("This may require:")
        print("1. Hugging Face authentication: huggingface-cli login")
        print("2. Model access approval at https://huggingface.co/meta-llama/Llama-2-7b-hf")
        return
    
    peft_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM, 
        inference_mode=False, 
        r=8, 
        lora_alpha=32, 
        lora_dropout=0.1
    )
    
    model = get_peft_model(model, peft_config)
    model.print_trainable_parameters()

    # 4. Training Loop
    print("\n--- Starting Training ---")
    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        report_to="none", # Disable all external logging
        per_device_train_batch_size=2 if DEVICE == "cuda" else 1,  # Smaller batch for LLaMA-2
        gradient_accumulation_steps=8 if DEVICE == "cuda" else 4,
        learning_rate=2e-4,
        logging_steps=50,
        eval_steps=200,
        evaluation_strategy="steps",
        max_steps=1000,  # Increased for better training
        save_strategy="steps",
        save_steps=200,
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        greater_is_better=False,
        fp16=DEVICE == "cuda",  # Enable FP16 for CUDA
        bf16=False,
        warmup_steps=100,
        lr_scheduler_type="cosine",
        use_cpu=DEVICE != "cuda"
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        data_collator=DataCollatorForSeq2Seq(tokenizer, padding=True)
    )

    trainer.train()
    
    # Explicitly save the final adapter
    trainer.save_model(OUTPUT_DIR)
    print("\n=== Training Completed Successfully ===")
    print(f"Model checkpoints saved to {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
