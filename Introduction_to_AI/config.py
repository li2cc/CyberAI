import os
from pathlib import Path

# Load environment variables
def load_env():
    """Load environment variables from .env file if it exists"""
    env_file = Path(__file__).parent.parent / ".env"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    key, value = line.split("=", 1)
                    os.environ[key.strip()] = value.strip()

load_env()

# Get API keys
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not ANTHROPIC_API_KEY:
    raise ValueError("ANTHROPIC_API_KEY not found in .env file or environment")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in .env file or environment")
