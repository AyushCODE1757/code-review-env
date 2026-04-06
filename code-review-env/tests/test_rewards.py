"""
Tests for env/rewards.py — RewardCalculator
"""
import pytest
from env.models import Action, ActionType
from env.rewards import RewardCalculator


# ─── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture
def no_bugs():
    return []

@pytest.fixture
def one_bug():
    return [{"line": 1, "type": "syntax_error", "description": "Missing colon."}]

@pytest.fixture
def two_bugs():
    return [
        {"line": 1, "type": "syntax_error", "description": "Missing colon."},
        {"line": 5, "type": "logical_bug", "description": "Wrong operator."},
    ]

@pytest.fixture
def calc_no_bugs(no_bugs):
    return RewardCalculator(no_bugs)

@pytest.fixture
def calc_one_bug(one_bug):
    return RewardCalculator(one_bug)

@pytest.fixture
def calc_two_bugs(two_bugs):
    return RewardCalculator(two_bugs)


# ─── Step Penalty ────────────────────────────────────────────────────────────

class TestStepPenalty:
    def test_comment_action_incurs_step_penalty(self, calc_one_bug):
        action = Action(action_type=ActionType.COMMENT, comment="looks fine")
        reward = calc_one_bug.calculate(action, step=0)
        assert reward == pytest.approx(RewardCalculator.STEP_PENALTY, abs=1e-4)

    def test_step_penalty_applies_to_all_actions(self, calc_no_bugs):
        action = Action(action_type=ActionType.COMMENT, comment="ok")
        reward = calc_no_bugs.calculate(action, step=3)
        assert reward <= 0  # at minimum the step penalty applies


# ─── identify_bug ─────────────────────────────────────────────────────────────

class TestIdentifyBug:
    def test_correct_bug_on_exact_line_gives_positive_reward(self, calc_one_bug):
        action = Action(
            action_type=ActionType.IDENTIFY_BUG,
            line_number=1,
            bug_description="Missing colon."
        )
        reward = calc_one_bug.calculate(action, step=0)
        expected = RewardCalculator.STEP_PENALTY + RewardCalculator.CORRECT_BUG_FOUND
        assert reward == pytest.approx(expected, abs=1e-4)

    def test_correct_bug_within_2_lines_tolerance(self, calc_one_bug):
        action = Action(
            action_type=ActionType.IDENTIFY_BUG,
            line_number=3,  # bug is at line 1, tolerance ±2
            bug_description="Missing colon."
        )
        reward = calc_one_bug.calculate(action, step=0)
        assert reward > RewardCalculator.STEP_PENALTY  # got CORRECT_BUG_FOUND

    def test_correct_bug_outside_tolerance_is_penalised(self, calc_one_bug):
        action = Action(
            action_type=ActionType.IDENTIFY_BUG,
            line_number=10,  # bug is at line 1
            bug_description="Missing colon."
        )
        reward = calc_one_bug.calculate(action, step=0)
        expected = RewardCalculator.STEP_PENALTY + RewardCalculator.WRONG_BUG_FLAGGED
        assert reward == pytest.approx(expected, abs=1e-4)

    def test_wrong_line_with_no_match_gives_wrong_penalty(self, calc_one_bug):
        action = Action(
            action_type=ActionType.IDENTIFY_BUG,
            line_number=99,
            bug_description="Invented bug."
        )
        reward = calc_one_bug.calculate(action, step=0)
        assert reward < RewardCalculator.STEP_PENALTY

    def test_correct_bug_with_fix_gives_bonus(self, calc_one_bug):
        action = Action(
            action_type=ActionType.IDENTIFY_BUG,
            line_number=1,
            bug_description="Missing colon.",
            suggested_fix="Add colon after def statement."
        )
        reward = calc_one_bug.calculate(action, step=0)
        expected = (
            RewardCalculator.STEP_PENALTY
            + RewardCalculator.CORRECT_BUG_FOUND
            + RewardCalculator.CORRECT_FIX_BONUS
        )
        assert reward == pytest.approx(expected, abs=1e-4)

    def test_same_bug_cannot_be_found_twice(self, calc_one_bug):
        action = Action(
            action_type=ActionType.IDENTIFY_BUG,
            line_number=1,
            bug_description="Missing colon."
        )
        calc_one_bug.calculate(action, step=0)  # first time — correct
        reward2 = calc_one_bug.calculate(action, step=1)  # second time — no match
        expected = RewardCalculator.STEP_PENALTY + RewardCalculator.WRONG_BUG_FLAGGED
        assert reward2 == pytest.approx(expected, abs=1e-4)

    def test_none_line_number_returns_wrong_penalty(self, calc_one_bug):
        action = Action(
            action_type=ActionType.IDENTIFY_BUG,
            line_number=None,
            bug_description="Missing colon."
        )
        reward = calc_one_bug.calculate(action, step=0)
        expected = RewardCalculator.STEP_PENALTY + RewardCalculator.WRONG_BUG_FLAGGED
        assert reward == pytest.approx(expected, abs=1e-4)

    def test_can_find_both_bugs_in_two_bug_task(self, calc_two_bugs):
        a1 = Action(action_type=ActionType.IDENTIFY_BUG, line_number=1, bug_description="Missing colon.")
        a2 = Action(action_type=ActionType.IDENTIFY_BUG, line_number=5, bug_description="Wrong operator.")
        r1 = calc_two_bugs.calculate(a1, step=0)
        r2 = calc_two_bugs.calculate(a2, step=1)
        assert r1 > RewardCalculator.STEP_PENALTY
        assert r2 > RewardCalculator.STEP_PENALTY
        assert len(calc_two_bugs.found_bug_indices) == 2


