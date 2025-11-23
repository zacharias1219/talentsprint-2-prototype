"""
Model training script.

Trains the fine-tuned model on financial data.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.model_training.data_preparation import DataPreparation
from src.model_training.fine_tuning import FineTuner
from src.utils.logger import get_logger

logger = get_logger(__name__)


def main():
    """Main training function."""
    logger.info("Starting model training...")

    # Prepare data
    data_prep = DataPreparation()
    training_data_file = "data/processed/training_data.json"

    # Load training data
    train_examples = data_prep.load_training_data("training_data.json")
    if not train_examples:
        logger.error("No training data found. Please prepare training data first.")
        sys.exit(1)

    # Split into train and eval (80/20)
    split_idx = int(len(train_examples) * 0.8)
    train_set = train_examples[:split_idx]
    eval_set = train_examples[split_idx:]

    logger.info(f"Training examples: {len(train_set)}, Evaluation examples: {len(eval_set)}")

    # Initialize fine-tuner
    fine_tuner = FineTuner()
    fine_tuner.load_model()
    fine_tuner.setup_lora()

    # Train model
    fine_tuner.train(train_set, eval_set)

    logger.info("Model training completed successfully!")


if __name__ == "__main__":
    main()

