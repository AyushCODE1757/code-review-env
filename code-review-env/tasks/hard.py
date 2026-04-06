"""
Hard Tasks — Performance Issues
These tasks involve code that is correct but highly inefficient.
The agent must recognize algorithmic or memory inefficiencies.
"""

HARD_TASKS = [
    {
        "taskid": "hard_001",
        "difficulty": "hard",
        "code": """\
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

# Called with large n
print(fibonacci(40))
""",
        "type": "performance",
        "description": "Naive recursive Fibonacci has O(2^n) time complexity due to repeated subproblem computation. Use memoization (@functools.lru_cache) or an iterative approach for O(n) performance.",
        "line": 4
    },
    {
        "taskid": "hard_002",
        "difficulty": "hard",
        "code": """\
def has_duplicates(lst):
    for i in range(len(lst)):
        for j in range(len(lst)):
            if i != j and lst[i] == lst[j]:
                return True
    return False
""",
        "type": "performance",
        "description": "O(n^2) nested loop for duplicate detection. Using a set — 'return len(lst) != len(set(lst))' — achieves O(n) time and space.",
        "line": 2
    },
    {
        "taskid": "hard_003",
        "difficulty": "hard",
        "code": """\
def build_string(words):
    result = ""
    for word in words:
        result = result + word + " "
    return result.strip()
""",
        "type": "performance",
        "description": "String concatenation inside a loop creates a new string object on every iteration, resulting in O(n^2) time. Use '\" \".join(words)' instead for O(n).",
        "line": 4
    },
    {
        "taskid": "hard_004",
        "difficulty": "hard",
        "code": """\
def process_large_file(filepath):
    with open(filepath, 'r') as f:
        lines = f.readlines()  # loads entire file into memory
    results = []
    for line in lines:
        results.append(line.strip().upper())
    return results
""",
        "type": "performance",
        "description": "f.readlines() loads the entire file into memory at once. For large files, iterate over the file object directly or use a generator to process one line at a time.",
        "line": 3
    },
]
