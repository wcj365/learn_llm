from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import torch

# Replace with the path to your local model directory
local_model_path = "../models"

# Load the tokenizer and model from the local path
tokenizer = AutoTokenizer.from_pretrained(local_model_path)
model = AutoModelForSequenceClassification.from_pretrained(local_model_path)

# Create a sentiment-analysis pipeline using the local model
sentiment_pipeline = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)

# Example usage
texts = [
    "I absolutely love this!",
    "This is the worst experience I've had."
]

# Run sentiment analysis
results = sentiment_pipeline(texts)

# Output the results
for text, result in zip(texts, results):
    print(f"Text: {text}\nLabel: {result['label']}, Score: {result['score']:.4f}\n")
