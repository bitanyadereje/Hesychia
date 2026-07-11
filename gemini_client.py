import os
from google import genai

def get_gemini_response(prompt: str, model_name: str = "gemini-3.5-flash") -> str:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY is not set")
    
    client = genai.Client(api_key=api_key)
    
    try:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt
        )
        return response.text
    except Exception as e:
        print(f"⚠️ Gemini error ({model_name}): {e}")
        return None