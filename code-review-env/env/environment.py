from typing import Optional, Dict, Any, List
from .models import Action, Observation, Bug  
from tasks import get_task
from .utils import number_lines, truncate_code


class CodeReviewEnv:

    _done: bool = False
    total_reward: float = 0.0

    def reset(self, difficulty="easy") -> Observation:
        self.difficulty = difficulty

        if difficulty == "easy":
            self.MAX_STEPS = 5
        elif difficulty == "medium":
            self.MAX_STEPS = 10
        elif difficulty == "hard":
            self.MAX_STEPS = 15

        task = get_task(difficulty)

        self.state = {
            "code": task["code"],
            "true_bugs": task["bugs"],  # FIXED
            "found_bugs": [],
            "applied_fixes": [],
            "steps_taken": 0,           # FIXED
            "max_steps": self.MAX_STEPS # FIXED
        }

        return self._build_observation()

    def step(self, action_dict):
        action = Action(**action_dict)

        reward = 0.0
        done = False
        info = {}

        if action.type == "flag_bug":
            reward, info = self._handle_flag_bug(action)

        elif action.type == "suggest_fix":
            reward, info = self._handle_suggest_fix(action)

        elif action.type == "approve":
            reward, done, info = self._handle_approve()

        else:
            reward = -1.0
            info["error"] = "Invalid action type"

        reward -= 0.05

        self.state["steps_taken"] += 1  # FIXED

        if self.state["steps_taken"] >= self.state["max_steps"]:  # FIXED
            done = True

        self.total_reward += reward      # FIXED
        self._done = done               # FIXED

        return self._build_observation(), reward, done, info

    def _build_observation(self) -> Observation:
        fixed_lines = [f["line"] for f in self.state["applied_fixes"]]  # FIXED

        return Observation(
            code=self.state["code"],
            found_bugs=self.state["found_bugs"],
            fixed_lines=fixed_lines,  # FIXED
            steps_remaining=self.state["max_steps"] - self.state["steps_taken"],  # FIXED
        )

    def _handle_flag_bug(self, action):
        line = action.line

        true_bug = next((b for b in self.state["true_bugs"] if b["line"] == line), None)

        if true_bug and line not in [b["line"] for b in self.state["found_bugs"]]:
            self.state["found_bugs"].append({
                "line": line,
                "description": action.description
            })
            return 1.0, {"message": "Correct bug found"}

        if true_bug:
            return -0.2, {"message": "Duplicate bug"}

        return -0.5, {"message": "No bug on this line"}

    def _handle_suggest_fix(self, action):
        line = action.line

        true_bug = next((b for b in self.state["true_bugs"] if b["line"] == line), None)

        if not true_bug:
            return -0.5, {"message": "No bug to fix"}

        if line not in [b["line"] for b in self.state["found_bugs"]]:
            return -0.5, {"message": "Fix before flagging"}

        if line in [f["line"] for f in self.state["applied_fixes"]]:  # FIXED
            return -0.2, {"message": "Duplicate fix"}

        self.state["applied_fixes"].append({   # FIXED
            "line": line,
            "fix": action.description
        })

        return 0.5, {"message": "Fix accepted"}

    def _handle_approve(self):
        total = len(self.state["true_bugs"])
        found = len(self.state["found_bugs"])

        if found == total:
            return 1.0, True, {"message": "All bugs found. Approved."}
        else:
            return -1.0, True, {"message": "Approved too early"}

    @property
    def is_done(self) -> bool:
        return self._done
