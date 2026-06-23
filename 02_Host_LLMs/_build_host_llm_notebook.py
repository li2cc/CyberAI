"""Generator for host_LLM_GPU.ipynb — Module 3 hands-on notebook.

Guides students to run an LLM three ways — cloud API (recall), local CPU (Ollama),
and a capable model on a free Colab T4 GPU (Hugging Face transformers, 4-bit) —
then explore the Hugging Face Hub and swap in their own model. Designed for ~40
minutes of in-class use. Ships WITHOUT executed outputs (it runs live on Colab
with a T4 GPU and downloads models).

Run:  python _build_host_llm_notebook.py   ->  writes host_LLM_GPU.ipynb
"""
import json

cells = []


def md(src):
    cells.append({"cell_type": "markdown", "metadata": {}, "source": src.splitlines(keepends=True)})


def code(src):
    cells.append({"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [],
                  "source": src.rstrip("\n").splitlines(keepends=True)})


def slide(title, bullets):
    md(f"# {title}\n\n" + "\n".join(f"- {b}" for b in bullets))


def script(text):
    md("> ### \U0001F3A4 Instructor Script\n>\n> " + text.replace("\n", "\n> "))


# ---------------------------------------------------------------------------
md(
    "# Hosting LLMs: From Your Laptop to a Cloud GPU\n"
    "### Module 3 — LLMs on Local & Cloud\n\n"
    "**Audience:** Students who finished Module 2 (a working environment: VS Code, Python, GitHub, "
    "Colab + Drive, and an API key in a hidden variable).\n\n"
    "**Goal:** run an LLM **three ways** and feel the trade-offs — a **cloud API** (recall from "
    "Module 2), a **small model locally on CPU** (no NVIDIA card needed), and a **capable model on a "
    "free Colab T4 GPU** — then **explore the Hugging Face Hub**, pick your own model, host it, and "
    "compare.\n\n"
    "> \U0001F3AC **New to LLM vocabulary?** Watch this fast primer on the basic terms first: "
    "https://www.youtube.com/watch?v=GtfqAr9CAgg\n\n"
    "> ⚡ **Runtime:** for the GPU section, set **Runtime → Change runtime type → T4 GPU** before "
    "running. The local section uses **Ollama on CPU**, so it works on any laptop."
)

# ---- 0: check runtime --------------------------------------------------------
slide("\U0001F50C 0 — Check Your Runtime", [
    "Confirm whether you have a GPU and which one",
    "On Colab: Runtime → Change runtime type → **T4 GPU**",
    "`nvidia-smi` shows the GPU; `torch.cuda` confirms PyTorch sees it",
    "No GPU? The local (Ollama/CPU) section still works",
])
script(
    "Before anything else, know what hardware you are on. Run nvidia-smi to see the GPU and how much "
    "memory it has — a Colab T4 gives you about 16 GB of vRAM, which is the budget that decides which "
    "models will fit. Then we ask PyTorch whether it can see the GPU; if CUDA is available, our model "
    "will run on the GPU and be fast, and if not, it falls back to CPU and will be slow. If you forgot "
    "to switch the runtime to T4, this is where you'll notice — go change it now and re-run."
)
code(
    r'''!nvidia-smi

import torch
print("CUDA available:", torch.cuda.is_available())
print("Device:", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU only")'''
)

