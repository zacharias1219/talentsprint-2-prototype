"""
Data preparation module for model training.

Prepares financial data and examples for fine-tuning.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.utils.logger import get_logger

logger = get_logger(__name__)


class DataPreparation:
    """Prepares training data for fine-tuning."""

    def __init__(self, data_dir: Optional[str] = None):
        """
        Initialize data preparation.

        Args:
            data_dir: Directory containing training data.
        """
        if data_dir:
            self.data_dir = Path(data_dir)
        else:
            self.data_dir = Path("data/processed")
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def create_training_example(
        self,
        input_text: str,
        output_text: str,
        domain: str,
        risk_level: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a training example.

        Args:
            input_text: Input query or context.
            output_text: Expected output response.
            domain: Domain category ('investment', 'retirement', 'savings', etc.).
            risk_level: Risk level ('low', 'medium', 'high').
            metadata: Optional metadata dictionary.

        Returns:
            Training example dictionary.
        """
        example = {
            "input": input_text,
            "output": output_text,
            "domain": domain,
            "risk_level": risk_level,
            "source": metadata.get("source", "expert") if metadata else "expert",
            "metadata": metadata or {},
        }
        return example

    def format_for_training(
        self,
        examples: List[Dict[str, Any]],
        format_type: str = "instruction",
    ) -> List[Dict[str, Any]]:
        """
        Format examples for training.

        Args:
            examples: List of training examples.
            format_type: Format type ('instruction', 'chat', 'completion').

        Returns:
            Formatted examples.
        """
        formatted = []

        for example in examples:
            if format_type == "instruction":
                formatted_example = {
                    "instruction": example["input"],
                    "input": "",
                    "output": example["output"],
                }
            elif format_type == "chat":
                formatted_example = {
                    "messages": [
                        {"role": "user", "content": example["input"]},
                        {"role": "assistant", "content": example["output"]},
                    ],
                }
            else:  # completion
                prompt = f"Question: {example['input']}\nAnswer: "
                formatted_example = {
                    "prompt": prompt,
                    "completion": example["output"],
                }

            formatted.append(formatted_example)

        return formatted

    def save_training_data(
        self,
        examples: List[Dict[str, Any]],
        filename: str,
    ) -> None:
        """
        Save training data to file.

        Args:
            examples: List of training examples.
            filename: Output filename.
        """
        file_path = self.data_dir / filename
        with open(file_path, "w") as f:
            json.dump(examples, f, indent=2)

        logger.info(f"Saved {len(examples)} training examples to {file_path}")

    def load_training_data(self, filename: str) -> List[Dict[str, Any]]:
        """
        Load training data from file.

        Args:
            filename: Input filename.

        Returns:
            List of training examples.
        """
        file_path = self.data_dir / filename
        if not file_path.exists():
            logger.warning(f"Training data file not found: {file_path}")
            return []

        with open(file_path, "r") as f:
            examples = json.load(f)

        logger.info(f"Loaded {len(examples)} training examples from {file_path}")
        return examples

