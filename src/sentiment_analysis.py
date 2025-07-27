from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import torch

model_name = "distilbert-base-uncased-finetuned-sst-2-english"
model_dir = f"C:/Users/WangC/Projects/huggingface_models/{model_name}"

# Load the tokenizer and model from the local path
tokenizer = AutoTokenizer.from_pretrained(model_dir)
model = AutoModelForSequenceClassification.from_pretrained(model_dir)

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