# ---- 1: three ways -----------------------------------------------------------
slide("\U0001F5FA️ 1 — Three Ways to Run an LLM", [
    "**Cloud API** — someone else's GPU; you send text, pay per token",
    "**Local (your laptop)** — your CPU/GPU; free, private, offline",
    "**Cloud GPU (Colab)** — a rented GPU you control for a session",
    "Same model idea, very different cost, privacy, and speed",
    "This notebook runs all three so you feel the difference",
])
script(
    "There are three places an LLM can run, and the whole module is about feeling the trade-offs "
    "between them. A cloud API like OpenAI or Anthropic is the easiest and most powerful, but your "
    "data leaves your machine and you pay for every token. Running locally on your own laptop is "
    "free, private, and works offline, but you're limited by your hardware. A cloud GPU like Colab's "
    "T4 sits in the middle: a capable rented GPU you control for the length of a session, perfect for "
    "experiments. None is best for everything — the skill is choosing the right one for the task, "
    "which is exactly what your lab and the comparison report ask you to do."
)
code(
    r'''rows = [
    ("",            "Cloud API",        "Local (laptop)",   "Cloud GPU (Colab T4)"),
    ("Cost",        "per token ($)",    "free",             "free tier / session"),
    ("Privacy",     "data leaves you",  "fully private",    "session on rented VM"),
    ("Capability",  "highest",          "limited by HW",    "good (7-8B models)"),
    ("Setup",       "an API key",       "install Ollama",   "pick T4, pip install"),
]
for r in rows:
    print(f"{r[0]:12}{r[1]:18}{r[2]:18}{r[3]}")'''
)

# ---- 2: API recall -----------------------------------------------------------
slide("☁️ 2 — Way 1: Cloud API (Recall from Module 2)", [
    "You already set up an API key in a hidden variable",
    "This is the baseline: most capable, simplest code",
    "But: per-token cost, and your prompt leaves your machine",
    "We'll compare local & Colab against this baseline",
])
script(
    "Let's anchor on what you already know. In Module 2 you stored an API key in a hidden variable and "
    "made a call. That hosted model is our baseline — the most capable and the least setup, just a few "
    "lines of code. The catch is the two things we'll keep coming back to: you pay per token, and your "
    "prompt is sent to a third party. The cell below makes one quick call if a key is present and "
    "otherwise skips, so the notebook runs either way. Keep this answer in mind; we'll ask the local "
    "and Colab models the same question and compare."
)
code(
    r'''import os
# Optional: paste your key into Colab Secrets (key icon) as OPENAI_API_KEY, or skip this cell.
try:
    from google.colab import userdata
    os.environ.setdefault("OPENAI_API_KEY", userdata.get("OPENAI_API_KEY"))
except Exception:
    pass

PROMPT = "In two sentences, what is SOC alert triage in cybersecurity?"

if os.getenv("OPENAI_API_KEY"):
    from openai import OpenAI
    client = OpenAI()
    r = client.chat.completions.create(model="gpt-4o-mini",
        messages=[{"role": "user", "content": PROMPT}])
    print("[API gpt-4o-mini]\n", r.choices[0].message.content)
else:
    print("No API key set — skipping the API baseline (that's fine).")'''
)

# ---- 3: local Ollama ---------------------------------------------------------
slide("\U0001F4BB 3 — Way 2: Local on Your Laptop (Ollama, CPU)", [
    "Install **Ollama** (ollama.com) — works with no NVIDIA card",
    "Pick a **small** model so it runs on CPU: `llama3.2:1b`, `qwen2.5:1.5b`",
    "Interact in your **terminal**: `ollama run llama3.2:1b`",
    "Free, private, offline — but small and slower on CPU",
    "Even if you have a GPU, start small (we use the GPU on Colab)",
])
script(
    "Now the opposite extreme: your own laptop, for free. Ollama is the de-facto tool for running "
    "models locally — install it from ollama.com, and it works even without an NVIDIA card by running "
    "on your CPU. The trick is to choose a small model so CPU inference stays bearable: a one-to-two "
    "billion parameter model like llama3.2:1b or qwen2.5:1.5b. You talk to it right in your terminal "
    "with 'ollama run'. It won't be as sharp as a frontier API, but it's genuinely useful, completely "
    "private, and costs nothing. Run these commands on your own laptop's terminal; the cell here shows "
    "the exact steps, and the optional cell after it runs Ollama inside Colab so you can see the same "
    "terminal-style interaction live."
)
code(
    r'''# ---- Run these in YOUR laptop's terminal (not here) ----
# 1) Install Ollama from https://ollama.com  (Windows / macOS / Linux)
# 2) Pull and chat with a small model that runs on CPU:
#       ollama run llama3.2:1b
#    then type your question at the prompt. Try:
#       "In two sentences, what is SOC alert triage?"
# 3) Other small models to try:  qwen2.5:1.5b   gemma2:2b   phi3.5
print("Local Ollama steps above — run them in your laptop terminal.")'''
)
md("**Optional — run Ollama inside Colab** to see the terminal / `!` style of interaction "
   "(this uses the Colab machine, not your laptop):")
