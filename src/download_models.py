from transformers import AutoTokenizer, AutoModelForSequenceClassification

model_name = "distilbert-base-uncased-finetuned-sst-2-english"
model_dir = f"C:/Users/WangC/Projects/huggingface_models/{model_name}"

# Load from Hugging Face Hub
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

# Save to local folder
tokenizer.save_pretrained(model_dir)
model.save_pretrained(model_dir)
