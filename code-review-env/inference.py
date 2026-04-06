"""
inference.py — Runs the agent (LLM loop)

This script orchestrates a full code review episode using an LLM as the agent.
It:
  1. Loads a task (easy/medium/hard)
  2. Resets the environment
  3. Loops: sends observation to LLM → parses action → steps environment
  4. Grades the final episode using the Grader
"""

import os
import argparse
import random
from openai import OpenAI  # or swap with any LLM client

from env import CodeReviewEnv
from env.models import Action, ActionType
from env.utils import parse_llm_action
from tasks import ALL_TASKS
from grader import Grader


# ── System prompt ──────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """\
You are an expert code reviewer. Your job is to carefully read the provided code
and identify bugs, logical errors, or performance issues.

For each response, output ONE action in the following structured format:

ACTION: <identify_bug | comment | approve | request_changes>
LINE: <line number, if applicable>
BUG_DESCRIPTION: <short description of the bug>
SUGGESTED_FIX: <suggested fix or improvement>
COMMENT: <any additional comment>

Rules:
- Use ACTION: identify_bug when you find a specific bug.
- Use ACTION: approve only when you are confident the code is correct.
- Use ACTION: request_changes when you want changes but haven't identified specifics.
- Use ACTION: comment for non-bug observations.
- Be concise and precise.
"""


def build_user_message(obs) -> str:
    """Format the current observation into an LLM user message."""
    return f"""\
Task: {obs.task_description}
Language: {obs.language}
Step: {obs.step}

Code:
{obs.code_snippet}

Bugs identified so far: {obs.bugs_found if obs.bugs_found else "None"}

What is your next review action?
"""


def run_episode(task: dict, model: str = "gpt-4o", verbose: bool = True):
    """
    Run a single code review episode with an LLM agent.

    Args:
        task: Task dictionary (from tasks/easy.py, medium.py, or hard.py).
        model: OpenAI model to use.
        verbose: Whether to print step-by-step output.
    """
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    env = CodeReviewEnv(task)
    grader = Grader(max_steps=env.MAX_STEPS)

    obs = env.reset()
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    false_positives = 0
    final_action = "request_changes"
    step = 0

    while not obs.done:
        user_msg = build_user_message(obs)
        messages.append({"role": "user", "content": user_msg})

        # ── LLM call ───────────────────────────────────────────────────────────
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.2,
        )
        raw_output = response.choices[0].message.content
        messages.append({"role": "assistant", "content": raw_output})

        if verbose:
            print(f"\n[Step {step + 1}] LLM Output:\n{raw_output}\n{'─'*60}")

        # ── Parse action ───────────────────────────────────────────────────────
        parsed = parse_llm_action(raw_output)
        action_type = parsed.get("action_type", "comment")

        # Validate action type
        valid_types = {t.value for t in ActionType}
        if action_type not in valid_types:
            action_type = "comment"

        action = Action(
            action_type=action_type,
            line_number=parsed.get("line_number"),
            comment=parsed.get("comment"),
            bug_description=parsed.get("bug_description"),
            suggested_fix=parsed.get("suggested_fix"),
        )

        # Track false positives (simplified heuristic — refine per task)
        if action_type == "identify_bug" and action.line_number is None:
            false_positives += 1

        # ── Step environment ───────────────────────────────────────────────────
        obs = env.step(action)

        if action_type in ("approve", "request_changes"):
            final_action = action_type

        step += 1

    # ── Grade ──────────────────────────────────────────────────────────────────
    result = grader.grade(
        task=task,
        bugs_found=obs.bugs_found,
        false_positives=false_positives,
        steps_taken=step,
        total_reward=env.total_reward,
        final_action=final_action,
    )

    if verbose:
        print("\n" + grader.summary(result))

    return result


def main():
    parser = argparse.ArgumentParser(description="Code Review RL Environment — Inference")
    parser.add_argument(
        "--difficulty",
        choices=["easy", "medium", "hard"],
        default="easy",
        help="Task difficulty level",
    )
    parser.add_argument(
        "--task-index",
        type=int,
        default=None,
        help="Index of the task to run (random if not specified)",
    )
    parser.add_argument(
        "--model",
        default="gpt-4o",
        help="OpenAI model to use",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress step-by-step output",
    )
    args = parser.parse_args()

    tasks = ALL_TASKS[args.difficulty]
    idx = args.task_index if args.task_index is not None else random.randint(0, len(tasks) - 1)
    task = tasks[idx]

    print(f"Running task: {task['id']} ({task['difficulty']})")
    print(f"Model: {args.model}\n{'='*60}")

    run_episode(task=task, model=args.model, verbose=not args.quiet)


if __name__ == "__main__":
    main()
