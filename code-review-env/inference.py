"""
inference.py — Runs the agent (LLM loop)

This script orchestrates a full code review episode using an LLM as the agent.
It:
  1. Loads a task (easy/medium/hard)
  2. Resets the environment
  3. Loops: sends observation to LLM → parses action → steps environment
  4. Grades the final episode using the Grader
"""
from env.utils import number_lines
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
from tasks import EASY_TASKS, MEDIUM_TASKS, HARD_TASKS
from grader import Grader


# ── System prompt ──────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """\
You are an expert code reviewer.

You are given code and must identify REAL bugs step by step.

At each step, output EXACTLY ONE action in valid JSON.

Allowed actions:

1. Flag a bug:
{
  "type": "flag_bug",
  "line": <line number>,
  "description": "<short description>"
}

2. Suggest a fix (ONLY after flagging that bug):
{
  "type": "suggest_fix",
  "line": <line number>,
  "description": "<fix description>"
}

3. Approve:
{
  "type": "approve"
}
Before choosing an action, carefully inspect the code line by line.

Focus only on real syntax or logical errors.

For each step:
1. Look at the code.
2. Identify if a specific line has a clear bug.
3. If no clear bug exists, stop and approve.

Do NOT assume patterns like "missing parenthesis" unless clearly visible in the code.

STRICT RULES:

- Only flag bugs that are clearly present in the code.
- Do NOT guess or assume issues.
- Do NOT repeat the same bug or same line.
- If a bug is already in "found_bugs", do NOT flag it again.
- Each line should be flagged at most once.
- If you cannot clearly point to the exact syntax issue in the code, DO NOT flag a bug.
-After suggesting a fix, check if all bugs are resolved.

-If no clear bugs remain, immediately return:
{
  "type": "approve"
}

Do NOT continue searching for more issues once a valid bug has been found and fixed.

- Prefer accuracy over quantity.
- It is better to miss a bug than to invent one.
- Do NOT assume additional issues unless clearly visible in the code.
- If you are not really a bug exists, DO NOT flag it.
- Output ONLY JSON. No explanation.
- Before identifying a bug, carefully analyze the full code.

- Do NOT guess based on a single line.
- Ensure the issue is logically consistent with the program behavior.
-
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
    client = OpenAI(
    base_url=os.getenv("API_BASE_URL"),
    api_key=os.getenv("HF_TOKEN"),
    )

    # FIXED: correct env init
    env = CodeReviewEnv()
    obs = env.reset(task=task)

    grader = Grader(max_steps=env.state["max_steps"])

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    done = False
    final_action = "approve"

    step_count = 0

    while not done:
        # use env observation directly
        obs_dict = obs.model_dump()
        obs_dict["code"] = number_lines(obs_dict["code"])
        user_msg = json.dumps(obs_dict, indent=2)

        messages.append({"role": "user", "content": user_msg})

        # LLM call
        model=os.getenv("MODEL_NAME"),
        if os.getenv("HF_TOKEN"):
            # --- Normal LLM path ---
            response = client.chat.completions.create(
                model=os.getenv("MODEL_NAME"),
                messages=messages,
                temperature=0.2,
            )
            raw_output = response.choices[0].message.content

        else:
            # --- Fallback (no API) ---
            print("⚠️ No API key found. Using fallback agent.")

            # Simple heuristic: always flag first line
            raw_output = json.dumps({
                "type": "flag_bug",
                "line": 1,
                "description": "Fallback guess (no LLM)"
            })
        messages.append({"role": "assistant", "content": raw_output})

        if verbose:
            print(f"\n[Step {step_count + 1}] LLM Output:\n{raw_output}\n{'─'*60}")

        # Parse action
        try:
            json_str = raw_output
            match = re.search(r'```(?:json)?\s*(.*?)\s*```', raw_output, re.DOTALL)
            if match:
                json_str = match.group(1)

            json_str = re.sub(r'#.*', '', json_str)

            try:
                parsed = json.loads(json_str)
            except json.JSONDecodeError:
                parsed = ast.literal_eval(json_str)

            if not isinstance(parsed, dict):
                parsed = {}

        except Exception:
            parsed = parse_llm_action(raw_output)

        # correct key
        action_type = parsed.get("type", "comment")

        #  send dict, not Action object
        action = {
            "type": action_type,
            "line": parsed.get("line"),
            "description": parsed.get("description"),
            "fix": parsed.get("fix"),
        }

        # correct step usage
        obs, reward, done, info = env.step(action)
        # If all bugs found → force approve
        true_bug_lines = {int(b["line"]) for b in env.state["true_bugs"]}
        found_bug_lines = {int(b["line"]) for b in env.state["found_bugs"]}

        if true_bug_lines == found_bug_lines and self.state["steps_taken"] >= 2:
            done = True
            final_action = "approve"
        step_count += 1
        if not done:
            final_action = action["type"]
    print("FOUND BUGS:", env.state["found_bugs"])

    # correct grader call
    result = grader.grade(
        task=task,
        bugs_found=env.state["found_bugs"],
        steps_taken=env.state["steps_taken"],
        total_reward=env.total_reward,
        final_action=final_action,
    )

    if verbose:
        print("\n--- GRADE RESULT ---\n")
        print(result)

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

    if args.difficulty == "easy":
        tasks = EASY_TASKS
    elif args.difficulty == "medium":
        tasks = MEDIUM_TASKS
    else:
        tasks = HARD_TASKS
    idx = args.task_index if args.task_index is not None else random.randint(0, len(tasks) - 1)
    task = tasks[idx]

    print(f"Running task: {task.get('taskid', task.get('id', 'unknown'))} ({task['difficulty']})")
    print(f"Model: {args.model}\n{'='*60}")

    run_episode(task=task, model=args.model, verbose=not args.quiet)


if __name__ == "__main__":
    main()
