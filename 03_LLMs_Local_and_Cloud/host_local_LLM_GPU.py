"""Host a capable open LLM on a GPU and chat with it — script version of the
Module 3 notebook's core (see host_LLM_GPU.ipynb for the full guided lecture).

Loads Qwen2.5-7B-Instruct in 4-bit so it fits a 16 GB GPU (e.g., a Colab T4),
then answers a cybersecurity prompt. Swap MODEL_ID for a smaller model
(e.g., Qwen/Qwen2.5-3B-Instruct or microsoft/Phi-3.5-mini-instruct) if needed.

Setup:  pip install -U transformers accelerate bitsandbytes torch
Run:    python host_local_LLM_GPU.py
"""
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

MODEL_ID = "Qwen/Qwen2.5-7B-Instruct"   # capable + open (Apache-2.0); fits a T4 in 4-bit

bnb = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
)

tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID, quantization_config=bnb, device_map="auto"
)
print(f"Loaded {MODEL_ID} on {model.device}")


def chat(prompt, system="You are a concise cybersecurity assistant.", max_new_tokens=256):
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": prompt},
    ]
    ids = tokenizer.apply_chat_template(
        messages, add_generation_prompt=True, return_tensors="pt"
    ).to(model.device)
    out = model.generate(ids, max_new_tokens=max_new_tokens, do_sample=False)
    return tokenizer.decode(out[0][ids.shape[-1]:], skip_special_tokens=True)


if __name__ == "__main__":
    alert = ("5 failed logins for 'admin' from 203.0.113.7 in 20 seconds, "
             "then 1 success and a new scheduled task.")
    print(chat(f"Classify this alert as benign or suspicious and explain in one sentence:\n{alert}"))
