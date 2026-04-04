from .easy import EASY_TASKS
from .medium import MEDIUM_TASKS
from .hard import HARD_TASKS

ALL_TASKS = {
    "easy": EASY_TASKS,
    "medium": MEDIUM_TASKS,
    "hard": HARD_TASKS,
}

__all__ = ["ALL_TASKS", "EASY_TASKS", "MEDIUM_TASKS", "HARD_TASKS"]