code(
    r'''# Optional demo: Ollama in Colab (terminal/"!" style interaction)
!curl -fsSL https://ollama.com/install.sh | sh
import subprocess, time
subprocess.Popen(["ollama", "serve"])      # start the server in the background
time.sleep(5)
!ollama run llama3.2:1b "In two sentences, what is SOC alert triage?"'''
)

# ---- 4: Colab GPU host -------------------------------------------------------
slide("\U0001F680 4 — Way 3: Host a Capable Model on the T4 GPU", [
    "Load a **capable** open model from Hugging Face: Qwen2.5-7B-Instruct",
    "It fits a 16 GB T4 using **4-bit quantization** (bitsandbytes)",
    "`transformers` downloads the weights and runs them on the GPU",
    "First load downloads several GB — give it a few minutes",
    "Open (Apache-2.0), no gated-access token needed",
])
script(
    "Here's the heart of the lecture: hosting a genuinely capable model on Colab's free T4. We use "
    "Qwen2.5-7B-Instruct — a strong, openly licensed model — and load it in 4-bit precision with "
    "bitsandbytes so its weights shrink to about five gigabytes and fit comfortably in the T4's "
    "sixteen. The transformers library downloads the model from the Hugging Face Hub the first time, "
    "which takes a few minutes, then places it on the GPU. We deliberately picked an ungated model so "
    "nobody gets stuck on access tokens. If the download or memory ever feels too heavy, swap the "
    "model id for the smaller Qwen2.5-3B-Instruct — one line — and everything else still works."
)
code(
    r'''!pip install -q -U transformers accelerate bitsandbytes

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

MODEL_ID = "Qwen/Qwen2.5-7B-Instruct"      # capable + open; fits a T4 in 4-bit
# Lighter alternative if you hit memory/time limits: "Qwen/Qwen2.5-3B-Instruct"

bnb = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4",
                         bnb_4bit_compute_dtype=torch.float16)
tok = AutoTokenizer.from_pretrained(MODEL_ID)
model = AutoModelForCausalLM.from_pretrained(MODEL_ID, quantization_config=bnb, device_map="auto")
print("Loaded", MODEL_ID, "on", model.device)'''
)
md("Now a small `chat()` helper, then ask it the **same** question we asked the API:")
code(
    r'''def chat(prompt, system="You are a concise cybersecurity assistant.", max_new_tokens=256):
    messages = [{"role": "system", "content": system},
                {"role": "user", "content": prompt}]
    ids = tok.apply_chat_template(messages, add_generation_prompt=True, return_tensors="pt").to(model.device)
    out = model.generate(ids, max_new_tokens=max_new_tokens, do_sample=False)
    return tok.decode(out[0][ids.shape[-1]:], skip_special_tokens=True)

print(chat("In two sentences, what is SOC alert triage in cybersecurity?"))'''
)

