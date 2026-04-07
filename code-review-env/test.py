from env.environment import CodeReviewEnv
from grader import Grader   # adjust path if needed
from tasks import get_task


def run_test():
    print("\n--- START TEST ---\n")

    # Initialize
    env = CodeReviewEnv()
    task = get_task("easy")

    obs = env.reset("easy")

    print("Initial Observation:")
    print(obs)
    print()

    done = False

    # --- Simulated agent actions ---
    actions = [
        {"type": "flag_bug", "line": 1, "description": "test bug"},
        {"type": "suggest_fix", "line": 1, "fix": "test fix"},
        {"type": "approve"}
    ]

    step_count = 0

    for action in actions:
        if done:
            break

        print(f"\nStep {step_count + 1}")
        print("Action:", action)

        obs, reward, done, info = env.step(action)

        print("Observation:", obs)
        print("Reward:", reward)
        print("Done:", done)
        print("Info:", info)

        step_count += 1

    print("\n--- ENVIRONMENT FINISHED ---\n")

    # --- Grading ---
    grader = Grader(max_steps=env.state["max_steps"])

    result = grader.grade(
        task=task,
        bugs_found=env.state["found_bugs"],
        steps_taken=env.state["steps_taken"],
        total_reward=env.total_reward,
        final_action="approve"
    )

    print("\n--- GRADE RESULT ---\n")
    print(result)


if __name__ == "__main__":
    run_test()