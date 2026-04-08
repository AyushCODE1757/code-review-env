from dataclasses import dataclass, field
from typing import Dict, Any, List


@dataclass
class GradeResult:
    task_id: str
    difficulty: str

    score: float                 # 0–1
    total_reward: float

    bugs_found: int
    bugs_missed: int
    false_positives: int

    steps_taken: int
    approved: bool

    feedback: List[str] = field(default_factory=list)


class Grader:
    WEIGHTS = {
        "bug_detection": 0.4,
        "false_positive": 0.2,
        "efficiency": 0.2,
        "decision_quality": 0.2
    }

    difficulty_weight = {
        "easy": 1.0,
        "medium": 0.9,
        "hard": 0.8
    }

    def __init__(self, max_steps=10):
        self.max_steps = max_steps

    def grade(
        self,
        task: Dict[str, Any],
        bugs_found: List[Dict[str, Any]],
        steps_taken: int,
        total_reward: float,
        final_action: str,
    ) -> GradeResult:

        ground_truth = task.get("bugs", [])
        total_bugs = len(ground_truth)

        # ✅ PURE LINE-BASED MATCHING (robust)
        true_lines = {int(b["line"]) for b in ground_truth}
        found_lines = {int(b["line"]) for b in bugs_found}

        correct = len(true_lines & found_lines)
        false_positives = len(found_lines - true_lines)
        missed = len(true_lines - found_lines)

        # ── Sub-scores ──
        bug_detection_score = correct / total_bugs if total_bugs > 0 else 1.0

        false_positive_score = max(0.0, 1.0 - (false_positives * 0.2))

        efficiency_score = max(0.0, 1.0 - (steps_taken / self.max_steps))

        # ── Decision logic ──
        if total_bugs == 0:
            decision_score = 1.0 if final_action == "approve" else 0.0
        else:
            if correct == total_bugs:
                decision_score = 1.0 if final_action == "approve" else 0.0
            else:
                decision_score = 0.0

        # ── Final score ──
        composite = (
            self.WEIGHTS["bug_detection"] * bug_detection_score
            + self.WEIGHTS["false_positive"] * false_positive_score
            + self.WEIGHTS["efficiency"] * efficiency_score
            + self.WEIGHTS["decision_quality"] * decision_score
        )

        # difficulty scaling
        weight = self.difficulty_weight.get(task.get("difficulty", "easy"), 1.0)
        final_score = round(composite * weight, 2)

        return GradeResult(
            task_id=task.get("task_id", task.get("taskid", "unknown")),
            difficulty=task.get("difficulty", "unknown"),
            total_reward=round(total_reward, 4),

            bugs_found=correct,
            bugs_missed=missed,
            false_positives=false_positives,

            steps_taken=steps_taken,
            approved=(final_action == "approve" and correct == total_bugs),

            score=final_score,
            feedback=[]
        )