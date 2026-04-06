# 🔍 Code Review RL Environment

An **OpenEnv-compatible reinforcement learning environment** for training and evaluating LLM agents on code review tasks. The agent reads code, identifies bugs, leaves comments, and receives rewards based on accuracy, precision, and efficiency.

---

## 📁 Project Structure

```
code-review-env/
│
├── env/
│   ├── __init__.py
│   ├── environment.py      # Core environment (step/reset/state)
│   ├── models.py           # Pydantic models (Action, Observation)
│   ├── rewards.py          # Reward logic
│   └── utils.py            # Helper functions
│
├── tasks/
│   ├── __init__.py
│   ├── easy.py             # Syntax error tasks
│   ├── medium.py           # Logical bug tasks
│   └── hard.py             # Performance issue tasks
│
├── grader/
│   ├── __init__.py
│   └── grader.py           # Final scoring logic
│
├── inference.py            # Runs the agent (LLM loop)
├── openenv.yaml            # OpenEnv config
├── requirements.txt
├── Dockerfile
└── README.md
```

---

## 🚀 Quickstart

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Set your API key

```bash
export OPENAI_API_KEY="sk-..."
```

### 3. Run the agent

```bash
# Easy task (syntax errors)
python inference.py --difficulty easy

# Medium task (logical bugs)
python inference.py --difficulty medium

# Hard task (performance issues)
python inference.py --difficulty hard

# Specific task index + model
python inference.py --difficulty hard --task-index 2 --model gpt-4o
```

---

## 🐳 Docker

```bash
# Build the image
docker build -t code-review-env .

# Run with your API key
docker run -e OPENAI_API_KEY="sk-..." code-review-env --difficulty medium
```

---

## 🏗️ Architecture

### Environment (`env/`)

| File | Purpose |
|------|---------|
| `environment.py` | Core `CodeReviewEnv` class with `reset()` and `step()` |
| `models.py` | Pydantic `Action` and `Observation` models |
| `rewards.py` | `RewardCalculator` — per-step and final rewards |
| `utils.py` | Utilities: line numbering, diff generation, LLM output parsing |

### Tasks (`tasks/`)

| File | Difficulty | Bug Type |
|------|-----------|----------|
| `easy.py` | ⭐ Easy | Syntax errors (missing colons, parens, `=` vs `==`) |
| `medium.py` | ⭐⭐ Medium | Logical bugs (off-by-one, wrong operator, wrong order) |
| `hard.py` | ⭐⭐⭐ Hard | Performance issues (O(n²) loops, memory leaks, recursion) |

### Grader (`grader/`)

The `Grader` computes a **0–100 score** using weighted sub-scores:

| Dimension | Weight |
|-----------|--------|
| Bug Detection Rate | 50% |
| False Positive Penalty | 20% |
| Efficiency (steps taken) | 20% |
| Decision Quality (approve vs. request_changes) | 10% |

---

## 🎁 Reward Structure

| Event | Reward |
|-------|--------|
| Correct bug identified | `+1.0` |
| Bug fix suggested | `+0.5` bonus |
| Wrong bug flagged | `-0.3` |
| Missed bug (at episode end) | `-0.5` |
| Approved clean code | `+0.5` |
| False positive on clean code | `-0.4` |
| Per step penalty | `-0.01` |

---

## 🤖 Supported Models

- `gpt-4o` (default)
- `gpt-4-turbo`
- `claude-3-5-sonnet` (via `anthropic`)
- `gemini-1.5-pro` (via `google-generativeai`)

---

## 🧪 Testing

```bash
pytest tests/ -v --cov=env --cov=grader
```

---

## ⚙️ Configuration

All environment parameters are defined in `openenv.yaml`:

```yaml
environment:
  max_steps: 10
  action_space: [identify_bug, comment, approve, request_changes]
```

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.
