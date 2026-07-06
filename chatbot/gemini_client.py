from google import genai
from dotenv import load_dotenv
import os
import time

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

client = None

if API_KEY:
    try:
        client = genai.Client(api_key=API_KEY)
    except Exception:
        client = None

ACTIVE_MODEL = "gemini-2.5-flash"


def generate(prompt):

    if client is None:
        return "CyberSafe AI is currently unavailable."

    for _ in range(2):
        try:
            response = client.models.generate_content(
                model=ACTIVE_MODEL,
                contents=prompt,
                config={
                    "temperature": 0.3,
                    "top_p": 0.8,
                }
            )

            return response.text

        except Exception as e:

            error = str(e)

            if "429" in error:
                time.sleep(5)
                continue

            raise e

    return "CyberSafe AI is temporarily busy. Please try again in a few moments."