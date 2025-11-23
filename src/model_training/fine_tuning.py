"""
Fine-tuning module for FinGPT model.

Implements LoRA fine-tuning for financial domain adaptation.
"""

from pathlib import Path
from typing import Any, Dict, Optional

import torch
from peft import LoraConfig, get_peft_model, TaskType
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling,
)

from src.model_training.data_preparation import DataPreparation
from src.utils.config import get_config
from src.utils.logger import get_logger

logger = get_logger(__name__)


class FineTuner:
    """Fine-tuner for FinGPT model."""

    def __init__(self):
        """Initialize fine-tuner."""
        config = get_config()
        model_config = config.get_model_config("training", {})

        self.base_model = model_config.get("base_model", "FinGPT/fingpt-forecaster_dow30_llama2-7b-lora")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.output_dir = Path(model_config.get("output_dir", "models/fine_tuned"))
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.model = None
        self.tokenizer = None

    def load_model(self) -> None:
        """Load base model and tokenizer."""
        logger.info(f"Loading model: {self.base_model}")

        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.base_model)
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token

            self.model = AutoModelForCausalLM.from_pretrained(
                self.base_model,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                device_map="auto" if self.device == "cuda" else None,
            )

            logger.info(f"Model loaded successfully on {self.device}")

        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise

    def setup_lora(self) -> None:
        """Set up LoRA configuration."""
        if self.model is None:
            raise ValueError("Model not loaded. Call load_model() first.")

        config = get_config()
        lora_config_dict = config.get_model_config("lora", {})

        lora_config = LoraConfig(
            task_type=TaskType.CAUSAL_LM,
            r=lora_config_dict.get("r", 16),
            lora_alpha=lora_config_dict.get("lora_alpha", 32),
            lora_dropout=lora_config_dict.get("lora_dropout", 0.1),
            target_modules=lora_config_dict.get("target_modules", ["q_proj", "v_proj"]),
        )

        self.model = get_peft_model(self.model, lora_config)
        logger.info("LoRA configuration applied")

    def prepare_dataset(self, examples: list) -> Any:
        """
        Prepare dataset for training.

        Args:
            examples: List of training examples.

        Returns:
            Tokenized dataset.
        """
        if self.tokenizer is None:
            raise ValueError("Tokenizer not loaded. Call load_model() first.")

        # Format examples as instruction-following format
        texts = []
        for example in examples:
            text = f"### Instruction:\n{example['input']}\n\n### Response:\n{example['output']}\n\n"
            texts.append(text)

        # Tokenize
        def tokenize_function(examples):
            return self.tokenizer(
                examples,
                truncation=True,
                max_length=1024,
                padding="max_length",
            )

        # Simple tokenization (in production, use datasets library)
        tokenized = tokenize_function(texts)
        return tokenized

    def train(
        self,
        train_examples: list,
        eval_examples: Optional[list] = None,
    ) -> None:
        """
        Train the model.

        Args:
            train_examples: Training examples.
            eval_examples: Optional evaluation examples.
        """
        if self.model is None:
            self.load_model()

        if not hasattr(self.model, "peft_config"):  # Check if LoRA is applied
            self.setup_lora()

        config = get_config()
        training_config = config.get_model_config("training", {})

        # Prepare datasets
        train_dataset = self.prepare_dataset(train_examples)
        eval_dataset = self.prepare_dataset(eval_examples) if eval_examples else None

        # Training arguments
        training_args = TrainingArguments(
            output_dir=str(self.output_dir),
            learning_rate=training_config.get("learning_rate", 2e-5),
            per_device_train_batch_size=training_config.get("batch_size", 8),
            gradient_accumulation_steps=training_config.get("gradient_accumulation_steps", 4),
            num_train_epochs=training_config.get("num_epochs", 5),
            warmup_steps=training_config.get("warmup_steps", 100),
            weight_decay=training_config.get("weight_decay", 0.01),
            logging_steps=training_config.get("logging_steps", 50),
            save_steps=training_config.get("save_steps", 500),
            eval_steps=training_config.get("eval_steps", 250),
            fp16=training_config.get("fp16", True) and self.device == "cuda",
            gradient_checkpointing=training_config.get("gradient_checkpointing", True),
            report_to="none",  # Disable wandb/tensorboard for now
        )

        # Data collator
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer,
            mlm=False,
        )

        # Trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=eval_dataset,
            data_collator=data_collator,
        )

        # Train
        logger.info("Starting training...")
        trainer.train()

        # Save model
        self.model.save_pretrained(self.output_dir)
        self.tokenizer.save_pretrained(self.output_dir)
        logger.info(f"Model saved to {self.output_dir}")

