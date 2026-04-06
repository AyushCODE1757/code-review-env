from typing import Optional, Dict, Any, List
from .models import Action, Observation
from .rewards import RewardCalculator
from .utils import number_lines, truncate_code


class CodeReviewEnv:
    """
    Core reinforcement learning environment for LLM-based code review.

    The agent receives code and iteratively takes review actions (comment,
    identify_bug, approve, request_changes) until it finalizes a review or
    reaches the maximum number of steps.
    """

    MAX_STEPS = 10

    def __init__(self, task: Dict[str, Any]):
        """
        Args:
            task: A task dictionary with keys:
                - 'code': str — The code to review
                - 'description': str — Task description / instructions
                - 'bugs': List[Dict] — Ground truth bugs
                - 'language': str — Programming language (default 'python')
        """
        self.task = task
        self.code: str = task.get("code", "")
        self.description: str = "Review the provided code and identify bugs."
        self.ground_truth_bugs: List[Dict[str, Any]] = [
            {
                "line": task.get("line"),
                "type": task.get("type"),
                "description": task.get("description")
            }
        ] if "type" in task else task.get("bugs", [])
        self.language: str = task.get("language", "python")

        self.reward_calc = RewardCalculator(self.ground_truth_bugs)
        self._step = 0
        self._done = False
        self._bugs_found: List[str] = []
        self._total_reward: float = 0.0

    def reset(self) -> Observation:
        """Reset the environment to its initial state and return the first observation."""
        self._step = 0
        self._done = False
        self._bugs_found = []
        self._total_reward = 0.0
        self.reward_calc.reset()
        return self._build_observation(reward=0.0)

    def step(self, action: Action) -> Observation:
        """
        Apply an action to the environment.

        Args:
            action: The Action taken by the agent.

        Returns:
            Observation: The next observation.
        """
        if self._done:
            raise RuntimeError("Episode is done. Call reset() to start a new episode.")

        reward = self.reward_calc.calculate(action, self._step)

        # Track identified bugs for observation
        if action.action_type == "identify_bug" and action.bug_description:
            self._bugs_found.append(action.bug_description)

        self._step += 1
        self._total_reward += reward

        # Terminal condition: agent approves/requests_changes OR max steps reached
        terminal_actions = {"approve", "request_changes"}
        if action.action_type in terminal_actions or self._step >= self.MAX_STEPS:
            reward += self.reward_calc.final_penalty()
            self._total_reward += self.reward_calc.final_penalty()
            self._done = True

        obs = self._build_observation(reward=reward)
        return obs

    def _build_observation(self, reward: float) -> Observation:
        """Construct an Observation from current environment state."""
        code_display = truncate_code(number_lines(self.code))
        return Observation(
            code_snippet=code_display,
            task_description=self.description,
            language=self.language,
            line_count=len(self.code.splitlines()),
            bugs_found=list(self._bugs_found),
            step=self._step,
            done=self._done,
            reward=round(reward, 4),
            info={
                "total_reward": round(self._total_reward, 4),
                "max_steps": self.MAX_STEPS,
                "ground_truth_bug_count": len(self.ground_truth_bugs),
            },
        )

    @property
    def is_done(self) -> bool:
        return self._done

    @property
    def total_reward(self) -> float:
        return self._total_reward
