"""
Model inference module.

Provides inference interface for fine-tuned model.
"""

from pathlib import Path
from typing import Any, Dict, Optional

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from src.utils.config import get_config
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ModelInference:
    """Inference interface for fine-tuned model."""

    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize model inference.

        Args:
            model_path: Path to fine-tuned model. If None, uses config default.
        """
        config = get_config()
        if model_path:
            self.model_path = Path(model_path)
        else:
            model_dir = config.get_model_config("training.output_dir", "models/fine_tuned")
            self.model_path = Path(model_dir)

        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = None
        self.tokenizer = None

        inference_config = config.get_model_config("inference", {})
        self.max_new_tokens = inference_config.get("max_new_tokens", 512)
        self.temperature = inference_config.get("temperature", 0.7)
        self.top_p = inference_config.get("top_p", 0.9)
        self.top_k = inference_config.get("top_k", 50)
        self.repetition_penalty = inference_config.get("repetition_penalty", 1.1)

    def load_model(self) -> None:
        """Load model and tokenizer."""
        if not self.model_path.exists():
            logger.warning(f"Model path not found: {self.model_path}. Using base model.")
            config = get_config()
            base_model = config.get_model_config("training.base_model", "FinGPT/fingpt-forecaster_dow30_llama2-7b-lora")
            self.model_path = None
            model_name = base_model
        else:
            model_name = str(self.model_path)

        logger.info(f"Loading model from: {model_name}")

        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token

            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                device_map="auto" if self.device == "cuda" else None,
            )
            self.model.eval()

            logger.info(f"Model loaded successfully on {self.device}")

        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise

    def generate(
        self,
        prompt: str,
        max_length: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> str:
        """
        Generate response from prompt.

        Args:
            prompt: Input prompt.
            max_length: Maximum generation length.
            temperature: Sampling temperature.

        Returns:
            Generated text.
        """
        if self.model is None or self.tokenizer is None:
            self.load_model()

        # Format prompt
        formatted_prompt = f"### Instruction:\n{prompt}\n\n### Response:\n"

        # Tokenize
        inputs = self.tokenizer(
            formatted_prompt,
            return_tensors="pt",
            truncation=True,
            max_length=512,
        ).to(self.device)

        # Generate
        max_length = max_length or self.max_new_tokens
        temperature = temperature or self.temperature

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_length,
                temperature=temperature,
                top_p=self.top_p,
                top_k=self.top_k,
                repetition_penalty=self.repetition_penalty,
                do_sample=True,
                pad_token_id=self.tokenizer.pad_token_id,
            )

        # Decode
        generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Extract response (remove prompt)
        if "### Response:" in generated_text:
            response = generated_text.split("### Response:")[-1].strip()
        else:
            response = generated_text[len(formatted_prompt):].strip()

        return response

    def generate_with_context(
        self,
        query: str,
        context: Optional[str] = None,
    ) -> str:
        """
        Generate response with additional context.

        Args:
            query: User query.
            context: Additional context to include.

        Returns:
            Generated response.
        """
        if context:
            prompt = f"Context: {context}\n\nQuestion: {query}\n\nAnswer:"
        else:
            prompt = f"Question: {query}\n\nAnswer:"

        return self.generate(prompt)

