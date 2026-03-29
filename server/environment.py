import json
import random
from typing import Tuple

from models import SecureCodeAction, SecureCodeObservation, SecureCodeState


class SecureCodeEnvironment:
    def __init__(self):
        with open("data/tasks.json", "r") as f:
            self.tasks = json.load(f)

        self.current_task = None
        self.state_data = None

    # =========================
    # RESET
    # =========================
    def reset(self, difficulty: str = "easy") -> SecureCodeObservation:
        filtered_tasks = [t for t in self.tasks if t["difficulty"] == difficulty]
        self.current_task = random.choice(filtered_tasks)

        self.state_data = SecureCodeState(
            task_id=self.current_task["id"],
            difficulty=difficulty,
            attempt_count=0
        )

        return SecureCodeObservation(
            vulnerable_code=self.current_task["vulnerable_code"],
            vulnerability_type=self.current_task["vulnerability_type"],
            test_cases=self.current_task["test_cases"],
            context=self.current_task["context"]
        )

    # =========================
    # STEP (CORE LOGIC)
    # =========================
    def step(self, action: SecureCodeAction) -> Tuple[SecureCodeObservation, float, bool]:
        self.state_data.attempt_count += 1
        patched_code = action.patched_code

        reward = self._grade(patched_code)
        done = reward == 1.0 or self.state_data.attempt_count >= self.state_data.max_attempts

        observation = SecureCodeObservation(
            vulnerable_code=self.current_task["vulnerable_code"],
            vulnerability_type=self.current_task["vulnerability_type"],
            test_cases=self.current_task["test_cases"],
            context=self.current_task["context"]
        )

        return observation, reward, done

    # =========================
    # STATE
    # =========================
    @property
    def state(self) -> SecureCodeState:
        return self.state_data

    # =========================
    # GRADER (IMPORTANT)
    # =========================
    def _grade(self, patched_code: str) -> float:
        vuln_type = self.current_task["vulnerability_type"]

        # EASY: Hardcoded secret
        if vuln_type == "hardcoded_secret":
            if "SECRET" not in patched_code and "os.getenv" in patched_code:
                return 1.0
            elif "SECRET" not in patched_code:
                return 0.5
            else:
                return 0.0

        # MEDIUM: SQL Injection
        elif vuln_type == "sql_injection":
            if "%s" in patched_code or "execute(" in patched_code:
                return 1.0
            elif "SELECT" in patched_code and "+" not in patched_code:
                return 0.5
            else:
                return 0.0

        # HARD: Insecure Deserialization
        elif vuln_type == "insecure_deserialization":
            if "pickle" not in patched_code and "json" in patched_code:
                return 1.0
            elif "pickle" not in patched_code:
                return 0.5
            else:
                return 0.0

        return 0.0