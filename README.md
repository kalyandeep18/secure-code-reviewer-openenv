---
title: Secure Code Reviewer
emoji: 🔐
colorFrom: blue
colorTo: green
sdk: docker
app_port: 8000
pinned: false
---







# 🔐 Secure Code Reviewer (OpenEnv Environment)

An OpenEnv-based environment designed to train and evaluate AI agents on **real-world security vulnerabilities in code**.

---

## 🚀 Overview

Modern AI-generated code often introduces security risks. This project simulates a **real-world code review environment** where an AI agent must detect and fix vulnerabilities.

The environment follows the **OpenEnv standard**, enabling structured interaction via `reset()`, `step()`, and `state()`.

---

## 🧠 Key Idea

We built a **hybrid AI system**:

* 🧩 Rule-based fixes → ensure correctness & reproducibility
* 🤖 LLM support → enables future scalability
* 📊 Deterministic grading → consistent evaluation

---

## 🧩 Tasks (Difficulty Levels)

### 🟢 Easy — Hardcoded Secrets

```python
api_key = "12345SECRET"
```

Fix: Use environment variables (`os.getenv`)

---

### 🟡 Medium — SQL Injection

```python
query = f"SELECT * FROM users WHERE name = '{username}'"
```

Fix: Use parameterized queries

---

### 🔴 Hard — Insecure Deserialization

```python
import pickle
data = pickle.load(file)
```

Fix: Replace with safe methods (`json.load`)

---

## ⚙️ Environment Design

### 🔹 Action

```python
patched_code: str
```

### 🔹 Observation

```python
vulnerable_code: str
vulnerability_type: str
test_cases: list
context: dict
```

### 🔹 State

```python
task_id: str
difficulty: str
attempt_count: int
```

---

## 🎯 Reward Function

| Scenario         | Reward |
| ---------------- | ------ |
| Correct fix      | +1.0   |
| Partial fix      | +0.5   |
| No fix           | 0.0    |
| Broken / invalid | -0.5   |
| Infinite loop    | -1.0   |

---

## 🔌 API Endpoints

| Endpoint    | Description        |
| ----------- | ------------------ |
| `/reset`    | Start new task     |
| `/step`     | Submit patch       |
| `/state`    | Get current state  |
| `/tasks`    | List tasks         |
| `/grader`   | Evaluate patch     |
| `/baseline` | Run baseline agent |

---

## 🤖 Baseline Agent

A deterministic baseline agent achieves:

```json
{
  "easy": 1.0,
  "medium": 1.0,
  "hard": 1.0
}
```

This ensures:

* ✅ Reproducibility
* ✅ Stability
* ✅ Strong evaluation benchmark

---

## 🐳 Running Locally

### 1. Clone repo

```bash
git clone https://github.com/kalyandeep18/secure-code-reviewer-openenv.git
cd secure-code-reviewer-openenv
```

### 2. Run server

```bash
uvicorn server.app:app --reload
```

### 3. Open API docs

```
http://localhost:8000/docs
```

---

## 🐳 Docker Setup

```bash
docker build -t secure-env -f server/Dockerfile .
docker run -p 8000:8000 secure-env
```

---

## ☁️ Deployment

Deployed using **Hugging Face Spaces (Docker SDK)**.

---

## 🧠 Why This Matters

* Simulates real-world security workflows
* Helps train safer AI coding agents
* Provides deterministic evaluation for RL systems

---

## 🚀 Future Improvements

* AST-based grading
* Static analysis integration (Bandit, Semgrep)
* Multi-step agent interactions
* More vulnerability types

---

## 👨‍💻 Author

Created and Developed by Kalyan as part of the **Meta x PyTorch OpenEnv Hackathon**

---
