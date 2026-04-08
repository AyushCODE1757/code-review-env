from fastapi import FastAPI
from pydantic import BaseModel
import random

from env import CodeReviewEnv
from tasks import EASY_TASKS, MEDIUM_TASKS, HARD_TASKS

app = FastAPI()
env = CodeReviewEnv()


class ActionInput(BaseModel):
    type: str
    line: int | None = None
    description: str | None = None
    fix: str | None = None


@app.post("/reset")
def reset():
    # pick a random task (important)
    task = random.choice(EASY_TASKS + MEDIUM_TASKS + HARD_TASKS)

    obs = env.reset(task=task)
    return obs.dict()


@app.post("/step")
def step(action: ActionInput):
    # safety check
    if not hasattr(env, "state") or "true_bugs" not in env.state:
        return {"error": "Call /reset first"}

    obs, reward, done, info = env.step(action.dict())

    return {
        "observation": obs.dict(),
        "reward": reward,
        "done": done,
        "info": info
    }


@app.get("/state")
def state():
    return env.state


@app.get("/")
def root():
    return {"status": "ok"}