

!pip install transformers accelerate torch bitsandbytes


from transformers import pipeline

pipe = pipeline(
    "text-generation",
    #model="microsoft/Phi-3-mini-4k-instruct",
    model="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
    device=0
)

alert = "5 failed logins for 'admin' from 203.0.113.7 in 20s, then 1 success"

prompt = f"Classify benign/suspicious and explain in one sentence: {alert}"

result = pipe(prompt, max_new_tokens=200)[0]["generated_text"]
print(result)