# ---- 5: three interaction modes ---------------------------------------------
slide("⌨️ 5 — Three Ways to Interact", [
    "**Python code** — call `chat(...)` (what we just did)",
    "**`!` in a cell** — run shell tools, e.g. `!nvidia-smi`, `!ollama run ...`",
    "**Terminal** — the same commands on your laptop or a VM",
    "Pick whatever fits your workflow; the model is the same",
])
script(
    "You can drive a model three ways, and you've now seen all of them. Inside Python you call a "
    "function like our chat helper — best when the model is one step in a bigger program, which is "
    "where this course is heading with agents. The exclamation mark in a notebook cell runs shell "
    "commands, like nvidia-smi to watch GPU memory, or ollama run to chat from the shell. And a plain "
    "terminal — on your laptop or on a NAIRR virtual machine later — runs those same commands. The "
    "interaction style is just convenience; the underlying model and prompt are identical. Let's watch "
    "GPU memory with a shell command while the model is loaded."
)
code(
    r'''# "!" shell interaction: check how much GPU memory the loaded model is using
!nvidia-smi --query-gpu=memory.used,memory.total --format=csv

# Python interaction: a security-flavored prompt
print(chat("List three signs that a login attempt might be a brute-force attack."))'''
)

# ---- 6: explore Hugging Face -------------------------------------------------
slide("\U0001F917 6 — Explore the Hugging Face Hub", [
    "huggingface.co/models — filter by **Text Generation**, sort by trending",
    "Read the **model card**: size, license, and whether it's *gated*",
    "Match the size to your GPU: ~7-8B fits a T4 in 4-bit; 1-3B is easy",
    "Open licenses (Apache-2.0, MIT) avoid access-token hassles",
    "Good families to try: Qwen2.5, Gemma 2, Phi-3.5, Mistral",
])
script(
    "The Hugging Face Hub is the app store of open models, and learning to shop there is a real skill. "
    "Go to huggingface.co/models, filter by the Text Generation task, and sort by trending or "
    "downloads to see what the community actually uses. Open each candidate's model card and check "
    "three things: the parameter size, which tells you if it fits your GPU; the license, where "
    "Apache-2.0 or MIT mean you can use it freely; and whether it's gated, which would require "
    "requesting access. For a T4, a 7-to-8-billion model in 4-bit is the sweet spot, and a 1-to-3 "
    "billion model is effortless. The cell lists a few trending text-generation models to get you "
    "started, but browsing the site yourself is the point."
)
code(
    r'''# List a few popular text-generation models to browse (or just visit huggingface.co/models)
try:
    from huggingface_hub import HfApi
    for m in HfApi().list_models(filter="text-generation", sort="downloads",
                                 direction=-1, limit=12):
        print(m.id)
except Exception as e:
    print("Browse huggingface.co/models directly. (Hub listing skipped:", e, ")")'''
)

# ---- 7: swap & compare -------------------------------------------------------
slide("\U0001F501 7 — Swap In Your Model & Compare", [
    "Pick one model from the Hub and load it the **same way**",
    "Run the **same prompt** on both; compare quality, speed, size",
    "Time the generation — tokens per second tells the speed story",
    "Bigger ≠ always better for a given task",
    "This is the comparison your assignment asks for",
])
script(
    "Now make it yours. Choose a model you found on the Hub — here we use Phi-3.5-mini as a smaller, "
    "faster contrast — and load it with the exact same code, just a different model id. Then run the "
    "same prompt through both and compare on three axes: answer quality, speed, and memory footprint. "
    "We time the generation so you can talk about tokens per second, not just vibes. You'll often find "
    "a smaller model is plenty for a given task and noticeably faster — which is the whole argument "
    "for picking the right tool rather than the biggest one. Capture what you observe; it goes "
    "straight into your comparison report and the forum discussion."
)
code(
    r'''import time

def load_pipe(model_id):
    bnb = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4",
                             bnb_4bit_compute_dtype=torch.float16)
    t = AutoTokenizer.from_pretrained(model_id)
    m = AutoModelForCausalLM.from_pretrained(model_id, quantization_config=bnb, device_map="auto")
    return t, m

def timed_chat(t, m, prompt, max_new_tokens=200):
    ids = t.apply_chat_template([{"role": "user", "content": prompt}],
                                add_generation_prompt=True, return_tensors="pt").to(m.device)
    start = time.time()
    out = m.generate(ids, max_new_tokens=max_new_tokens, do_sample=False)
    secs = time.time() - start
    n = out.shape[-1] - ids.shape[-1]
    text = t.decode(out[0][ids.shape[-1]:], skip_special_tokens=True)
    print(f"  {n} tokens in {secs:.1f}s  ->  {n/secs:.1f} tok/s")
    return text

# Your pick from the Hub (swap this id for the model YOU chose):
MY_PICK = "microsoft/Phi-3.5-mini-instruct"
t2, m2 = load_pipe(MY_PICK)

q = "Explain what a CVE is to a new analyst, in three sentences."
print("=== Qwen2.5-7B ==="); print(timed_chat(tok, model, q))
print("\n=== " + MY_PICK + " ==="); print(timed_chat(t2, m2, q))'''
)

