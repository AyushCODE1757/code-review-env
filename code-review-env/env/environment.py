from typing import Optional, Dict, Any, List
from .models import Action, Observation, Bug  
from tasks import get_task
from .utils import number_lines, truncate_code


class CodeReviewEnv:

    _done: bool = False
    total_reward: float = 0.0

    def reset(self, difficulty="easy", task=None):
    # --- SINGLE SOURCE OF TRUTH ---
        if task is not None:
            self.task = task
        else:
            self.task = get_task(difficulty)

        task = self.task  # always use this

        # --- MAX STEPS ---
        if difficulty == "easy":
            self.MAX_STEPS = 5
        elif difficulty == "medium":
            self.MAX_STEPS = 10
        elif difficulty == "hard":
            self.MAX_STEPS = 15

        # --- NORMALIZE TASK FORMAT ---
        if "bugs" not in task:
            task["bugs"] = [{
                "line": task.get("line"),
                "description": task.get("description", "")
            }]

        # --- DEBUG ---
       

        # --- STATE INIT ---
        self.state = {
            "code": task["code"],
            "true_bugs": [
                {
                    "line": int(b["line"]),  # ensure consistent type
                    "description": b.get("description", "")
                }
                for b in task["bugs"]
            ],
            "found_bugs": [],
            "applied_fixes": [],
            "steps_taken": 0,
            "max_steps": self.MAX_STEPS
        }

  

        return self._build_observation()

    def step(self, action_dict):
        action = Action(**action_dict)

        reward = 0.0
        done = False
        info = {}

        if action.type == "flag_bug":
            reward, info = self._handle_flag_bug(action)
            if len(self.state["found_bugs"]) == 1:
                reward +=0.3  # bonus for first bug found

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

        true_bug = next((b for b in self.state["true_bugs"] if int(b["line"]) == line), None)

        if true_bug and line not in [int(b["line"]) for b in self.state["found_bugs"]]:
            self.state["found_bugs"].append({
                "line": line,
                "description": action.description
            })
            return 1.0, {"message": "Correct bug found"}

        if true_bug:
            return -0.3, {"message": "Duplicate bug"}

        return -0.7, {"message": "No bug on this line"}

    def _handle_suggest_fix(self, action):
        line = action.line

        true_bug = next((b for b in self.state["true_bugs"] if int(b["line"]) == line), None)

        if not true_bug:
            return -0.7, {"message": "No bug to fix"}

        if line not in [int(b["line"]) for b in self.state["found_bugs"]]:
            return -0.7, {"message": "Fix before flagging"}

        if line in [f["line"] for f in self.state["applied_fixes"]]:  # FIXED
            return -0.3, {"message": "Duplicate fix"}

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
