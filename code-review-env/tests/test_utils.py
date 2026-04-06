"""
Tests for env/utils.py — Helper functions
"""
import pytest
from env.utils import number_lines, extract_line, generate_diff, parse_llm_action, truncate_code


SAMPLE_CODE = "def foo():\n    return 1\n"


# ─── number_lines() ───────────────────────────────────────────────────────────

class TestNumberLines:
    def test_adds_line_numbers(self):
        result = number_lines(SAMPLE_CODE)
        assert "1 |" in result
        assert "2 |" in result

    def test_correct_number_of_lines(self):
        result = number_lines(SAMPLE_CODE)
        assert len(result.splitlines()) == len(SAMPLE_CODE.splitlines())

    def test_original_code_preserved(self):
        result = number_lines(SAMPLE_CODE)
        assert "def foo():" in result
        assert "return 1" in result

    def test_empty_string(self):
        result = number_lines("")
        assert result == ""

    def test_single_line(self):
        result = number_lines("x = 1")
        assert "1 |" in result
        assert "x = 1" in result

    def test_line_numbers_are_sequential(self):
        code = "a\nb\nc\n"
        result = number_lines(code)
        lines = result.splitlines()
        for i, line in enumerate(lines):
            assert f"{i+1}" in line


# ─── extract_line() ───────────────────────────────────────────────────────────

class TestExtractLine:
    def test_extract_first_line(self):
        result = extract_line(SAMPLE_CODE, 1)
        assert result == "def foo():"

    def test_extract_second_line(self):
        result = extract_line(SAMPLE_CODE, 2)
        assert result == "    return 1"

    def test_line_out_of_bounds_returns_none(self):
        assert extract_line(SAMPLE_CODE, 99) is None

    def test_line_zero_returns_none(self):
        assert extract_line(SAMPLE_CODE, 0) is None

    def test_negative_line_returns_none(self):
        assert extract_line(SAMPLE_CODE, -1) is None

    def test_empty_code_returns_none(self):
        assert extract_line("", 1) is None


# ─── generate_diff() ─────────────────────────────────────────────────────────

class TestGenerateDiff:
    def test_identical_code_no_diff_markers(self):
        diff = generate_diff(SAMPLE_CODE, SAMPLE_CODE)
        assert "-" not in [line[0] for line in diff.splitlines() if line]
        assert "+" not in [line[0] for line in diff.splitlines() if line]

    def test_changed_line_shows_minus_and_plus(self):
        original = "x = 1\n"
        modified = "x = 2\n"
        diff = generate_diff(original, modified)
        assert "- x = 1" in diff
        assert "+ x = 2" in diff

    def test_extra_line_in_modified_shows_plus(self):
        original = "a\n"
        modified = "a\nb\n"
        diff = generate_diff(original, modified)
        assert "+ b" in diff

    def test_extra_line_in_original_shows_minus(self):
        original = "a\nb\n"
        modified = "a\n"
        diff = generate_diff(original, modified)
        assert "- b" in diff

    def test_empty_inputs(self):
        diff = generate_diff("", "")
        assert diff == ""

    def test_returns_string(self):
        assert isinstance(generate_diff(SAMPLE_CODE, SAMPLE_CODE), str)


# ─── parse_llm_action() ───────────────────────────────────────────────────────

class TestParseLlmAction:
    def test_parse_action_type(self):
        result = parse_llm_action("ACTION: identify_bug")
        assert result["action_type"] == "identify_bug"

    def test_parse_line_number_as_int(self):
        result = parse_llm_action("ACTION: identify_bug\nLINE: 5")
        assert result["line_number"] == 5
        assert isinstance(result["line_number"], int)

    def test_parse_comment(self):
        result = parse_llm_action("COMMENT: This looks wrong")
        assert result["comment"] == "This looks wrong"

    def test_parse_bug_description(self):
        result = parse_llm_action("BUG_DESCRIPTION: Missing semicolon")
        assert result["bug_description"] == "Missing semicolon"

    def test_parse_suggested_fix(self):
        result = parse_llm_action("SUGGESTED_FIX: Add semicolon at end")
        assert result["suggested_fix"] == "Add semicolon at end"

    def test_parse_full_block(self):
        raw = (
            "ACTION: identify_bug\n"
            "LINE: 3\n"
            "BUG_DESCRIPTION: Off-by-one error\n"
            "SUGGESTED_FIX: Change index to len(arr)-1\n"
            "COMMENT: Classic mistake"
        )
        result = parse_llm_action(raw)
        assert result["action_type"] == "identify_bug"
        assert result["line_number"] == 3
        assert result["bug_description"] == "Off-by-one error"
        assert result["suggested_fix"] == "Change index to len(arr)-1"
        assert result["comment"] == "Classic mistake"

    def test_case_insensitive_keys(self):
        result = parse_llm_action("action: approve")
        assert result["action_type"] == "approve"

    def test_empty_string_returns_empty_dict(self):
        result = parse_llm_action("")
        assert result == {}

    def test_missing_fields_not_in_result(self):
        result = parse_llm_action("ACTION: approve")
        assert "line_number" not in result
        assert "comment" not in result

    def test_returns_dict(self):
        assert isinstance(parse_llm_action("ACTION: approve"), dict)


# ─── truncate_code() ─────────────────────────────────────────────────────────

class TestTruncateCode:
    def test_short_code_unchanged(self):
        code = "x = 1\ny = 2\n"
        result = truncate_code(code, max_lines=100)
        # Truncate works on splitlines, but original code ends with \n
        assert "x = 1" in result
        assert "y = 2" in result

    def test_truncation_adds_message(self):
        code = "\n".join([f"line_{i}" for i in range(200)])
        result = truncate_code(code, max_lines=100)
        assert "truncated" in result.lower()

    def test_truncated_to_correct_line_count(self):
        code = "\n".join([f"line_{i}" for i in range(200)])
        result = truncate_code(code, max_lines=50)
        lines = result.splitlines()
        # 50 content lines + 1 truncation message line
        assert lines[49] == "line_49"

    def test_exactly_at_limit_not_truncated(self):
        code = "\n".join([f"line_{i}" for i in range(100)])
        result = truncate_code(code, max_lines=100)
        assert "truncated" not in result.lower()

    def test_default_max_lines_is_100(self):
        code = "\n".join([f"line_{i}" for i in range(150)])
        result = truncate_code(code)
        assert "truncated" in result.lower()

    def test_returns_string(self):
        assert isinstance(truncate_code(SAMPLE_CODE), str)

    def test_empty_code_unchanged(self):
        result = truncate_code("", max_lines=100)
        assert result == ""
