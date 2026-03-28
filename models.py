from pydantic import BaseModel
from typing import Optional, Dict, Any

class Action(BaseModel):
    command: str

class Observation(BaseModel):
    stdout: str
    stderr: str
    exit_code: int
    task_id: str
    reward: float
    done: bool
    info: Dict[str, Any] = {}

class State(BaseModel):
    task_id: str
    step_count: int
    done: bool
