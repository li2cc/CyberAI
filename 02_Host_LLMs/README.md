# Hosting LLMs: Local & GPU

A short module for the *Applied AI for Cybersecurity* course covering **Module 3 — LLMs on Local
and Cloud**. It shows how to run an open-source large language model **locally on a GPU** (instead
of calling a cloud API), using the same security task as the intro module — classifying a
suspicious-login alert — so students can compare local vs. cloud trade-offs directly.

The module contrasts with [Introduction_to_AI](../01_Introduction_to_AI/), which sends the same alert
to **cloud** models (OpenAI and Claude). Here the model runs on your own hardware.

## Contents

- **[host_LLM_GPU.ipynb](host_LLM_GPU.ipynb)** — notebook version: load a small open-source model
  with Hugging Face `transformers` and run a security-alert classification on a GPU.
- **[host_local_LLM_GPU.py](host_local_LLM_GPU.py)** — the same as a plain script.

Both use a compact instruct model (`TinyLlama/TinyLlama-1.1B-Chat-v1.0`, with
`microsoft/Phi-3-mini-4k-instruct` as a commented alternative) via the `text-generation` pipeline.

## Topics

- Cloud LLMs vs. local LLMs vs. Colab-based experimentation
- Loading open-source models with Hugging Face `transformers` (`pipeline`)
- Running inference on a GPU (`device=0`) and `max_new_tokens`
- Capability, privacy, latency, and cost trade-offs between hosting modes
- A security use case: benign-vs-suspicious alert classification

## Setup

A CUDA-capable GPU is recommended (Google Colab with a GPU runtime works well). Install the
dependencies:

```bash
pip install transformers accelerate torch bitsandbytes
```

Then run the script:

```bash
python host_local_LLM_GPU.py
```

…or open `host_LLM_GPU.ipynb` in Jupyter / VS Code / Colab and run the cells top to bottom. The
first run downloads the model weights (~1 GB for TinyLlama) and caches them.

## How it works

1. Build a Hugging Face `text-generation` pipeline around a small instruct model on the GPU.
2. Wrap a sample security alert in a classification prompt.
3. Generate and print the model's benign/suspicious verdict and one-sentence rationale.

Swap the `model=` line to try a larger model (e.g. Phi-3) and observe the capability/latency
trade-off on your hardware.

## Notes & safety

Local models keep data on your machine (a privacy win for sensitive logs) but trade away the
capability of frontier cloud models. As always, validate model output — small local models
hallucinate more — and keep any cloud API keys in the repository-root `.env`, never in code.
