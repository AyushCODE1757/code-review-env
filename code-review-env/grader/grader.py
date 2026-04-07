from dataclasses import dataclass, field
from typing import Dict, Any
from typing import List
@dataclass
class GradeResult:
    task_id: str
    difficulty: str
    # Performance metrics
    score: float                 # 0–100
    total_reward: float
    # Bug stats
    bugs_found: int              # correctly found
    bugs_missed: int
    false_positives: int
    # Efficiency
    steps_taken: int
    # Final decision
    approved: bool
    # Optional feedback (keep but don’t overuse)
    feedback: List[str] = field(default_factory=list)
class Grader:
    WEIGHTS = {
        "bug_detection": 0.4,
        "false_positive": 0.2,
        "efficiency": 0.2,
        "decision_quality": 0.2
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
        true_lines = {b["line"] for b in ground_truth}
        found_lines = {b["line"] for b in bugs_found}

        correct = len(true_lines & found_lines)
        false_positives = len(found_lines - true_lines)
        missed = len(true_lines - found_lines)
        # Sub-scores 
        bug_detection_score = correct / total_bugs if total_bugs > 0 else 1.0
        false_positive_score = max(0.0, 1.0 - (false_positives * 0.2))
        efficiency_score = max(0.0, 1.0 - (steps_taken / self.max_steps))
        # Decision logic
        if total_bugs == 0:
            decision_score = 1.0 if final_action == "approve" else 0.0
        else:
        # bugs exist
            if correct == total_bugs:
                decision_score = 1.0 if final_action == "approve" else 0.0
            else:
                decision_score = 0.0
        #  Final score 
        composite = (
            self.WEIGHTS["bug_detection"] * bug_detection_score
            + self.WEIGHTS["false_positive"] * false_positive_score
            + self.WEIGHTS["efficiency"] * efficiency_score
            + self.WEIGHTS["decision_quality"] * decision_score
        )

        normalized_score = round(composite * 100, 2)

        return GradeResult(
            task_id=task.get("task_id", "unknown"),
            difficulty=task.get("difficulty", "unknown"),
            total_reward=round(total_reward, 4),
            bugs_found=correct,
            bugs_missed=missed,
            false_positives=false_positives,
            steps_taken=steps_taken,
            approved=(final_action == "approve"),
            score=normalized_score,
            feedback=[]
        )