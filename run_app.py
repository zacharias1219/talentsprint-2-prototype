"""
Financial Advisor Application Launcher.

This script provides a unified way to launch different components of the application.
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

PROJECT_ROOT = Path(__file__).parent


def run_streamlit():
    """Launch the Streamlit web interface."""
    print("🚀 Starting Streamlit Web Interface...")
    print("=" * 50)
    print("Open your browser at: http://localhost:8501")
    print("Press Ctrl+C to stop")
    print("=" * 50)
    
    ui_app = PROJECT_ROOT / "ui" / "streamlit_app.py"
    subprocess.run([sys.executable, "-m", "streamlit", "run", str(ui_app)])


def run_api():
    """Launch the FastAPI REST server."""
    print("🚀 Starting REST API Server...")
    print("=" * 50)
    print("API available at: http://localhost:8000")
    print("API Docs at: http://localhost:8000/docs")
    print("Press Ctrl+C to stop")
    print("=" * 50)
    
    subprocess.run([
        sys.executable, "-m", "uvicorn", 
        "src.api.rest_api:app", 
        "--host", "0.0.0.0", 
        "--port", "8000",
        "--reload"
    ])


def run_inference_test():
    """Run the inference script to test the model."""
    print("🧪 Running Inference Test...")
    print("=" * 50)
    
    inference_script = PROJECT_ROOT / "scripts" / "inference.py"
    subprocess.run([sys.executable, str(inference_script)])


def run_personalization():
    """Generate user recommendations."""
    print("📊 Generating User Recommendations...")
    print("=" * 50)
    
    personalization_script = PROJECT_ROOT / "scripts" / "personalization_engine.py"
    subprocess.run([sys.executable, str(personalization_script)])


def run_data_acquisition():
    """Fetch market data and generate training data."""
    print("📥 Running Data Acquisition...")
    print("=" * 50)
    
    data_script = PROJECT_ROOT / "scripts" / "data_acquisition.py"
    subprocess.run([sys.executable, str(data_script)])


def run_evaluation():
    """Evaluate the fine-tuned model."""
    print("📈 Running Model Evaluation...")
    print("=" * 50)
    
    eval_script = PROJECT_ROOT / "scripts" / "evaluate_model.py"
    subprocess.run([sys.executable, str(eval_script)])


def check_requirements():
    """Check if all requirements are installed."""
    print("🔍 Checking Requirements...")
    
    try:
        import streamlit
        import torch
        import transformers
        import peft
        import fastapi
        import plotly
        print("✅ All core requirements are installed.")
        return True
    except ImportError as e:
        print(f"❌ Missing requirement: {e}")
        print("\nPlease install requirements with:")
        print("  pip install -r requirements.txt")
        return False


def show_status():
    """Show application status."""
    print("=" * 50)
    print("📋 Financial Advisor Application Status")
    print("=" * 50)
    
    # Check model
    model_path = PROJECT_ROOT / "models" / "fine_tuned" / "financial_advisor" / "adapter_config.json"
    if model_path.exists():
        import json
        with open(model_path) as f:
            config = json.load(f)
        print(f"✅ Fine-tuned model found")
        print(f"   Base model: {config.get('base_model_name_or_path', 'unknown')}")
    else:
        print("❌ Fine-tuned model not found")
        print("   Run: python scripts/train_model.py")
    
    # Check user recommendations
    recs_path = PROJECT_ROOT / "data" / "processed" / "user_recommendations.json"
    if recs_path.exists():
        import json
        with open(recs_path) as f:
            recs = json.load(f)
        print(f"✅ User recommendations found ({len(recs)} users)")
    else:
        print("❌ User recommendations not found")
        print("   Run: python scripts/personalization_engine.py")
    
    # Check training data
    training_path = PROJECT_ROOT / "data" / "processed" / "training_data.json"
    if training_path.exists():
        print("✅ Training data found")
    else:
        print("❌ Training data not found")
        print("   Run: python scripts/data_acquisition.py")
    
    # Check evaluation results
    eval_path = PROJECT_ROOT / "models" / "evaluation_results.json"
    if eval_path.exists():
        import json
        with open(eval_path) as f:
            results = json.load(f)
        print(f"✅ Evaluation results found")
        print(f"   BLEU: {results.get('bleu_score', 0):.4f}")
    else:
        print("⚠️  Evaluation results not found")
        print("   Run: python scripts/evaluate_model.py")
    
    print("=" * 50)


def main():
    parser = argparse.ArgumentParser(
        description="Financial Advisor Application Launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_app.py ui          # Launch Streamlit web interface
  python run_app.py api         # Launch REST API server
  python run_app.py test        # Run inference test
  python run_app.py status      # Check application status
  python run_app.py setup       # Run full setup (data + recommendations)
        """
    )
    
    parser.add_argument(
        "command",
        choices=["ui", "api", "test", "status", "setup", "eval", "data"],
        help="Command to run"
    )
    
    args = parser.parse_args()
    
    # Change to project root
    os.chdir(PROJECT_ROOT)
    
    if args.command == "ui":
        if check_requirements():
            run_streamlit()
    elif args.command == "api":
        if check_requirements():
            run_api()
    elif args.command == "test":
        run_inference_test()
    elif args.command == "status":
        show_status()
    elif args.command == "setup":
        print("🔧 Running Full Setup...")
        run_data_acquisition()
        run_personalization()
        show_status()
    elif args.command == "eval":
        run_evaluation()
    elif args.command == "data":
        run_data_acquisition()


if __name__ == "__main__":
    main()

