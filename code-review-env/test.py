from env.environment import CodeReviewEnv
from grader import Grader


def run_test(task):
    env = CodeReviewEnv()

    obs = env.reset(task=task)
    max_steps = env.state["max_steps"]  # ✅ source of truth
    grader = Grader(max_steps=max_steps)

    print("\n--- START TEST ---")
    print("Initial Observation:", obs)

    total_reward = 0

    # ---- Step 1: correct bug ----
    bug = task["bugs"][0]
    action = {
        "type": "flag_bug",
        "line": 999,
        "description": "fake bug"
    }

    obs, reward, done, info = env.step(action)
    total_reward += reward

    print("\nStep 1:", action)
    print("Reward:", reward, "Done:", done)

    # ---- Step 2: approve ----
    action = {"type": "approve"}

    obs, reward, done, info = env.step(action)
    total_reward += reward

    print("\nStep 2:", action)
    print("Reward:", reward, "Done:", done)

    # ---- Grade ----
    result = grader.grade(
        task=task,
        bugs_found=env.state["found_bugs"],
        steps_taken=env.state["steps_taken"],
        total_reward=total_reward,
        final_action="approve",
    )

    print("\n--- RESULT ---")
    print(result)


if __name__ == "__main__":
    from tasks.easy import EASY_TASKS
    from tasks.medium import MEDIUM_TASKS
    from tasks.hard import HARD_TASKS

    print("\n===== EASY TEST =====")
    run_test(EASY_TASKS[0])

    print("\n===== MEDIUM TEST =====")
    run_test(MEDIUM_TASKS[0])

    print("\n===== HARD TEST =====")
    run_test(HARD_TASKS[0])