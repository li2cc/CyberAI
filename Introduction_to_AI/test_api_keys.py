"""
Test script to verify API keys are working correctly
"""

from config import ANTHROPIC_API_KEY, OPENAI_API_KEY
from anthropic import Anthropic
from openai import OpenAI

print("\n" + "="*60)
print("TESTING API KEYS")
print("="*60 + "\n")

# Test Anthropic
print("Testing Anthropic API...")
try:
    client = Anthropic(api_key=ANTHROPIC_API_KEY)
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=50,
        messages=[{"role": "user", "content": "Say 'Anthropic works!' in one sentence."}]
    )
    print(f"✓ Anthropic API works!")
    print(f"  Response: {response.content[0].text}\n")
except Exception as e:
    print(f"✗ Anthropic API failed: {str(e)}\n")

# Test OpenAI
print("Testing OpenAI API...")
try:
    client = OpenAI(api_key=OPENAI_API_KEY)
    response = client.chat.completions.create(
        model="gpt-4-mini",
        max_tokens=50,
        messages=[{"role": "user", "content": "Say 'OpenAI works!' in one sentence."}]
    )
    print(f"✓ OpenAI API works!")
    print(f"  Response: {response.choices[0].message.content}\n")
except Exception as e:
    print(f"✗ OpenAI API failed: {str(e)}\n")

print("="*60)
