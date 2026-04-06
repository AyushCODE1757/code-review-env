"""
Tests for grader/grader.py — Grader
"""
import pytest
from grader.grader import Grader, GradeResult


# ─── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture
def grader():
    return Grader(max_steps=10)

@pytest.fixture
def clean_task():
    return {"id": "clean_001", "difficulty": "easy", "bugs": []}

@pytest.fixture
def one_bug_task():
    return {
        "id": "bug_001",
        "difficulty": "easy",
        "bugs": [{"line": 1, "type": "syntax_error", "description": "Missing colon."}],
    }

@pytest.fixture
def two_bug_task():
    return {
        "id": "bug_002",
        "difficulty": "medium",
        "bugs": [
            {"line": 1, "type": "syntax_error", "description": "Missing colon."},
            {"line": 5, "type": "logical_bug", "description": "Wrong operator."},
        ],
    }


# ─── grade() return type ──────────────────────────────────────────────────────

class TestGradeReturnType:
    def test_returns_grade_result(self, grader, one_bug_task):
        result = grader.grade(one_bug_task, ["Missing colon."], 0, 3, 0.9, "request_changes")
        assert isinstance(result, GradeResult)

    def test_task_id_correct(self, grader, one_bug_task):
        result = grader.grade(one_bug_task, ["Missing colon."], 0, 3, 0.9, "request_changes")
        assert result.task_id == "bug_001"

    def test_difficulty_correct(self, grader, one_bug_task):
        result = grader.grade(one_bug_task, ["Missing colon."], 0, 3, 0.9, "request_changes")
        assert result.difficulty == "easy"

    def test_unknown_task_id_defaults(self, grader):
        result = grader.grade({}, [], 0, 5, 0.0, "approve")
        assert result.task_id == "unknown"
        assert result.difficulty == "unknown"


# ─── Bug detection scoring ────────────────────────────────────────────────────

class TestBugDetectionScore:
    def test_all_bugs_found_perfect_detection(self, grader, one_bug_task):
        result = grader.grade(one_bug_task, ["Missing colon."], 0, 3, 0.9, "request_changes")
        assert result.bugs_found == 1
        assert result.bugs_missed == 0

    def test_no_bugs_found_all_missed(self, grader, one_bug_task):
        result = grader.grade(one_bug_task, [], 0, 5, -0.5, "approve")
        assert result.bugs_found == 0
        assert result.bugs_missed == 1

    def test_partial_detection(self, grader, two_bug_task):
        result = grader.grade(two_bug_task, ["Missing colon."], 0, 5, 0.5, "request_changes")
        assert result.bugs_found == 1
        assert result.bugs_missed == 1

    def test_clean_task_no_bugs_to_find(self, grader, clean_task):
        result = grader.grade(clean_task, [], 0, 3, 0.5, "approve")
        assert result.bugs_found == 0
        assert result.bugs_missed == 0

    def test_bugs_found_capped_at_total(self, grader, one_bug_task):
        # Agent reports more bugs than exist
        result = grader.grade(one_bug_task, ["Bug A", "Bug B", "Bug C"], 0, 3, 0.9, "request_changes")
        assert result.bugs_found == 1  # capped at total_bugs


# ─── False positives ──────────────────────────────────────────────────────────

class TestFalsePositives:
    def test_zero_false_positives(self, grader, one_bug_task):
        result = grader.grade(one_bug_task, ["Missing colon."], 0, 3, 0.9, "request_changes")
        assert result.false_positives == 0

    def test_false_positives_recorded(self, grader, one_bug_task):
        result = grader.grade(one_bug_task, ["Missing colon."], 2, 5, 0.5, "request_changes")
        assert result.false_positives == 2

    def test_high_false_positives_reduce_score(self, grader, one_bug_task):
        result_clean = grader.grade(one_bug_task, ["Missing colon."], 0, 3, 0.9, "request_changes")
        result_fp = grader.grade(one_bug_task, ["Missing colon."], 5, 3, 0.9, "request_changes")
        assert result_fp.score < result_clean.score


# ─── Efficiency scoring ───────────────────────────────────────────────────────

class TestEfficiencyScore:
    def test_fewer_steps_gives_higher_score(self, grader, one_bug_task):
        result_fast = grader.grade(one_bug_task, ["Missing colon."], 0, 2, 0.9, "request_changes")
        result_slow = grader.grade(one_bug_task, ["Missing colon."], 0, 9, 0.9, "request_changes")
        assert result_fast.score > result_slow.score

    def test_steps_recorded_correctly(self, grader, one_bug_task):
        result = grader.grade(one_bug_task, ["Missing colon."], 0, 7, 0.9, "request_changes")
        assert result.steps_taken == 7


