import os
from pathlib import Path

# Load environment variables
def load_env():
    """Load environment variables from .env file if it exists"""
    env_file = Path(__file__).parent.parent / ".env"
    if env_file.exists():
        print(f"✓ Loading .env from: {env_file}")
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    if "=" in line:
                        key, value = line.split("=", 1)
                        key = key.strip()
                        value = value.strip()
                        # Remove quotes if present
                        if value.startswith('"') and value.endswith('"'):
                            value = value[1:-1]
                        elif value.startswith("'") and value.endswith("'"):
                            value = value[1:-1]
                        os.environ[key] = value
                        print(f"  - Loaded {key}: {value[:10]}...")
    else:
        print(f"✗ .env file not found at: {env_file}")

load_env()

# Get API keys
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

print("\n" + "="*60)
print("API KEY STATUS:")
print("="*60)
if ANTHROPIC_API_KEY:
    print(f"✓ ANTHROPIC_API_KEY loaded: {ANTHROPIC_API_KEY[:10]}...")
else:
    print("✗ ANTHROPIC_API_KEY not found")

if OPENAI_API_KEY:
    print(f"✓ OPENAI_API_KEY loaded: {OPENAI_API_KEY[:10]}...")
else:
    print("✗ OPENAI_API_KEY not found")
print("="*60 + "\n")

if not ANTHROPIC_API_KEY:
    raise ValueError("ANTHROPIC_API_KEY not found in .env file or environment")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in .env file or environment")
