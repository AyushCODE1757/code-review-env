from typing import List, Dict, Any


class RewardCalculator:
    """
    Calculates rewards based on agent actions and ground truth bugs.
    """

    # Reward constants
    CORRECT_BUG_FOUND = 1.0
    WRONG_BUG_FLAGGED = -0.3
    MISSED_BUG_PENALTY = -0.5
    CORRECT_FIX_BONUS = 0.5
    APPROVE_CLEAN_CODE = 0.5
    FALSE_POSITIVE_PENALTY = -0.4
    STEP_PENALTY = -0.01       # Small penalty per step to encourage efficiency

    def __init__(self, ground_truth_bugs: List[Dict[str, Any]]):
        """
        Args:
            ground_truth_bugs: List of known bugs in the task, each a dict with
                               keys: 'line', 'type', 'description'
        """
        self.ground_truth_bugs = ground_truth_bugs
        self.found_bug_indices: set = set()

    def calculate(self, action: Any, step: int) -> float:
        """
        Calculate the reward for a given action.

        Args:
            action: The Action object taken by the agent.
            step: Current step number.

        Returns:
            float: The computed reward.
        """
        reward = self.STEP_PENALTY  # baseline step cost

        if action.action_type == "identify_bug":
            matched = self._match_bug(action.line_number, action.bug_description)
            if matched is not None:
                reward += self.CORRECT_BUG_FOUND
                self.found_bug_indices.add(matched)
                if action.suggested_fix:
                    reward += self.CORRECT_FIX_BONUS
            else:
                reward += self.WRONG_BUG_FLAGGED

        elif action.action_type == "approve":
            if len(self.ground_truth_bugs) == 0:
                reward += self.APPROVE_CLEAN_CODE
            else:
                reward += self.FALSE_POSITIVE_PENALTY

        elif action.action_type == "request_changes":
            # Neutral — agent is escalating but not identifying specifics
            reward += 0.0

        return round(reward, 4)

    def final_penalty(self) -> float:
        """Penalize for any bugs that were never found."""
        missed = len(self.ground_truth_bugs) - len(self.found_bug_indices)
        return missed * self.MISSED_BUG_PENALTY

    def _match_bug(self, line: int, description: str) -> int | None:
        """
        Match an agent's identified bug against ground truth.

        Returns:
            Index of the matched bug, or None if no match.
        """
        if line is None:
            return None
        for i, bug in enumerate(self.ground_truth_bugs):
            if i in self.found_bug_indices:
                continue
            if abs(bug.get("line", -999) - line) <= 2:
                return i
        return None

    def reset(self):
        """Reset internal state for a new episode."""
        self.found_bug_indices = set()
