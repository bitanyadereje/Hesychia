import os
import requests

def get_hf_response(prompt: str) -> str:
    api_key = os.getenv("HF_API_KEY")
    if not api_key:
        print("⚠️ HF_API_KEY not set.")
        return None
    
    model = "google/flan-t5-large"
    url = f"https://api-inference.huggingface.co/models/{model}"
    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {"inputs": prompt, "parameters": {"max_new_tokens": 200}}
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=20)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                return data[0].get("generated_text")
            elif isinstance(data, dict):
                return data.get("generated_text")
            return None
        else:
            print(f"⚠️ HF error: {response.status_code}")
            return None
    except Exception as e:
        print(f"⚠️ HF failed: {e}")
        return None