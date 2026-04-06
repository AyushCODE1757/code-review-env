"""
Tests for tasks/ — Easy, Medium, Hard task definitions
"""
import pytest
import ast
from tasks.easy import EASY_TASKS
from tasks.medium import MEDIUM_TASKS
from tasks.hard import HARD_TASKS

ALL_TASKS = [
    ("easy", EASY_TASKS),
    ("medium", MEDIUM_TASKS),
    ("hard", HARD_TASKS),
]

REQUIRED_KEYS = {"id", "difficulty", "language", "description", "code", "bugs"}
REQUIRED_BUG_KEYS = {"line", "type", "description"}


# ─── Schema validation ────────────────────────────────────────────────────────

class TestSchema:
    @pytest.mark.parametrize("difficulty, tasks", ALL_TASKS)
    def test_tasks_is_nonempty_list(self, difficulty, tasks):
        assert isinstance(tasks, list)
        assert len(tasks) > 0, f"{difficulty} tasks list is empty"

    @pytest.mark.parametrize("difficulty, tasks", ALL_TASKS)
    def test_all_tasks_have_required_keys(self, difficulty, tasks):
        for task in tasks:
            missing = REQUIRED_KEYS - task.keys()
            assert not missing, f"Task {task.get('id')} missing keys: {missing}"

    @pytest.mark.parametrize("difficulty, tasks", ALL_TASKS)
    def test_difficulty_field_matches_list(self, difficulty, tasks):
        for task in tasks:
            assert task["difficulty"] == difficulty, (
                f"Task {task['id']} has difficulty='{task['difficulty']}' but is in {difficulty} list"
            )

    @pytest.mark.parametrize("difficulty, tasks", ALL_TASKS)
    def test_all_task_ids_are_unique(self, difficulty, tasks):
        ids = [t["id"] for t in tasks]
        assert len(ids) == len(set(ids)), f"Duplicate IDs in {difficulty} tasks: {ids}"

    @pytest.mark.parametrize("difficulty, tasks", ALL_TASKS)
    def test_language_is_string(self, difficulty, tasks):
        for task in tasks:
            assert isinstance(task["language"], str)
            assert len(task["language"]) > 0

    @pytest.mark.parametrize("difficulty, tasks", ALL_TASKS)
    def test_description_is_nonempty_string(self, difficulty, tasks):
        for task in tasks:
            assert isinstance(task["description"], str)
            assert len(task["description"].strip()) > 0

    @pytest.mark.parametrize("difficulty, tasks", ALL_TASKS)
    def test_code_is_nonempty_string(self, difficulty, tasks):
        for task in tasks:
            assert isinstance(task["code"], str)
            assert len(task["code"].strip()) > 0

    @pytest.mark.parametrize("difficulty, tasks", ALL_TASKS)
    def test_bugs_is_list(self, difficulty, tasks):
        for task in tasks:
            assert isinstance(task["bugs"], list)

    @pytest.mark.parametrize("difficulty, tasks", ALL_TASKS)
    def test_bugs_have_required_keys(self, difficulty, tasks):
        for task in tasks:
            for bug in task["bugs"]:
                missing = REQUIRED_BUG_KEYS - bug.keys()
                assert not missing, f"Bug in {task['id']} missing keys: {missing}"

    @pytest.mark.parametrize("difficulty, tasks", ALL_TASKS)
    def test_bug_line_numbers_are_positive_ints(self, difficulty, tasks):
        for task in tasks:
            for bug in task["bugs"]:
                assert isinstance(bug["line"], int), f"Bug line in {task['id']} is not int"
                assert bug["line"] >= 1, f"Bug line in {task['id']} is < 1"

    @pytest.mark.parametrize("difficulty, tasks", ALL_TASKS)
    def test_bug_line_within_code_bounds(self, difficulty, tasks):
        for task in tasks:
            code_lines = len(task["code"].splitlines())
            for bug in task["bugs"]:
                assert bug["line"] <= code_lines + 1, (
                    f"Bug line {bug['line']} out of range in {task['id']} (code has {code_lines} lines)"
                )

    @pytest.mark.parametrize("difficulty, tasks", ALL_TASKS)
    def test_bug_description_is_nonempty_string(self, difficulty, tasks):
        for task in tasks:
            for bug in task["bugs"]:
                assert isinstance(bug["description"], str)
                assert len(bug["description"].strip()) > 0


