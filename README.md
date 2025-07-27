# Learn LLM

## Setup

- create a requirements.txt file for required Python packages.
  - pandas and plotly for data analysis and visualization
  - streamlit for developing dashboards and apps
  - transformers and torch for using pre-trained models from Huggingface
- Create a Python virtual environment named `.venv` and install the required packages
  - `python -m venv .venv`
  - `pip install -r requirements.txt`
  - make sure to add .venv to.gitignore
- Download pre-trained models from Huggingface
  - Create a local folder `.hf_models`
  - Make sure to add .hfmodels to .gitignore
  - Run download_models.py script
- Register a Huggingface account and generate a access token

