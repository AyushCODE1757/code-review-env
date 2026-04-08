from fastapi import FastAPI
from pydantic import BaseModel
from env import CodeReviewEnv

app = FastAPI()
env = CodeReviewEnv()

class ActionInput(BaseModel):
    type: str
    line: int | None = None
    description: str | None = None
    fix: str | None = None

@app.post("/reset")
def reset():
    obs = env.reset()
    return obs.model_dump()

@app.post("/step")
def step(action: ActionInput):
    obs, reward, done, info = env.step(action.model_dump())
    return {
        "observation": obs.model_dump(),
        "reward": reward,
        "done": done,
        "info": info
    }

@app.get("/")
def root():
    return {"status": "ok"}