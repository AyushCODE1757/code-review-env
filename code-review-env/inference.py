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
import json
import re
import ast
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

For each response, output ONE action in the following structured JSON format:
{
  "action_type": "flag_bug",
  "description": "<short description of the bug>",
  "line": <line number>
}

Rules:
- Use "action_type": "flag_bug" when you find a specific bug.
- Use "action_type": "approve" only when you are confident the code is correct.
- Use "action_type": "request_changes" when you want changes but haven't identified specifics.
- Use "action_type": "comment" for non-bug observations.
- Be concise and precise.
"""


def build_user_message(state: dict) -> str:
    """Format the current observation into an LLM user message."""
    observation = {
        "code": state["Code"],
        "steps_remaining": state["max_no_of_steps"] - state["number_of_steps"],
        "found_bugs": state["found_bugs"]
    }
    return json.dumps(observation, indent=2)


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
    
    state = {
        "Code": task.get("code", ""),
        "bug": [
            {
                "line": task.get("line"),
                "type": task.get("type"),
                "description": task.get("description")
            }
        ] if "type" in task else task.get("bugs", []),
        "found_bugs": [],
        "number_of_steps": 0,
        "max_no_of_steps": 5,
        "done": False
    }
    env.MAX_STEPS = state["max_no_of_steps"]
    grader = Grader(max_steps=env.MAX_STEPS)

    obs = env.reset()
    state["Code"] = obs.code_snippet

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    false_positives = 0
    final_action = "request_changes"

    while not state["done"]:
        user_msg = build_user_message(state)
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
            print(f"\n[Step {state['number_of_steps'] + 1}] LLM Output:\n{raw_output}\n{'─'*60}")

        # ── Parse action ───────────────────────────────────────────────────────
        try:
            json_str = raw_output
            match = re.search(r'```(?:json)?\s*(.*?)\s*```', raw_output, re.DOTALL)
            if match:
                json_str = match.group(1)
            # Remove comments starting with #
            json_str = re.sub(r'#.*', '', json_str)
            try:
                parsed = json.loads(json_str)
            except json.JSONDecodeError:
                parsed = ast.literal_eval(json_str)
            if not isinstance(parsed, dict):
                parsed = {}
        except Exception:
            parsed = parse_llm_action(raw_output)

        action_type_raw = parsed.get("action_type", parsed.get("ACTION", "comment"))
        action_type = "identify_bug" if action_type_raw == "flag_bug" else action_type_raw

        # Validate action type
        valid_types = {t.value for t in ActionType}
        if action_type not in valid_types:
            action_type = "comment"

        action = Action(
            action_type=action_type,
            line_number=parsed.get("line"),
            comment=parsed.get("comment"),
            bug_description=parsed.get("description"),
            suggested_fix=parsed.get("suggested_fix"),
        )

        # Track false positives (simplified heuristic — refine per task)
        if action_type == "identify_bug" and action.line_number is None:
            false_positives += 1

        # ── Step environment ───────────────────────────────────────────────────
        obs = env.step(action)
        
        state["number_of_steps"] += 1
        state["found_bugs"] = obs.bugs_found
        state["done"] = obs.done

        if action_type in ("approve", "request_changes"):
            final_action = action_type

    # ── Grade ──────────────────────────────────────────────────────────────────
    result = grader.grade(
        task=task,
        bugs_found=state["found_bugs"],
        false_positives=false_positives,
        steps_taken=state["number_of_steps"],
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

    print(f"Running task: {task.get('taskid', task.get('id', 'unknown'))} ({task['difficulty']})")
    print(f"Model: {args.model}\n{'='*60}")

    run_episode(task=task, model=args.model, verbose=not args.quiet)


if __name__ == "__main__":
    main()
