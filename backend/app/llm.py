import os
import requests
from dotenv import load_dotenv

load_dotenv()

LLM_API_KEY = os.getenv("LLM_API_KEY")
MODEL_NAME = "gemini-2.0-flash"
LLM_API_URL = (
    f"https://generativelanguage.googleapis.com/v1/models/{MODEL_NAME}:generateContent?key={LLM_API_KEY}"
)

HEADERS = { "Content-Type": "application/json" }

SYSTEM_INSTRUCTIONS = """
You are an expert academic & professional writing assistant.

Write content that is:
- clear, structured, and well-organized
- suitable for students and professionals
- formal and polished
- includes examples and strong explanations
- avoids repetition and filler
"""


# -------------------------------------------------
#  CLEAN-UP FUNCTION (removes *, markdown, symbols)
# -------------------------------------------------
def clean_output(text: str) -> str:
    if not isinstance(text, str):
        return text

    # Remove asterisks
    text = text.replace("*", "")

    # Remove markdown headers
    text = text.replace("###", "")
    text = text.replace("##", "")
    text = text.replace("#", "")

    # Remove stray underscores
    text = text.replace("_", "")

    # Remove extra spaces
    return text.strip()


# -------------------------------------------------
#  CALL GEMINI FUNCTION
# -------------------------------------------------
def call_llm(prompt: str) -> str:
    full_user_prompt = SYSTEM_INSTRUCTIONS + "\n\nUSER REQUEST:\n" + prompt

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": full_user_prompt}]
            }
        ]
    }

    try:
        res = requests.post(LLM_API_URL, json=payload, headers=HEADERS)

        print("STATUS:", res.status_code)
        print("RAW:", res.text)

        res.raise_for_status()

        data = res.json()

        raw_text = data["candidates"][0]["content"]["parts"][0]["text"]

        # Clean the text before returning
        return clean_output(raw_text)

    except Exception as e:
        print("LLM ERROR:", e)
        return "AI generation failed."


# -------------------------------------------------
#  GENERATE SECTION CONTENT
# -------------------------------------------------
def generate_llm_content(section_title: str, topic: str) -> str:
    prompt = (
        f"Write a detailed, structured section titled '{section_title}' "
        f"based on this topic: {topic}. "
        f"Make it clear, formal, and highly readable."
    )
    return call_llm(prompt)


# -------------------------------------------------
#  REFINE SECTION CONTENT (FIXED BUG)
# -------------------------------------------------
def refine_llm_content(current_content: str, prompt: str) -> str:
    full_prompt = (
        f"Improve the following content.\n\n"
        f"INSTRUCTION: {prompt}\n\n"
        f"CONTENT:\n{current_content}"
    )
    return call_llm(full_prompt)
