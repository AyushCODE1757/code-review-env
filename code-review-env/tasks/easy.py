"""
Easy Tasks — Syntax Errors
These tasks involve clear, syntactically invalid or obviously broken Python code.
The agent should be able to identify bugs from surface-level reading.
"""

EASY_TASKS = [
    {
        "taskid": "easy_001",
        "difficulty": "easy",
        "code": """\
def add_numbers(a, b)
    result = a + b
    return result
""",
        "type": "syntax_error",
        "description": "Missing colon at the end of the function definition.",
        "line": 1
    },
    {
        "taskid": "easy_002",
        "difficulty": "easy",
        "code": """\
def print_file(filepath):
    f = open(filepath, 'r'
    for line in f:
        print(line)
    f.close()
""",
        "type": "syntax_error",
        "description": "Missing closing parenthesis in open() call.",
        "line": 2
    },
    {
        "taskid": "easy_003",
        "difficulty": "easy",
        "code": """\
def square(n):
    return n * n

result = square(5
print(result)
""",
        "type": "syntax_error",
        "description": "Missing closing parenthesis in square() call.",
        "line": 4
    },
    {
        "taskid": "easy_004",
        "difficulty": "easy",
        "code": """\
def is_even(n):
    if n % 2 = 0:
        return True
    return False
""",
        "type": "syntax_error",
        "description": "Assignment operator '=' used instead of comparison '==' in if condition.",
        "line": 2
    },
]
