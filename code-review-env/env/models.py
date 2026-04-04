from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum


class ActionType(str, Enum):
    COMMENT = "comment"           # Leave a review comment on a line
    APPROVE = "approve"           # Approve the code
    REQUEST_CHANGES = "request_changes"  # Request changes
    IDENTIFY_BUG = "identify_bug" # Identify a specific bug


class Action(BaseModel):
    """Represents an action taken by the agent during code review."""
    action_type: ActionType = Field(..., description="The type of action to perform")
    line_number: Optional[int] = Field(None, description="Target line number (for COMMENT/IDENTIFY_BUG)")
    comment: Optional[str] = Field(None, description="The review comment text")
    bug_description: Optional[str] = Field(None, description="Description of the identified bug")
    suggested_fix: Optional[str] = Field(None, description="Suggested code fix")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    class Config:
        use_enum_values = True


class Observation(BaseModel):
    """Represents the environment's response after an action."""
    code_snippet: str = Field(..., description="The current code under review")
    task_description: str = Field(..., description="Description of the review task")
    diff: Optional[str] = Field(None, description="Git-style diff of the code changes")
    language: str = Field(default="python", description="Programming language of the code")
    line_count: int = Field(..., description="Total number of lines in the code")
    bugs_found: List[str] = Field(default_factory=list, description="List of bugs found so far")
    step: int = Field(default=0, description="Current step number in the episode")
    done: bool = Field(default=False, description="Whether the episode is done")
    reward: float = Field(default=0.0, description="Reward from the last action")
    info: Dict[str, Any] = Field(default_factory=dict, description="Extra info from the environment")
