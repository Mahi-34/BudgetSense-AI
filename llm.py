import time
import requests
import streamlit as st


GEMINI_MODEL = "gemini-3.5-flash-lite"

GEMINI_URL = (
    f"https://generativelanguage.googleapis.com/"
    f"v1beta/models/{GEMINI_MODEL}:generateContent"
)


def generate_variance_commentary(
    department,
    line_item,
    line_type,
    budget,
    actual,
    variance,
    variance_pct,
    status,
    analyst_note=""
):
    """
    Generate concise AI commentary for one material variance.

    Python calculates the financial figures.
    Gemini only converts verified figures and analyst notes
    into management commentary.
    """

    api_key = st.secrets["GEMINI_API_KEY"]

    if analyst_note and analyst_note.strip():
        driver_text = analyst_note.strip()
    else:
        driver_text = (
            "Driver not provided — analyst input required."
        )

    prompt = f"""
You are a financial analyst writing management commentary.

Use ONLY the verified information provided below.
Do NOT invent causes, facts, numbers, percentages, or recommendations.

VERIFIED FINANCIAL INFORMATION

Department: {department}
Line item: {line_item}
Line type: {line_type}
Budget: ₹{budget:,.0f}
Actual: ₹{actual:,.0f}
Variance: ₹{variance:,.0f}
Variance percentage: {variance_pct:.2f}%
Status: {status}

ANALYST-PROVIDED DRIVER

{driver_text}

TASK

Write exactly 2 concise sentences.

Sentence 1 MUST state:
- actual amount
- budget amount
- variance amount
- variance percentage

Sentence 2 MUST:
- explain the driver only if an analyst-provided driver exists;
- otherwise say that the driver requires analyst input.

RULES:
- Copy all financial figures exactly as provided.
- Do not recalculate anything.
- Do not invent a reason.
- Do not introduce additional numbers.
- Do not use headings or bullet points.
- Return ONLY the two sentences.
"""

    headers = {
        "x-goog-api-key": api_key,
        "Content-Type": "application/json"
    }

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ],
        "generationConfig": {
            "thinkingConfig": {
                "thinkingLevel": "minimal"
            },
            "maxOutputTokens": 1000
        }
    }

    last_error = None

    for attempt in range(3):

        try:

            response = requests.post(
                GEMINI_URL,
                headers=headers,
                json=payload,
                timeout=45
            )

            if response.status_code == 200:

                data = response.json()

                candidates = data.get("candidates", [])

                if not candidates:
                    raise RuntimeError(
                        "Gemini returned no candidates."
                    )

                candidate = candidates[0]

                finish_reason = candidate.get(
                    "finishReason",
                    ""
                )

                content = candidate.get("content", {})
                parts = content.get("parts", [])

                commentary = ""

                for part in parts:
                    if "text" in part:
                        commentary += part["text"]

                commentary = commentary.strip()

                # Do not accept truncated responses.
                if finish_reason == "MAX_TOKENS":
                    last_error = RuntimeError(
                        "Gemini response was truncated."
                    )

                    if attempt < 2:
                        time.sleep(2)
                        continue

                    raise last_error

                if not commentary:
                    last_error = RuntimeError(
                        "Gemini returned empty commentary."
                    )

                    if attempt < 2:
                        time.sleep(2)
                        continue

                    raise last_error

                return commentary

            last_error = RuntimeError(
                f"Gemini API error {response.status_code}: "
                f"{response.text[:500]}"
            )

            if response.status_code in [
                429, 500, 502, 503, 504
            ]:
                if attempt < 2:
                    time.sleep(2)
                    continue

            raise last_error

        except requests.exceptions.Timeout as e:

            last_error = e

            if attempt < 2:
                time.sleep(2)
                continue

            raise RuntimeError(
                "Gemini request timed out after "
                "three attempts. Please try again."
            ) from e

        except requests.exceptions.RequestException as e:

            raise RuntimeError(
                f"Could not connect to Gemini: {e}"
            ) from e

    raise RuntimeError(
        "Gemini commentary generation failed."
    )