# ─── Easy task specific ───────────────────────────────────────────────────────

class TestEasyTasks:
    def test_all_easy_bugs_are_syntax_errors(self):
        for task in EASY_TASKS:
            for bug in task["bugs"]:
                assert bug["type"] == "syntax_error", (
                    f"Expected syntax_error in {task['id']}, got {bug['type']}"
                )

    def test_easy_code_is_actually_invalid_python(self):
        """Easy tasks should have syntactically broken code."""
        for task in EASY_TASKS:
            try:
                ast.parse(task["code"])
                pytest.fail(
                    f"Easy task {task['id']} has valid Python — expected a syntax error"
                )
            except SyntaxError:
                pass  # expected

    def test_easy_tasks_have_exactly_one_bug(self):
        for task in EASY_TASKS:
            assert len(task["bugs"]) == 1, (
                f"Easy task {task['id']} should have 1 bug, found {len(task['bugs'])}"
            )


# ─── Medium task specific ─────────────────────────────────────────────────────

class TestMediumTasks:
    def test_all_medium_bugs_are_logical(self):
        for task in MEDIUM_TASKS:
            for bug in task["bugs"]:
                assert bug["type"] == "logical_bug", (
                    f"Expected logical_bug in {task['id']}, got {bug['type']}"
                )

    def test_medium_code_is_valid_python(self):
        """Medium tasks should be syntactically valid but logically wrong."""
        for task in MEDIUM_TASKS:
            try:
                ast.parse(task["code"])
            except SyntaxError as e:
                pytest.fail(f"Medium task {task['id']} has a syntax error: {e}")

    def test_medium_binary_search_bug_on_line_2(self):
        task = next(t for t in MEDIUM_TASKS if t["id"] == "medium_001")
        assert task["bugs"][0]["line"] == 2

    def test_medium_fizzbuzz_bug_on_line_7(self):
        task = next(t for t in MEDIUM_TASKS if t["id"] == "medium_003")
        assert task["bugs"][0]["line"] == 7


# ─── Hard task specific ───────────────────────────────────────────────────────

class TestHardTasks:
    def test_all_hard_bugs_are_performance(self):
        for task in HARD_TASKS:
            for bug in task["bugs"]:
                assert bug["type"] == "performance", (
                    f"Expected performance in {task['id']}, got {bug['type']}"
                )

    def test_hard_code_is_valid_python(self):
        """Hard tasks should be syntactically correct."""
        for task in HARD_TASKS:
            try:
                ast.parse(task["code"])
            except SyntaxError as e:
                pytest.fail(f"Hard task {task['id']} has a syntax error: {e}")

    def test_hard_fibonacci_is_hard_001(self):
        task = next(t for t in HARD_TASKS if t["id"] == "hard_001")
        assert "fibonacci" in task["code"].lower()

    def test_hard_duplicate_detection_is_hard_002(self):
        task = next(t for t in HARD_TASKS if t["id"] == "hard_002")
        assert "has_duplicates" in task["code"]


# ─── Cross-difficulty ─────────────────────────────────────────────────────────

class TestCrossDifficulty:
    def test_all_task_ids_globally_unique(self):
        all_ids = (
            [t["id"] for t in EASY_TASKS]
            + [t["id"] for t in MEDIUM_TASKS]
            + [t["id"] for t in HARD_TASKS]
        )
        assert len(all_ids) == len(set(all_ids)), f"Globally duplicate task IDs: {all_ids}"

    def test_no_task_id_is_empty(self):
        for _, tasks in ALL_TASKS:
            for task in tasks:
                assert task["id"].strip() != ""
