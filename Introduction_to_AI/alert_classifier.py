"""
Alert Classifier using Claude and OpenAI APIs
Classifies security alerts as benign or suspicious
"""

from anthropic import Anthropic
from openai import OpenAI
import textwrap
from config import ANTHROPIC_API_KEY, OPENAI_API_KEY


def classify_with_claude(alert: str) -> str:
    """Classify alert using Claude API"""
    client = Anthropic(api_key=ANTHROPIC_API_KEY)

    msg = client.messages.create(
        model='claude-haiku-4-5-20251001',
        max_tokens=150,
        messages=[{
            'role': 'user',
            'content': f'Classify benign/suspicious and explain in one sentence: {alert}'
        }]
    )

    return msg.content[0].text


def classify_with_openai(alert: str) -> str:
    """Classify alert using OpenAI API"""
    client = OpenAI(api_key=OPENAI_API_KEY)

    response = client.chat.completions.create(
        model="gpt-4-mini",
        messages=[{
            "role": "user",
            "content": f"Classify benign/suspicious and explain in one sentence: {alert}"
        }]
    )

    return response.choices[0].message.content


def main():
    # Sample alert
    alert = "5 failed logins for 'admin' from 203.0.113.7 in 20s, then 1 success"

    print("=" * 60)
    print("SECURITY ALERT CLASSIFIER")
    print("=" * 60)
    print(f"\nAlert: {alert}\n")

    # Classify with Claude
    print("Claude Analysis:")
    print("-" * 60)
    claude_result = classify_with_claude(alert)
    print(claude_result)

    print("\n" + "=" * 60)

    # Classify with OpenAI
    print("OpenAI Analysis:")
    print("-" * 60)
    openai_result = classify_with_openai(alert)
    # Wrap text for readability
    wrapped = "\n".join(textwrap.wrap(openai_result, width=50))
    print(wrapped)

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
