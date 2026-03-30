from fastapi import FastAPI
from pydantic import BaseModel

from models import SecureCodeAction
from server.environment import SecureCodeEnvironment

app = FastAPI(title="Secure Code Reviewer")

env = SecureCodeEnvironment()


class GraderRequest(BaseModel):
    patched_code: str


def _model_to_dict(obj):
    """
    Pydantic v1/v2 compatible conversion.
    """
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    return obj.dict()


@app.get("/")
def home():
    return {"status": "running", "message": "Secure Code Reviewer is live"}


# =========================
# RESET ENDPOINT
# =========================
@app.post("/reset")
def reset(difficulty: str = "easy"):
    obs = env.reset(difficulty)
    return _model_to_dict(obs)


# =========================
# STEP ENDPOINT
# =========================
@app.post("/step")
def step(action: SecureCodeAction):
    obs, reward, done = env.step(action)
    return {
        "observation": _model_to_dict(obs),
        "reward": reward,
        "done": done,
    }


# =========================
# STATE ENDPOINT
# =========================
@app.get("/state")
def get_state():
    return _model_to_dict(env.state)


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
def grader(payload: GraderRequest):
    reward = env._grade(payload.patched_code)
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
            patched_code = (
                'query = "SELECT * FROM users WHERE name = %s"\n'
                "cursor.execute(query, (username,))"
            )

        elif obs.vulnerability_type == "insecure_deserialization":
            patched_code = "import json\ndata = json.load(file)"

        else:
            patched_code = obs.vulnerable_code

        _, reward, _ = env.step(
            SecureCodeAction(patched_code=patched_code)
        )

        results[difficulty] = reward

    return results


def main():
    import uvicorn

    uvicorn.run("server.app:app", host="0.0.0.0", port=8000, reload=False)


if __name__ == "__main__":
    main()