# ---- 8: compare experiences --------------------------------------------------
slide("⚖️ 8 — Compare the Experiences", [
    "**Local CPU** — free, private, offline; small & slower",
    "**Colab T4** — capable models, free session; setup + time limits",
    "**Cloud API** — most capable, simplest; per-token cost + data leaves you",
    "Right tool depends on the task: privacy? cost? capability?",
    "→ Write this up in your lab report and the forum",
])
script(
    "Step back and compare the three experiences you just lived. Local on CPU was free, private, and "
    "offline, but limited to small models and slower answers. The Colab T4 let you host a capable "
    "seven-billion model for free during a session, at the cost of some setup and Colab's time limits. "
    "The cloud API was the most capable and the simplest code, but you pay per token and your data "
    "leaves your machine. There's no universal winner — for a privacy-sensitive log you might insist "
    "on local, for a quick capable answer you might reach for the API, and for class experiments the "
    "free Colab GPU is ideal. That judgment is what your comparison report and the forum post are "
    "really assessing."
)
code(
    r'''print("Decision guide:")
print("  Sensitive data, must stay private  -> local model")
print("  Need maximum capability, fast        -> cloud API (watch token cost)")
print("  Free experiments with capable models -> Colab GPU")
print("\nYou ran all three. Now write up which you'd pick for which task.")'''
)

# ---- summary -----------------------------------------------------------------
slide("✅ Summary & Key Takeaways", [
    "You ran an LLM **three ways**: API, local CPU, Colab T4 GPU",
    "You hosted a **capable** open model on a free GPU with 4-bit quantization",
    "You learned to **shop the Hugging Face Hub** (size, license, gated)",
    "You **swapped models and compared** speed, quality, and cost",
    "Trade-offs — cost, privacy, capability — drive the choice",
])
script(
    "In forty minutes you've done what used to take a research lab: run a capable language model on a "
    "free GPU, run a private one on your own machine, and compare both to a hosted API. You also "
    "learned to navigate the Hugging Face Hub and read a model card for the three things that matter — "
    "size, license, and access. Carry forward the core lesson: there's no single best place to run an "
    "LLM; cost, privacy, and capability decide. In the next modules we'll take the model you can now "
    "host and put it to work — grounding it with RAG and driving it with agents."
)
code(
    r'''print("Module 3 complete. You can now:")
print("  - run an LLM via API, locally on CPU, and on a Colab GPU")
print("  - host a capable open model on a T4 with 4-bit quantization")
print("  - choose a model from Hugging Face and compare it to others")
print("\nNext: ground these models with retrieval (RAG) and drive them with agents.")'''
)

# ---------------------------------------------------------------------------
nb = {
    "nbformat": 4, "nbformat_minor": 5,
    "metadata": {"kernelspec": {"name": "python3", "display_name": "Python 3"},
                 "language_info": {"name": "python"},
                 "accelerator": "GPU", "colab": {"provenance": [], "gpuType": "T4"}},
    "cells": cells,
}
with open("host_LLM_GPU.ipynb", "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)
print(f"Wrote host_LLM_GPU.ipynb with {len(cells)} cells.")
