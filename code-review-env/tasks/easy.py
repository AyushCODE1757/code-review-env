"""
Easy Tasks — Syntax Errors
These tasks involve clear, syntactically invalid or obviously broken Python code.
The agent should be able to identify bugs from surface-level reading.
"""

EASY_TASKS = [
    {
        "id": "easy_001",
        "difficulty": "easy",
        "language": "python",
        "description": (
            "Review the following Python function. It is supposed to add two numbers "
            "and return the result. Identify any bugs or issues."
        ),
        "code": """\
def add_numbers(a, b)
    result = a + b
    return result
""",
        "bugs": [
            {
                "line": 1,
                "type": "syntax_error",
                "description": "Missing colon at the end of the function definition.",
            }
        ],
    },
    {
        "id": "easy_002",
        "difficulty": "easy",
        "language": "python",
        "description": (
            "Review this Python script that reads a file and prints each line. "
            "Identify any bugs."
        ),
        "code": """\
def print_file(filepath):
    f = open(filepath, 'r'
    for line in f:
        print(line)
    f.close()
""",
        "bugs": [
            {
                "line": 2,
                "type": "syntax_error",
                "description": "Missing closing parenthesis in open() call.",
            }
        ],
    },
    {
        "id": "easy_003",
        "difficulty": "easy",
        "language": "python",
        "description": (
            "Review this function that computes the square of a number. "
            "Spot the bug."
        ),
        "code": """\
def square(n):
    return n * n

result = square(5
print(result)
""",
        "bugs": [
            {
                "line": 4,
                "type": "syntax_error",
                "description": "Missing closing parenthesis in square() call.",
            }
        ],
    },
    {
        "id": "easy_004",
        "difficulty": "easy",
        "language": "python",
        "description": (
            "Review this function that checks if a number is even. Find any bugs."
        ),
        "code": """\
def is_even(n):
    if n % 2 = 0:
        return True
    return False
""",
        "bugs": [
            {
                "line": 2,
                "type": "syntax_error",
                "description": "Assignment operator '=' used instead of comparison '==' in if condition.",
            }
        ],
    },
]
