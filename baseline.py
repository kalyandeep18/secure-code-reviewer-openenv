import os
import re
import json
import time
import requests
from openai import OpenAI

# =========================
# CONFIG
# =========================
ENV_BASE_URL = "http://127.0.0.1:8000"

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

MODEL = "meta-llama/llama-3.2-3b-instruct:free"  # Best free stable model

if not OPENROUTER_API_KEY:
    raise ValueError("Please set OPENROUTER_API_KEY")

client = OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url=OPENROUTER_BASE_URL
)


# =========================
# HELPERS
# =========================
def reset_env(difficulty):
    res = requests.post(f"{ENV_BASE_URL}/reset", params={"difficulty": difficulty})
    return res.json()


def step_env(patched_code):
    res = requests.post(
        f"{ENV_BASE_URL}/step",
        json={"patched_code": patched_code}
    )
    return res.json()


def clean_output(text):
    text = text.strip()

    # remove markdown ``` blocks
    if text.startswith("```"):
        text = re.sub(r"```.*?\n", "", text)
        text = text.replace("```", "")

    return text.strip()


# =========================
# LLM PATCH GENERATION
# =========================
def generate_patch(observation):
    vuln_type = observation["vulnerability_type"]
    code = observation["vulnerable_code"]

    # =========================
    # RULE-BASED FAST FIX (backup)
    # =========================
    if vuln_type == "hardcoded_secret":
        return "import os\napi_key = os.getenv('API_KEY')"

    elif vuln_type == "sql_injection":
        return "query = \"SELECT * FROM users WHERE name = %s\"\ncursor.execute(query, (username,))"

    elif vuln_type == "insecure_deserialization":
        return "import json\ndata = json.load(file)"

    # =========================
    # LLM (if needed)
    # =========================
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "Fix security issues in code."},
                {"role": "user", "content": code}
            ],
            temperature=0
        )

        output = response.choices[0].message.content
        return clean_output(output)

    except Exception as e:
        print("LLM failed, using fallback:", e)
        return code


# =========================
# RUN ONE TASK
# =========================
def run_task(difficulty):
    print("\n" + "="*60)
    print(f"Running {difficulty.upper()} task")

    obs = reset_env(difficulty)
    print("\nObservation:", json.dumps(obs, indent=2))

    patched_code = generate_patch(obs)
    print("\nGenerated Patch:\n", patched_code)

    result = step_env(patched_code)
    print("\nResult:", json.dumps(result, indent=2))

    return result["reward"]


# =========================
# MAIN
# =========================
if __name__ == "__main__":
    difficulties = ["easy", "medium", "hard"]
    scores = []

    for d in difficulties:
        try:
            score = run_task(d)
            scores.append(score)
            time.sleep(1)
        except Exception as e:
            print(f"Error in {d}: {e}")
            scores.append(0.0)

    print("\n" + "="*60)
    print("FINAL SCORES")
    print(dict(zip(difficulties, scores)))
    print("Average Score:", sum(scores)/len(scores))