from fastapi import FastAPI
from models import SecureCodeAction
from server.environment import SecureCodeEnvironment

app = FastAPI()

env = SecureCodeEnvironment()


# =========================
# RESET ENDPOINT
# =========================
@app.post("/reset")
def reset(difficulty: str = "easy"):
    obs = env.reset(difficulty)
    return obs.dict()


# =========================
# STEP ENDPOINT
# =========================
@app.post("/step")
def step(action: SecureCodeAction):
    obs, reward, done = env.step(action)
    return {
        "observation": obs.dict(),
        "reward": reward,
        "done": done
    }


# =========================
# STATE ENDPOINT
# =========================
@app.get("/state")
def get_state():
    return env.state.dict()

# =========================
# TASKS ENDPOINT
# =========================
@app.get("/tasks")
def get_tasks():
    return {"tasks": env.tasks}


# =========================
# GRADER ENDPOINT
# =========================
@app.post("/grader")
def grader(patched_code: str):
    reward = env._grade(patched_code)
    return {"reward": reward}


# =========================
# BASELINE ENDPOINT
# =========================
@app.get("/baseline")
def run_baseline():
    results = {}

    for difficulty in ["easy", "medium", "hard"]:
        obs = env.reset(difficulty)

        if obs.vulnerability_type == "hardcoded_secret":
            patched_code = "import os\napi_key = os.getenv('API_KEY')"

        elif obs.vulnerability_type == "sql_injection":
            patched_code = "query = \"SELECT * FROM users WHERE name = %s\"\ncursor.execute(query, (username,))"

        elif obs.vulnerability_type == "insecure_deserialization":
            patched_code = "import json\ndata = json.load(file)"

        else:
            patched_code = obs.vulnerable_code

        _, reward, _ = env.step(
            SecureCodeAction(patched_code=patched_code)
        )

        results[difficulty] = reward

    return results
