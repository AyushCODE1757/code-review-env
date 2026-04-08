# 🔍 Code Review RL Environment

An **OpenEnv-compatible reinforcement learning environment** for training and evaluating LLM agents on code review tasks. The agent reads code, identifies bugs, suggests fixes, and receives rewards based on accuracy, efficiency, and decision quality.

---

## 📁 Project Structure

```
code-review-env/
│
├── env/
│   ├── __init__.py
│   ├── environment.py      # Core environment (reset / step / state)
│   ├── models.py           # Pydantic models (Action, Observation)
│   ├── rewards.py          # Reward logic
│   └── utils.py            # number_lines(), parse_llm_action(), helpers
│
├── tasks/
│   ├── __init__.py
│   ├── easy.py             # EASY_TASKS   — syntax error tasks
│   ├── medium.py           # MEDIUM_TASKS — logical bug tasks
│   └── hard.py             # HARD_TASKS   — performance issue tasks
│
├── grader/
│   ├── __init__.py
│   └── grader.py           # Grader — final 0–100 episode scoring
│
├── tests/                  # pytest test suite
│   ├── conftest.py         # Shared test fixtures
│   ├── test_environment.py # Environment lifecycle tests
│   ├── test_grader.py      # Scoring logic tests
│   ├── test_rewards.py     # Reward calculation tests
│   ├── test_tasks.py       # Task loading tests
│   └── test_utils.py       # Helper function tests                 # pytest test suite
│
├── inference.py            # LLM agent loop (main entry point)
├── test.py                 # Quick manual test runner (no pytest needed)
├── openenv.yaml            # OpenEnv specification config
├── requirements.txt
├── Dockerfile
└── __init__.py
```

---

## 🚀 Quickstart

### 1. Prerequisites

- Python 3.9+
- API Access: A valid API key for OpenAI, Anthropic, or Google Gemini

### 2. Virtual Environment (Windows)

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set environment variables
(windows)

```bash
set HF_TOKEN=your-token-here
set API_BASE_URL=https://api.openai.com/v1
set MODEL_NAME=gpt-4o
```

### 5. Run the agent

```bash
# Easy task (syntax errors)
python inference.py --difficulty easy

# Medium task (logical bugs)
python inference.py --difficulty medium

# Hard task (performance issues)
python inference.py --difficulty hard

# Specific task index + model
python inference.py --difficulty hard --task-index 2 --model gpt-4o

# Suppress step-by-step output
python inference.py --difficulty easy --quiet
```

---

## 🐳 Docker

```bash
# Build
docker build -t code-review-env .

# Run
docker run \
  -e HF_TOKEN="your-token-here" \
  -e API_BASE_URL="https://api.openai.com/v1" \
  -e MODEL_NAME="gpt-4o" \
  code-review-env --difficulty medium
```

---

## 🏗️ Architecture

### How an episode works

```
inference.py
    │
    ├── loads task (easy / medium / hard)
    ├── env.reset(task)  →  initial Observation
    │
    └── loop:
          Observation → LLM → raw JSON output
                             → parse_llm_action()
                             → env.step(action)
                             → reward, done, info
          (repeat until done or max_steps reached)
    │
    └── Grader.grade(...)  →  final 0–100 score
```

### Environment (`env/`)

| File | Purpose |
|------|---------|
| `environment.py` | `CodeReviewEnv` with `reset()` and `step()` |
| `models.py` | Pydantic `Action` and `Observation` models |
| `rewards.py` | Per-step reward computation |
| `utils.py` | `number_lines()`, `parse_llm_action()`, helpers |

### Tasks (`tasks/`)

| File | Difficulty | Bug Type |
|------|-----------|----------|
| `easy.py` | ⭐ Easy | Syntax errors (missing colons, `=` vs `==`, bad indentation) |
| `medium.py` | ⭐⭐ Medium | Logical bugs (off-by-one, wrong operator, wrong return) |
| `hard.py` | ⭐⭐⭐ Hard | Performance issues (O(n²) loops, memory leaks, recursion) |

### Grader (`grader/`)

Produces a **0–100 score** using weighted sub-scores:

| Dimension | Weight |
|-----------|--------|
| Bug Detection Rate | 50% |
| False Positive Penalty | 20% |
| Efficiency (steps taken) | 20% |
| Decision Quality (`approve` vs `request_changes`) | 10% |

---

## 🎁 Reward Structure

Defined in `openenv.yaml` and applied in `env/rewards.py`:

| Event | Reward |
|-------|--------|
| Correct bug flagged | `+1.0` |
| Correct fix suggested | `+0.5` bonus |
| Wrong bug flagged | `−0.3` |
| Missed bug (at episode end) | `−0.5` |
| Approved clean code | `+0.5` |
| False positive on clean code | `−0.4` |
| Per step penalty | `−0.01` |

---

## 🤖 Agent Actions

### 🔍 Agent Observations

At each step, the environment provides a JSON observation containing the code to be reviewed:

```json
{
  "code": "1: def calculate(a, b):\n2:    return a + b", 
  "task_id": "easy_01",
  "history": [] 
}
```

The LLM outputs **one JSON action per step**:

```json
// Flag a bug
{ "type": "flag_bug", "line": 5, "description": "Variable used before assignment" }

// Suggest a fix (only after flagging that bug)
{ "type": "suggest_fix", "line": 5, "description": "Initialise x = 0 before the loop" }

// Approve — no bugs remain
{ "type": "approve" }
```

The episode ends when the agent approves, all true bugs are found, or `max_steps` (10) is reached.

---

## 🤖 Supported Models

Configured via the `MODEL_NAME` environment variable:

| Model | Provider |
|-------|----------|
| `gpt-4o` *(default)* | OpenAI |
| `gpt-4-turbo` | OpenAI |
| `claude-3-5-sonnet` | Anthropic |
| `gemini-1.5-pro` | Google |

> The client uses `API_BASE_URL` + `HF_TOKEN`, making it compatible with OpenAI, HuggingFace Inference, or any OpenAI-compatible endpoint.

---

## 🧪 Testing

### Quick manual test (no pytest needed)

```bash
python test.py
```

Runs one episode each for Easy, Medium, and Hard tasks and prints rewards + final grades.

### Full test suite

```bash
pytest tests/ -v --cov=env --cov=grader
```

---

## ⚙️ Configuration (`openenv.yaml`)

```yaml
environment:
  entry_point: env.environment:CodeReviewEnv
  max_steps: 10
  action_space:
    - flag_bug
    - suggest_fix
    - approve

rewards:
  correct_bug_found: 1.0
  wrong_bug_flagged: -0.3
  missed_bug_penalty: -0.5
  correct_fix_bonus: 0.5
  approve_clean_code: 0.5
  false_positive_penalty: -0.4
  step_penalty: -0.01

grader:
  weights:
    bug_detection: 0.5
    false_positive: 0.2
    efficiency: 0.2
    decision_quality: 0.1
```

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.
