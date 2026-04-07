"""
Easy Tasks — Syntax Errors
These tasks involve clear, syntactically invalid or obviously broken Python code.
The agent should be able to identify bugs from surface-level reading.
"""

EASY_TASKS = [
    {
        "task_id": "easy_1",
        "difficulty": "easy",
        "code": "print('hello'",
        "bugs": [
            {
                "type": "syntax_error",
                "description": "missing closing parenthesis",
                "line": 1
            }
        ]
    }
]
