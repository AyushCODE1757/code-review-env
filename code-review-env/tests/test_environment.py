"""
Tests for env/environment.py — CodeReviewEnv
"""
import pytest
from unittest.mock import MagicMock, patch
from env.models import Action, ActionType, Observation
from env.environment import CodeReviewEnv


# ─── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture
def clean_task():
    """A task with no bugs — clean code."""
    return {
        "id": "test_clean",
        "difficulty": "easy",
        "language": "python",
        "description": "Review this clean code.",
        "code": "def add(a, b):\n    return a + b\n",
        "bugs": [],
    }

@pytest.fixture
def buggy_task():
    """A task with one known bug."""
    return {
        "id": "test_buggy",
        "difficulty": "easy",
        "language": "python",
        "description": "Review this code for bugs.",
        "code": "def add(a, b)\n    return a + b\n",
        "bugs": [
            {"line": 1, "type": "syntax_error", "description": "Missing colon."}
        ],
    }

@pytest.fixture
def multi_bug_task():
    """A task with multiple bugs."""
    return {
        "id": "test_multi",
        "difficulty": "medium",
        "language": "python",
        "description": "Review this code.",
        "code": "def foo():\n    x = 1\n    y = 2\n    return x\n",
        "bugs": [
            {"line": 3, "type": "logical_bug", "description": "y is unused."},
            {"line": 4, "type": "logical_bug", "description": "Should return x + y."},
        ],
    }

@pytest.fixture
def env_clean(clean_task):
    return CodeReviewEnv(clean_task)

@pytest.fixture
def env_buggy(buggy_task):
    return CodeReviewEnv(buggy_task)


# ─── Initialisation ──────────────────────────────────────────────────────────

class TestInit:
    def test_code_loaded(self, env_buggy, buggy_task):
        assert env_buggy.code == buggy_task["code"]

    def test_description_loaded(self, env_buggy, buggy_task):
        assert env_buggy.description == buggy_task["description"]

    def test_ground_truth_bugs_loaded(self, env_buggy, buggy_task):
        assert env_buggy.ground_truth_bugs == buggy_task["bugs"]

    def test_default_language_python(self, clean_task):
        del clean_task["language"]
        env = CodeReviewEnv(clean_task)
        assert env.language == "python"

    def test_explicit_language(self, env_buggy):
        assert env_buggy.language == "python"

    def test_initial_step_zero(self, env_buggy):
        assert env_buggy._step == 0

    def test_initial_not_done(self, env_buggy):
        assert env_buggy._done is False

    def test_initial_total_reward_zero(self, env_buggy):
        assert env_buggy._total_reward == 0.0

    def test_no_bugs_defaults_empty(self, clean_task):
        del clean_task["bugs"]
        env = CodeReviewEnv(clean_task)
        assert env.ground_truth_bugs == []


# ─── reset() ─────────────────────────────────────────────────────────────────

class TestReset:
    def test_reset_returns_observation(self, env_buggy):
        obs = env_buggy.reset()
        assert isinstance(obs, Observation)

    def test_reset_step_zero(self, env_buggy):
        env_buggy._step = 5
        env_buggy.reset()
        assert env_buggy._step == 0

    def test_reset_clears_done(self, env_buggy):
        env_buggy._done = True
        env_buggy.reset()
        assert env_buggy._done is False

    def test_reset_clears_bugs_found(self, env_buggy):
        env_buggy._bugs_found = ["some bug"]
        env_buggy.reset()
        assert env_buggy._bugs_found == []

    def test_reset_clears_total_reward(self, env_buggy):
        env_buggy._total_reward = 99.9
        env_buggy.reset()
        assert env_buggy._total_reward == 0.0

    def test_reset_observation_reward_is_zero(self, env_buggy):
        obs = env_buggy.reset()
        assert obs.reward == 0.0

    def test_reset_observation_step_is_zero(self, env_buggy):
        obs = env_buggy.reset()
        assert obs.step == 0

    def test_reset_observation_done_is_false(self, env_buggy):
        obs = env_buggy.reset()
        assert obs.done is False

    def test_reset_observation_bugs_found_empty(self, env_buggy):
        obs = env_buggy.reset()
        assert obs.bugs_found == []


# ─── step() ──────────────────────────────────────────────────────────────────

