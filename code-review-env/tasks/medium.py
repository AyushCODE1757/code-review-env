"""
Medium Tasks — Logical Bugs
These tasks involve code that is syntactically valid but contains logical errors.
The agent must understand program logic to identify the issue.
"""

MEDIUM_TASKS = [
    {
        "id": "medium_001",
        "difficulty": "medium",
        "language": "python",
        "description": (
            "Review this binary search implementation. It is supposed to return "
            "the index of the target in a sorted list, or -1 if not found."
        ),
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
        "bugs": [
            {
                "line": 2,
                "type": "logical_bug",
                "description": (
                    "'right' should be initialized to len(arr) - 1, not len(arr). "
                    "Using len(arr) causes an IndexError when arr[mid] is accessed."
                ),
            }
        ],
    },
    {
        "id": "medium_002",
        "difficulty": "medium",
        "language": "python",
        "description": (
            "Review this function that is supposed to reverse a string."
        ),
        "code": """\
def reverse_string(s):
    result = ""
    for i in range(len(s)):
        result += s[i]
    return result
""",
        "bugs": [
            {
                "line": 3,
                "type": "logical_bug",
                "description": (
                    "The loop iterates forward (range(len(s))), so 'result' ends up "
                    "being the same as the input. It should iterate in reverse: "
                    "range(len(s) - 1, -1, -1)."
                ),
            }
        ],
    },
    {
        "id": "medium_003",
        "difficulty": "medium",
        "language": "python",
        "description": (
            "Review this FizzBuzz implementation. It should print 'Fizz' for multiples "
            "of 3, 'Buzz' for multiples of 5, and 'FizzBuzz' for both."
        ),
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
        "bugs": [
            {
                "line": 7,
                "type": "logical_bug",
                "description": (
                    "The FizzBuzz condition (i % 15 == 0) will never be reached because "
                    "it is checked after the Fizz (i % 3 == 0) and Buzz (i % 5 == 0) "
                    "conditions. It should be checked first."
                ),
            }
        ],
    },
    {
        "id": "medium_004",
        "difficulty": "medium",
        "language": "python",
        "description": (
            "Review this function that counts the number of vowels in a string."
        ),
        "code": """\
def count_vowels(s):
    vowels = "aeiou"
    count = 0
    for char in s:
        if char in vowels:
            count =+ 1
    return count
""",
        "bugs": [
            {
                "line": 6,
                "type": "logical_bug",
                "description": (
                    "'count =+ 1' is an assignment (count = +1), not an increment. "
                    "It should be 'count += 1'."
                ),
            }
        ],
    },
]
