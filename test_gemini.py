import requests
import streamlit as st
import json

api_key = st.secrets["GEMINI_API_KEY"]

print("API key loaded.")
print("Testing Gemini text generation with low thinking...")

url = (
    "https://generativelanguage.googleapis.com/"
    "v1beta/models/gemini-3.5-flash-lite:generateContent"
)

headers = {
    "x-goog-api-key": api_key,
    "Content-Type": "application/json"
}

payload = {
    "contents": [
        {
            "parts": [
                {
                    "text": "Reply with exactly: Gemini works."
                }
            ]
        }
    ],
    "generationConfig": {
        "thinkingConfig": {
            "thinkingLevel": "low"
        },
        "maxOutputTokens": 100
    }
}

try:
    response = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=60
    )

    print("HTTP status:", response.status_code)

    if response.status_code == 200:
        data = response.json()

        print("\nGemini API responded successfully.")
        print("Response received:")
        print(json.dumps(data, indent=2))

    else:
        print("\nGemini returned an error:")
        print(response.text[:2000])

except Exception as e:
    print("\nFAILED!")
    print(type(e).__name__)
    print(str(e))