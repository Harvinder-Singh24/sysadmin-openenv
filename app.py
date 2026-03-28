from fastapi import FastAPI
from environment import SysAdminEnvironment
from models import Action, Observation, State
import os

app = FastAPI()
env = SysAdminEnvironment()
env.reset()

@app.post("/reset", response_model=Observation)
async def reset():
    return env.reset()

@app.post("/step", response_model=Observation)
async def step(action: Action):
    return env.step(action)

@app.get("/state", response_model=State)
async def state_get():
    return env.state_dict()

@app.post("/state", response_model=State)
async def state_post():
    return env.state_dict()