# ─── Decision quality ─────────────────────────────────────────────────────────

class TestDecisionQuality:
    def test_approve_clean_code_is_correct_decision(self, grader, clean_task):
        result = grader.grade(clean_task, [], 0, 2, 0.5, "approve")
        assert result.approved is True

    def test_request_changes_on_buggy_code_is_correct(self, grader, one_bug_task):
        result = grader.grade(one_bug_task, ["Missing colon."], 0, 3, 0.9, "request_changes")
        assert result.approved is False

    def test_approve_buggy_code_hurts_score(self, grader, one_bug_task):
        result_correct = grader.grade(one_bug_task, ["Missing colon."], 0, 3, 0.9, "request_changes")
        result_wrong = grader.grade(one_bug_task, ["Missing colon."], 0, 3, 0.9, "approve")
        assert result_correct.score > result_wrong.score

    def test_request_changes_clean_code_suboptimal(self, grader, clean_task):
        result_correct = grader.grade(clean_task, [], 0, 3, 0.5, "approve")
        result_subopt = grader.grade(clean_task, [], 0, 3, 0.5, "request_changes")
        assert result_correct.score > result_subopt.score


# ─── Composite score ──────────────────────────────────────────────────────────

class TestCompositeScore:
    def test_score_between_0_and_100(self, grader, one_bug_task):
        result = grader.grade(one_bug_task, ["Missing colon."], 0, 3, 0.9, "request_changes")
        assert 0.0 <= result.score <= 100.0

    def test_perfect_run_high_score(self, grader, one_bug_task):
        # Find the bug fast, no false positives, correct decision
        result = grader.grade(one_bug_task, ["Missing colon."], 0, 2, 1.0, "request_changes")
        assert result.score >= 70.0

    def test_worst_run_low_score(self, grader, one_bug_task):
        # Find nothing, many false positives, wrong decision, max steps
        result = grader.grade(one_bug_task, [], 5, 10, -2.0, "approve")
        assert result.score < 40.0

    def test_total_reward_recorded(self, grader, one_bug_task):
        result = grader.grade(one_bug_task, ["Missing colon."], 0, 3, 1.23, "request_changes")
        assert result.total_reward == pytest.approx(1.23, abs=1e-4)


# ─── Feedback messages ────────────────────────────────────────────────────────

class TestFeedback:
    def test_feedback_is_list(self, grader, one_bug_task):
        result = grader.grade(one_bug_task, ["Missing colon."], 0, 3, 0.9, "request_changes")
        assert isinstance(result.feedback, list)

    def test_perfect_feedback_all_positive(self, grader, one_bug_task):
        result = grader.grade(one_bug_task, ["Missing colon."], 0, 2, 1.0, "request_changes")
        assert all("✅" in msg for msg in result.feedback)

    def test_missed_bug_feedback_warning(self, grader, one_bug_task):
        result = grader.grade(one_bug_task, [], 0, 5, -0.5, "approve")
        assert any("missed" in msg.lower() or "❌" in msg for msg in result.feedback)

    def test_false_positive_feedback(self, grader, one_bug_task):
        result = grader.grade(one_bug_task, ["Missing colon."], 3, 3, 0.5, "request_changes")
        assert any("false positive" in msg.lower() for msg in result.feedback)

    def test_wrong_decision_feedback(self, grader, one_bug_task):
        result = grader.grade(one_bug_task, ["Missing colon."], 0, 3, 0.9, "approve")
        assert any("❌" in msg for msg in result.feedback)


# ─── summary() ───────────────────────────────────────────────────────────────

class TestSummary:
    def test_summary_returns_string(self, grader, one_bug_task):
        result = grader.grade(one_bug_task, ["Missing colon."], 0, 3, 0.9, "request_changes")
        summary = grader.summary(result)
        assert isinstance(summary, str)

    def test_summary_contains_task_id(self, grader, one_bug_task):
        result = grader.grade(one_bug_task, ["Missing colon."], 0, 3, 0.9, "request_changes")
        summary = grader.summary(result)
        assert "bug_001" in summary

    def test_summary_contains_score(self, grader, one_bug_task):
        result = grader.grade(one_bug_task, ["Missing colon."], 0, 3, 0.9, "request_changes")
        summary = grader.summary(result)
        assert str(result.score) in summary

    def test_summary_contains_separator(self, grader, one_bug_task):
        result = grader.grade(one_bug_task, ["Missing colon."], 0, 3, 0.9, "request_changes")
        summary = grader.summary(result)
        assert "=" * 10 in summary
