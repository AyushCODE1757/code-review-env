"""
Medium Tasks — Logical Bugs
These tasks involve code that is syntactically valid but contains logical errors.
The agent must understand program logic to identify the issue.
"""

MEDIUM_TASKS = [
    {
        "taskid": "medium_001",
        "difficulty": "medium",
        "code": """\
def binary_search(arr, target):
    left, right = 0, len(arr)
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1
""",
        "type": "logical_bug",
        "description": "'right' should be initialized to len(arr) - 1, not len(arr). Using len(arr) causes an IndexError when arr[mid] is accessed.",
        "line": 2
    },
    {
        "taskid": "medium_002",
        "difficulty": "medium",
        "code": """\
def reverse_string(s):
    result = ""
    for i in range(len(s)):
        result += s[i]
    return result
""",
        "type": "logical_bug",
        "description": "The loop iterates forward (range(len(s))), so 'result' ends up being the same as the input. It should iterate in reverse: range(len(s) - 1, -1, -1).",
        "line": 3
    },
    {
        "taskid": "medium_003",
        "difficulty": "medium",
        "code": """\
def fizzbuzz(n):
    for i in range(1, n + 1):
        if i % 3 == 0:
            print("Fizz")
        elif i % 5 == 0:
            print("Buzz")
        elif i % 15 == 0:
            print("FizzBuzz")
        else:
            print(i)
""",
        "type": "logical_bug",
        "description": "The FizzBuzz condition (i % 15 == 0) will never be reached because it is checked after the Fizz (i % 3 == 0) and Buzz (i % 5 == 0) conditions. It should be checked first.",
        "line": 7
    },
    {
        "taskid": "medium_004",
        "difficulty": "medium",
        "code": """\
def count_vowels(s):
    vowels = "aeiou"
    count = 0
    for char in s:
        if char in vowels:
            count =+ 1
    return count
""",
        "type": "logical_bug",
        "description": "'count =+ 1' is an assignment (count = +1), not an increment. It should be 'count += 1'.",
        "line": 6
    },
]
