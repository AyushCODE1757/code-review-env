import random
from .easy import  EASY_TASKS
from .medium import  MEDIUM_TASKS
from .hard import  HARD_TASKS

def get_task(difficulty="easy"):
    if difficulty == "easy":
        return random.choice(EASY_TASKS)
    elif difficulty == "medium":
        return random.choice(MEDIUM_TASKS)
    elif difficulty == "hard":
        return random.choice(HARD_TASKS)
    else:
        raise ValueError(f"Unknown difficulty: {difficulty}")