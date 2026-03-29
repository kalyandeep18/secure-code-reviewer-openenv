from pydantic import BaseModel
from typing import List, Dict, Any, Optional


# =========================
# ACTION (Agent Output)
# =========================
class SecureCodeAction(BaseModel):
    patched_code: str
    fix_strategy: Optional[str] = None  # optional explanation


# =========================
# OBSERVATION (Agent Input)
# =========================
class SecureCodeObservation(BaseModel):
    vulnerable_code: str
    vulnerability_type: str
    test_cases: List[str]
    context: Dict[str, Any]


# =========================
# STATE (Internal Tracking)
# =========================
class SecureCodeState(BaseModel):
    task_id: str
    difficulty: str  # easy / medium / hard
    attempt_count: int = 0
    max_attempts: int = 3