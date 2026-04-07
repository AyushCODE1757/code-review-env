from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum


class ActionType(str, Enum):
    FLAG_BUG = "flag_bug"           
    SUGGEST_FIX = "suggest_fix"
    APPROVE = "approve"


class Action(BaseModel):
    type: ActionType
    line: Optional[int] = None
    description: Optional[str] = None

class Bug(BaseModel):
    line: int
    description: str


class Observation(BaseModel):
    code: str
    found_bugs: List[Bug]
    fixed_lines: List[int]
    steps_remaining: int