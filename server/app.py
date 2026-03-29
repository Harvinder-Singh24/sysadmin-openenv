import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi import FastAPI
from environment import SysAdminEnvironment
from models import Action, Observation, State

app = FastAPI()
env = SysAdminEnvironment()
env.reset()

@app.get("/")
async def root():
    return {"status": "ok", "message": "SysAdmin Simulator OpenEnv API is running. Endpoints: /reset, /step, /state"}

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

def main():
    import uvicorn
    uvicorn.run("server.app:app", host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()
