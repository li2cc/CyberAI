# Security Alert Classifier

This project classifies security alerts as benign or suspicious using Claude and OpenAI APIs.

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Create `.env` file

Create a `.env` file in the project root directory (`your_project_root\.env`):

```
ANTHROPIC_API_KEY=sk-ant-your-key-here
OPENAI_API_KEY=sk-your-openai-key-here
```

### 3. Run the Script

```bash
python Introduction_to_AI/alert_classifier.py
```

## Files

- `alert_classifier.py` - Main alert classification script
- `config.py` - Configuration and environment variable loader
- `SimpleAlertClassifier.ipynb` - Jupyter notebook version (for Google Colab)
- `requirements.txt` - Python dependencies

## How It Works

The script:
1. Takes a security alert as input
2. Sends it to Claude API for classification
3. Sends it to OpenAI API for classification
4. Displays results from both APIs side-by-side

Example alert:
```
5 failed logins for 'admin' from 203.0.113.7 in 20s, then 1 success
```

Both APIs will classify this as SUSPICIOUS (potential brute-force attack).
