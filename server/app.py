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
    from baseline import run_task

    results = {}
    for d in ["easy", "medium", "hard"]:
        results[d] = run_task(d)

    return results