"""
Model evaluation module.

Evaluates model performance on test datasets.
"""

from typing import Any, Dict, List, Optional

from src.model_training.inference import ModelInference
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ModelEvaluator:
    """Evaluator for model performance."""

    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize model evaluator.

        Args:
            model_path: Path to model for evaluation.
        """
        self.inference = ModelInference(model_path)

    def evaluate_accuracy(
        self,
        test_examples: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Evaluate model accuracy on test examples.

        Args:
            test_examples: List of test examples with 'input' and 'expected_output'.

        Returns:
            Dictionary with accuracy metrics.
        """
        correct = 0
        total = len(test_examples)
        results = []

        for example in test_examples:
            input_text = example["input"]
            expected_output = example.get("expected_output", example.get("output", ""))

            # Generate response
            generated_output = self.inference.generate(input_text)

            # Simple exact match (in production, use semantic similarity)
            is_correct = expected_output.lower().strip() == generated_output.lower().strip()
            if is_correct:
                correct += 1

            results.append({
                "input": input_text,
                "expected": expected_output,
                "generated": generated_output,
                "correct": is_correct,
            })

        accuracy = correct / total if total > 0 else 0.0

        logger.info(f"Accuracy: {accuracy:.2%} ({correct}/{total})")

        return {
            "accuracy": accuracy,
            "correct": correct,
            "total": total,
            "results": results,
        }

    def evaluate_financial_qa(
        self,
        qa_pairs: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Evaluate on financial Q&A dataset.

        Args:
            qa_pairs: List of question-answer pairs.

        Returns:
            Dictionary with evaluation metrics.
        """
        return self.evaluate_accuracy(qa_pairs)

    def generate_evaluation_report(
        self,
        test_examples: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Generate comprehensive evaluation report.

        Args:
            test_examples: Test examples.

        Returns:
            Evaluation report dictionary.
        """
        # Overall accuracy
        accuracy_results = self.evaluate_accuracy(test_examples)

        # Per-domain accuracy
        domain_results = {}
        domains = set(example.get("domain", "unknown") for example in test_examples)

        for domain in domains:
            domain_examples = [ex for ex in test_examples if ex.get("domain") == domain]
            if domain_examples:
                domain_accuracy = self.evaluate_accuracy(domain_examples)
                domain_results[domain] = domain_accuracy["accuracy"]

        report = {
            "overall_accuracy": accuracy_results["accuracy"],
            "total_examples": accuracy_results["total"],
            "correct_examples": accuracy_results["correct"],
            "per_domain_accuracy": domain_results,
            "detailed_results": accuracy_results["results"],
        }

        return report

