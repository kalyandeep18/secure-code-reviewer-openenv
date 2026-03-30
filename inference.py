import os
import json
import time
import requests

ENV_BASE_URL = os.getenv("ENV_BASE_URL", "http://127.0.0.1:8000")


def reset_env(difficulty: str):
    res = requests.post(f"{ENV_BASE_URL}/reset", params={"difficulty": difficulty}, timeout=30)
    res.raise_for_status()
    return res.json()


def step_env(patched_code: str):
    res = requests.post(
        f"{ENV_BASE_URL}/step",
        json={"patched_code": patched_code},
        timeout=30,
    )
    res.raise_for_status()
    return res.json()


def solve(observation: dict) -> str:
    vuln_type = observation["vulnerability_type"]

    if vuln_type == "hardcoded_secret":
        return "import os\napi_key = os.getenv('API_KEY')"

    if vuln_type == "sql_injection":
        return 'query = "SELECT * FROM users WHERE name = %s"\ncursor.execute(query, (username,))'

    if vuln_type == "insecure_deserialization":
        return "import json\ndata = json.load(file)"

    return observation["vulnerable_code"]


def run_task(difficulty: str) -> float:
    obs = reset_env(difficulty)
    patched_code = solve(obs)
    result = step_env(patched_code)

    print("=" * 60)
    print(f"Difficulty: {difficulty}")
    print("Observation:", json.dumps(obs, indent=2))
    print("\nPatched code:\n", patched_code)
    print("\nResult:", json.dumps(result, indent=2))

    return float(result["reward"])


if __name__ == "__main__":
    difficulties = ["easy", "medium", "hard"]
    scores = []

    for difficulty in difficulties:
        try:
            scores.append(run_task(difficulty))
            time.sleep(1)
        except Exception as e:
            print(f"[ERROR] {difficulty}: {e}")
            scores.append(0.0)

    print("\nFINAL SCORES")
    print(dict(zip(difficulties, scores)))
    print("Average Score:", sum(scores) / len(scores))