# ─── approve ─────────────────────────────────────────────────────────────────

class TestApprove:
    def test_approve_clean_code_gives_positive_reward(self, calc_no_bugs):
        action = Action(action_type=ActionType.APPROVE)
        reward = calc_no_bugs.calculate(action, step=0)
        expected = RewardCalculator.STEP_PENALTY + RewardCalculator.APPROVE_CLEAN_CODE
        assert reward == pytest.approx(expected, abs=1e-4)

    def test_approve_buggy_code_gives_false_positive_penalty(self, calc_one_bug):
        action = Action(action_type=ActionType.APPROVE)
        reward = calc_one_bug.calculate(action, step=0)
        expected = RewardCalculator.STEP_PENALTY + RewardCalculator.FALSE_POSITIVE_PENALTY
        assert reward == pytest.approx(expected, abs=1e-4)


# ─── request_changes ──────────────────────────────────────────────────────────

class TestRequestChanges:
    def test_request_changes_reward_is_only_step_penalty(self, calc_one_bug):
        action = Action(action_type=ActionType.REQUEST_CHANGES)
        reward = calc_one_bug.calculate(action, step=0)
        assert reward == pytest.approx(RewardCalculator.STEP_PENALTY, abs=1e-4)

    def test_request_changes_on_clean_code_is_step_penalty(self, calc_no_bugs):
        action = Action(action_type=ActionType.REQUEST_CHANGES)
        reward = calc_no_bugs.calculate(action, step=0)
        assert reward == pytest.approx(RewardCalculator.STEP_PENALTY, abs=1e-4)


# ─── final_penalty ────────────────────────────────────────────────────────────

class TestFinalPenalty:
    def test_no_bugs_no_penalty(self, calc_no_bugs):
        assert calc_no_bugs.final_penalty() == 0.0

    def test_all_bugs_found_no_penalty(self, calc_one_bug):
        calc_one_bug.calculate(
            Action(action_type=ActionType.IDENTIFY_BUG, line_number=1, bug_description="Missing colon."),
            step=0
        )
        assert calc_one_bug.final_penalty() == 0.0

    def test_missed_bug_penalised(self, calc_one_bug):
        penalty = calc_one_bug.final_penalty()
        assert penalty == pytest.approx(RewardCalculator.MISSED_BUG_PENALTY, abs=1e-4)

    def test_two_missed_bugs_double_penalty(self, calc_two_bugs):
        penalty = calc_two_bugs.final_penalty()
        assert penalty == pytest.approx(2 * RewardCalculator.MISSED_BUG_PENALTY, abs=1e-4)

    def test_partial_miss_correct_penalty(self, calc_two_bugs):
        calc_two_bugs.calculate(
            Action(action_type=ActionType.IDENTIFY_BUG, line_number=1, bug_description="Missing colon."),
            step=0
        )
        penalty = calc_two_bugs.final_penalty()
        assert penalty == pytest.approx(RewardCalculator.MISSED_BUG_PENALTY, abs=1e-4)


# ─── reset() ─────────────────────────────────────────────────────────────────

class TestRewardCalculatorReset:
    def test_reset_clears_found_bug_indices(self, calc_one_bug):
        calc_one_bug.calculate(
            Action(action_type=ActionType.IDENTIFY_BUG, line_number=1, bug_description="Missing colon."),
            step=0
        )
        assert len(calc_one_bug.found_bug_indices) == 1
        calc_one_bug.reset()
        assert len(calc_one_bug.found_bug_indices) == 0

    def test_reset_allows_finding_same_bug_again(self, calc_one_bug):
        action = Action(
            action_type=ActionType.IDENTIFY_BUG,
            line_number=1,
            bug_description="Missing colon."
        )
        calc_one_bug.calculate(action, step=0)
        calc_one_bug.reset()
        reward = calc_one_bug.calculate(action, step=0)
        assert reward > RewardCalculator.STEP_PENALTY  # matched again after reset
