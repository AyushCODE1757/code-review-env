from typing import List, Dict, Any

def reward_handler(outcome) -> float :
    if outcome == "correct_flag":
        return 1.0

    elif outcome == "duplicate_flag":
        return -0.2

    elif outcome == "wrong_flag":
        return -0.5

    elif outcome == "valid_fix":
        return 0.5

    elif outcome == "invalid_fix":
        return -0.3
    elif outcome == "duplicate_fix":
        return -0.2
    elif outcome== "wrong_fix":
        return -0.2
    elif outcome == "approve_success":
        return 1.0

    elif outcome == "approve_fail":
        return -1.0
    return 0.0
def calc_reward( outcome) -> float:
    return reward_handler( outcome) -0.4
    