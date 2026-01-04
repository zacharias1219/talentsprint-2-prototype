"""
Inference Script: Using the Fine-Tuned Model for Financial Advisory.

This script loads the fine-tuned model and integrates it with the RAG pipeline
to generate actual financial advice responses.
"""

import os
import sys
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

# Add scripts directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rag_pipeline import FinancialRAGPipeline

class FinancialAdvisorInference:
    def __init__(self, model_path="./models/fine_tuned/financial_advisor", base_model="TinyLlama/TinyLlama-1.1B-Chat-v1.0"):
        """
        Initialize the inference engine with the fine-tuned model.
        
        Args:
            model_path: Path to the fine-tuned LoRA adapter
            base_model: Base model name (must match what was fine-tuned)
        """
        print(f"Loading fine-tuned model from {model_path}...")
        
        # Load base model and tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(base_model)
        self.tokenizer.pad_token = self.tokenizer.eos_token
        
        # Use FP16/CUDA if available
        dtype = torch.float16 if torch.cuda.is_available() else torch.float32
        device_map = "auto" if torch.cuda.is_available() else None
        
        base_model_obj = AutoModelForCausalLM.from_pretrained(
            base_model,
            torch_dtype=dtype,
            device_map=device_map,
            trust_remote_code=True
        )
        
        # Load LoRA adapter
        if os.path.exists(model_path):
            self.model = PeftModel.from_pretrained(base_model_obj, model_path)
            print("[OK] Fine-tuned adapter loaded successfully")
        else:
            print(f"[!] Warning: Model path {model_path} not found. Using base model only.")
            self.model = base_model_obj
        
        self.model.eval()
        
        # Initialize RAG pipeline for context retrieval
        self.rag = FinancialRAGPipeline()
        
    def generate_response(self, user_id: str, query: str, max_length=200, temperature=0.7):
        """
        Generate a financial advisory response using the fine-tuned model + RAG context.
        
        Args:
            user_id: User identifier
            query: User's financial question
            max_length: Maximum response length
            temperature: Sampling temperature (lower = more deterministic)
        """
        # Get context from RAG pipeline
        context = self.rag.retrieve_context(user_id, query)
        
        if context == "User not found.":
            return "Error: User profile not found. Please ensure user_recommendations.json exists."
        
        # Enhanced prompt template matching training format
        prompt = f"""<|system|>
You are an expert Financial Advisor AI. Provide accurate, compliant financial advice based on the user's question and context.
Always include appropriate disclaimers and cite specific data when available.
<|user|>
### Instruction:
Utilize your financial knowledge and the provided context to give your answer or opinion to the input question or subject.

### Input:
Context:
{context}

User Question: {query}

### Response:
"""
        
        # Tokenize
        inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)
        
        # Generate
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_length=inputs.input_ids.shape[1] + max_length,
                temperature=temperature,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id,
                eos_token_id=self.tokenizer.eos_token_id
            )
        
        # Decode response
        full_response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract only the response part (after "### RESPONSE:")
        if "### RESPONSE:" in full_response:
            response = full_response.split("### RESPONSE:")[-1].strip()
        else:
            response = full_response[len(prompt):].strip()
        
        return response

    def generate_response_with_context(self, context: str, query: str, max_length=200, temperature=0.7):
        """
        Generate a financial advisory response using provided context directly.
        
        Args:
            context: Pre-built context string (user profile + recommendations)
            query: User's financial question
            max_length: Maximum response length
            temperature: Sampling temperature
        """
        # Enhanced prompt template matching training format
        prompt = f"""<|system|>
You are an expert Financial Advisor AI. Provide accurate, compliant financial advice based on the user's question and context.
Always include appropriate disclaimers and cite specific data when available.
<|user|>
### Instruction:
Utilize your financial knowledge and the provided context to give your answer or opinion to the input question or subject.

### Input:
Context:
{context}

User Question: {query}

### Response:
"""
        
        # Tokenize
        inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)
        
        # Move to same device as model
        if hasattr(self.model, 'device'):
            inputs = {k: v.to(self.model.device) for k, v in inputs.items()}
        
        # Generate
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_length=inputs['input_ids'].shape[1] + max_length,
                temperature=temperature,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
                repetition_penalty=1.2
            )
        
        # Decode response
        full_response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract only the response part
        if "### Response:" in full_response:
            response = full_response.split("### Response:")[-1].strip()
        elif "### RESPONSE:" in full_response:
            response = full_response.split("### RESPONSE:")[-1].strip()
        else:
            response = full_response[len(prompt):].strip()
        
        # Clean up any trailing instruction markers
        for marker in ["### Instruction:", "<|user|>", "<|system|>", "###"]:
            if marker in response:
                response = response.split(marker)[0].strip()
        
        return response


def main():
    print("=" * 60)
    print("Financial Advisor Inference Engine")
    print("=" * 60)
    
    # Initialize inference engine
    advisor = FinancialAdvisorInference()
    
    # Test queries
    user_id = "user_1000"
    
    test_queries = [
        "Should I invest in mutual funds or ETFs this year?",
        "What do you think about buying Apple stock right now?",
        "How should I rebalance my portfolio?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*60}")
        print(f"Query {i}: {query}")
        print('='*60)
        
        try:
            response = advisor.generate_response(user_id, query)
            print(f"\nResponse:\n{response}\n")
        except Exception as e:
            print(f"Error generating response: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()




