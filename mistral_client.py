import os
import requests

def get_mistral_response(prompt: str) -> str:
    """
    Get a response from Mistral AI using the HTTP API (free tier).
    """
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        print("⚠️ MISTRAL_API_KEY not set in environment variables.")
        return None
    
    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "mistral-tiny",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,
        "max_tokens": 500
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        else:
            print(f"⚠️ Mistral API error: {response.status_code} - {response.text[:200]}")
            return None
    except Exception as e:
        print(f"⚠️ Mistral request failed: {e}")
        return None