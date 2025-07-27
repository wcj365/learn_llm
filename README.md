# Learn LLM

## Setup Python Virtual Environment

Create a Python virtual environment named `.venv`.

- Make sure you are at the project root. 
- Run `python -m venv .venv` in a terminal

**Note:**

 in VS Code, open a new terminal will automatically activate this virtual environment. All the following commands will need to be run in the virutal environment. Always make sure the .venv is active before running any commands.

## Install the required Python packages

- Make sure the .venv is activated
- Run `pip install -r requirements.txt`

## Download pre-trained models from Huggingface
  - Create a local folder outside of the project root folder and name it `huggingface_models` 
  - Modify the download_models.py script to use the folder name
  - Run the download_models.py script

## Run sentiment analysis using the downloaded model

  - Modify sentiment_analysis.py to point to the folder
  - Run the script

