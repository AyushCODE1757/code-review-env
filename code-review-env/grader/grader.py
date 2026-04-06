from typing import Dict, Any, List
from dataclasses import dataclass, field


@dataclass
class GradeResult:
    task_id: str
    difficulty: str
    total_reward: float
    bugs_found: int
    bugs_missed: int
    false_positives: int
    steps_taken: int
    approved: bool
    score: float  # 0.0 – 1.0 normalized score
    feedback: List[str] = field(default_factory=list)


class Grader:
    """
    Final scoring logic for a completed code review episode.

    Computes a normalized 0–100 score from episode outcomes and produces
    human-readable feedback for the agent.
    """

    WEIGHTS = {
        "bug_detection": 0.5,      # % of bugs correctly found
        "false_positive": 0.2,     # penalty for incorrectly flagged issues
        "efficiency": 0.2,         # fewer steps → higher score
        "decision_quality": 0.1,   # approve vs. request_changes appropriateness
    }

    def __init__(self, max_steps: int = 10):
        self.max_steps = max_steps

    def grade(
        self,
        task: Dict[str, Any],
        bugs_found: List[str],
        false_positives: int,
        steps_taken: int,
        total_reward: float,
        final_action: str,
    ) -> GradeResult:
        """
        Grade a completed episode.

        Args:
            task: The original task dict (must contain 'bugs', 'id', 'difficulty').
            bugs_found: List of bug descriptions the agent identified.
            false_positives: Number of incorrectly flagged issues.
            steps_taken: Number of steps the agent took.
            total_reward: Cumulative reward from the environment.
            final_action: The terminal action taken ('approve' or 'request_changes').

        Returns:
            GradeResult with detailed scoring breakdown.
        """
        ground_truth = task.get("bugs", [])
        total_bugs = len(ground_truth)
        bugs_correctly_found = min(len(bugs_found), total_bugs)
        bugs_missed = max(0, total_bugs - bugs_correctly_found)

        # --- Sub-scores ---
        bug_detection_score = (
            bugs_correctly_found / total_bugs if total_bugs > 0 else 1.0
        )
        false_positive_score = max(0.0, 1.0 - (false_positives * 0.2))
        efficiency_score = max(0.0, 1.0 - (steps_taken / self.max_steps))

        # Decision quality: approve is correct only if no bugs exist
        if total_bugs == 0:
            decision_score = 1.0 if final_action == "approve" else 0.5
        else:
            decision_score = 1.0 if final_action == "request_changes" else 0.0

        # --- Composite score ---
        composite = (
            self.WEIGHTS["bug_detection"] * bug_detection_score
            + self.WEIGHTS["false_positive"] * false_positive_score
            + self.WEIGHTS["efficiency"] * efficiency_score
            + self.WEIGHTS["decision_quality"] * decision_score
        )
        normalized_score = round(composite * 100, 2)

        # --- Feedback generation ---
        feedback = self._generate_feedback(
            bug_detection_score,
            false_positives,
            efficiency_score,
            decision_score,
            total_bugs,
            bugs_missed,
        )

        return GradeResult(
            task_id=task.get("taskid", task.get("id", "unknown")),
            difficulty=task.get("difficulty", "unknown"),
            total_reward=round(total_reward, 4),
            bugs_found=bugs_correctly_found,
            bugs_missed=bugs_missed,
            false_positives=false_positives,
            steps_taken=steps_taken,
            approved=(final_action == "approve"),
            score=normalized_score,
            feedback=feedback,
        )

    def _generate_feedback(
        self,
        bug_score: float,
        fp: int,
        eff_score: float,
        dec_score: float,
        total_bugs: int,
        missed: int,
    ) -> List[str]:
        msgs = []
        if bug_score == 1.0:
            msgs.append("✅ All bugs were correctly identified.")
        elif bug_score >= 0.5:
            msgs.append(f"⚠️  Partial bug detection: {missed} bug(s) were missed.")
        else:
            msgs.append(f"❌ Poor bug detection: {missed}/{total_bugs} bugs missed.")

        if fp == 0:
            msgs.append("✅ No false positives — precision is excellent.")
        else:
            msgs.append(f"⚠️  {fp} false positive(s) flagged incorrectly.")

        if eff_score >= 0.7:
            msgs.append("✅ Review completed efficiently.")
        else:
            msgs.append("⚠️  Review took too many steps. Aim to be more concise.")

        if dec_score == 1.0:
            msgs.append("✅ Final decision (approve/request_changes) was correct.")
        elif dec_score == 0.5:
            msgs.append("⚠️  Final decision was suboptimal for this scenario.")
        else:
            msgs.append("❌ Final decision was incorrect given the bugs present.")

        return msgs

    def summary(self, result: GradeResult) -> str:
        """Return a human-readable summary of the grade result."""
        lines = [
            f"{'='*50}",
            f"  GRADE REPORT — Task: {result.task_id} ({result.difficulty})",
            f"{'='*50}",
            f"  Score         : {result.score} / 100",
            f"  Total Reward  : {result.total_reward}",
            f"  Bugs Found    : {result.bugs_found}",
            f"  Bugs Missed   : {result.bugs_missed}",
            f"  False Positives: {result.false_positives}",
            f"  Steps Taken   : {result.steps_taken}",
            f"  Final Action  : {'Approved' if result.approved else 'Requested Changes'}",
            f"{'─'*50}",
            "  Feedback:",
        ]
        for msg in result.feedback:
            lines.append(f"    {msg}")
        lines.append(f"{'='*50}")
        return "\n".join(lines)
