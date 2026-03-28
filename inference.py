import os
import requests
import re
import time
from openai import OpenAI

API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
API_KEY = os.getenv("HF_TOKEN") or os.getenv("API_KEY", "dummy_key")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")

class OpenEnvClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def reset(self):
        r = requests.post(f"{self.base_url}/reset")
        r.raise_for_status()
        return r.json()
    
    def step(self, command):
        r = requests.post(f"{self.base_url}/step", json={"command": command})
        r.raise_for_status()
        return r.json()
    
    def state(self):
        r = requests.get(f"{self.base_url}/state")
        r.raise_for_status()
        return r.json()

def main():
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
    env = OpenEnvClient("http://localhost:7860")
    
    completed_tasks = {}
    target_tasks = 3
    
    # Wait for server to be ready
    for _ in range(5):
        try:
            env.reset()
            break
        except requests.ConnectionError:
            print("Waiting for server to start...")
            time.sleep(1)
            
    while len(completed_tasks) < target_tasks:
        obs = env.reset()
        task_id = obs.get("task_id")
        
        if task_id in completed_tasks:
            continue
            
        print(f"\n======================================")
        print(f"Starting Task: {task_id}")
        print(f"======================================")
        print(f"Initial Observation:\n{obs['stdout']}")
        
        history = [{"role": "system", "content": "You are an AI sysadmin. Reply with EXACTLY one terminal command. Do not use markdown backticks for the answer. If you are asked to 'submit <something>', physically output 'submit <something>'."}]
        history.append({"role": "user", "content": obs["stdout"]})
        
        task_reward = 0.0
        
        for step in range(15):
            try:
                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=history,
                    temperature=0.2,
                    max_tokens=100
                )
                command = response.choices[0].message.content.strip()
            except Exception as e:
                print(f"LLM API Error: {e}")
                break
                
            command = re.sub(r'```(?:bash)?\\n(.*?)\\n```', r'\\1', command, flags=re.DOTALL)
            command = command.split('\\n')[0].strip()
            
            print(f"\n[Step {step+1}] Executing: {command}")
            history.append({"role": "assistant", "content": command})
            
            obs = env.step(command)
            step_reward = obs['reward']
            task_reward += step_reward
            
            print(f"Result (code={obs['exit_code']}, reward={step_reward}, done={obs['done']}):\n{obs['stdout']} {obs['stderr']}")
            
            history.append({
                "role": "user", 
                "content": f"Exit Code: {obs['exit_code']}\nStdout:\n{obs['stdout']}\nStderr:\n{obs['stderr']}"
            })
            
            if obs["done"]:
                print(f"\nTask finished.")
                break
                
        # Cap reward to [0.0, 1.0]
        final_score = max(0.0, min(1.0, task_reward))
        completed_tasks[task_id] = final_score
        print(f"--> Final Score for {task_id}: {final_score}")
        
    print("\n" + "="*40)
    print("BASELINE EVALUATION SUMMARY")
    print("="*40)
    for t_id, score in completed_tasks.items():
        print(f"Task: {t_id:<20} | Score: {score:.2f}")
    print("="*40)

if __name__ == "__main__":
    main()