class TestStep:
    def test_step_returns_observation(self, env_buggy):
        env_buggy.reset()
        action = Action(action_type=ActionType.COMMENT, comment="looks fine")
        obs = env_buggy.step(action)
        assert isinstance(obs, Observation)

    def test_step_increments_step_counter(self, env_buggy):
        env_buggy.reset()
        action = Action(action_type=ActionType.COMMENT, comment="looks fine")
        env_buggy.step(action)
        assert env_buggy._step == 1

    def test_step_after_done_raises(self, env_buggy):
        env_buggy.reset()
        action = Action(action_type=ActionType.APPROVE)
        env_buggy.step(action)
        with pytest.raises(RuntimeError, match="Episode is done"):
            env_buggy.step(action)

    def test_approve_terminates_episode(self, env_buggy):
        env_buggy.reset()
        obs = env_buggy.step(Action(action_type=ActionType.APPROVE))
        assert obs.done is True

    def test_request_changes_terminates_episode(self, env_buggy):
        env_buggy.reset()
        obs = env_buggy.step(Action(action_type=ActionType.REQUEST_CHANGES))
        assert obs.done is True

    def test_comment_does_not_terminate(self, env_buggy):
        env_buggy.reset()
        obs = env_buggy.step(Action(action_type=ActionType.COMMENT, comment="ok"))
        assert obs.done is False

    def test_identify_bug_does_not_terminate(self, env_buggy):
        env_buggy.reset()
        obs = env_buggy.step(Action(
            action_type=ActionType.IDENTIFY_BUG,
            line_number=1,
            bug_description="Missing colon."
        ))
        assert obs.done is False

    def test_identify_bug_appends_to_bugs_found(self, env_buggy):
        env_buggy.reset()
        env_buggy.step(Action(
            action_type=ActionType.IDENTIFY_BUG,
            line_number=1,
            bug_description="Missing colon."
        ))
        assert "Missing colon." in env_buggy._bugs_found

    def test_total_reward_accumulates(self, env_buggy):
        env_buggy.reset()
        env_buggy.step(Action(action_type=ActionType.COMMENT, comment="ok"))
        env_buggy.step(Action(action_type=ActionType.COMMENT, comment="ok"))
        assert env_buggy._total_reward != 0.0

    def test_max_steps_terminates_episode(self, buggy_task):
        env = CodeReviewEnv(buggy_task)
        env.reset()
        for _ in range(CodeReviewEnv.MAX_STEPS - 1):
            env.step(Action(action_type=ActionType.COMMENT, comment="ok"))
        obs = env.step(Action(action_type=ActionType.COMMENT, comment="ok"))
        assert obs.done is True

    def test_step_observation_step_count_correct(self, env_buggy):
        env_buggy.reset()
        env_buggy.step(Action(action_type=ActionType.COMMENT, comment="a"))
        obs = env_buggy.step(Action(action_type=ActionType.COMMENT, comment="b"))
        assert obs.step == 2

    def test_step_observation_bugs_found_reflected(self, env_buggy):
        env_buggy.reset()
        obs = env_buggy.step(Action(
            action_type=ActionType.IDENTIFY_BUG,
            line_number=1,
            bug_description="Missing colon."
        ))
        assert "Missing colon." in obs.bugs_found


# ─── Properties ──────────────────────────────────────────────────────────────

class TestProperties:
    def test_is_done_false_initially(self, env_buggy):
        env_buggy.reset()
        assert env_buggy.is_done is False

    def test_is_done_true_after_approve(self, env_buggy):
        env_buggy.reset()
        env_buggy.step(Action(action_type=ActionType.APPROVE))
        assert env_buggy.is_done is True

    def test_total_reward_property(self, env_buggy):
        env_buggy.reset()
        env_buggy.step(Action(action_type=ActionType.COMMENT, comment="ok"))
        assert isinstance(env_buggy.total_reward, float)


# ─── _build_observation() ────────────────────────────────────────────────────

class TestBuildObservation:
    def test_observation_has_code_snippet(self, env_buggy):
        obs = env_buggy.reset()
        assert obs.code_snippet is not None
        assert len(obs.code_snippet) > 0

    def test_observation_code_has_line_numbers(self, env_buggy):
        obs = env_buggy.reset()
        assert "1 |" in obs.code_snippet

    def test_observation_task_description(self, env_buggy, buggy_task):
        obs = env_buggy.reset()
        assert obs.task_description == buggy_task["description"]

    def test_observation_language(self, env_buggy):
        obs = env_buggy.reset()
        assert obs.language == "python"

    def test_observation_line_count(self, env_buggy, buggy_task):
        obs = env_buggy.reset()
        expected = len(buggy_task["code"].splitlines())
        assert obs.line_count == expected

    def test_observation_info_contains_total_reward(self, env_buggy):
        obs = env_buggy.reset()
        assert "total_reward" in obs.info

    def test_observation_info_contains_max_steps(self, env_buggy):
        obs = env_buggy.reset()
        assert obs.info["max_steps"] == CodeReviewEnv.MAX_STEPS

    def test_observation_info_ground_truth_bug_count(self, env_buggy, buggy_task):
        obs = env_buggy.reset()
        assert obs.info["ground_truth_bug_count"] == len(buggy_task["bugs"])
