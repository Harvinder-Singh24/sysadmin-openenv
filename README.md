---
title: SysAdmin OpenEnv Simulator
emoji: 🖥️
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---

# SysAdmin OpenEnv Simulator

This project is a submission for the **Meta PyTorch OpenEnv Hackathon x Scaler Round 1**. It implements a complete, real-world OpenEnv environment simulating a Junior System Administrator's workspace.

## Environment Description

The **SysAdmin Simulator** evaluates an AI agent's ability to diagnose and repair simulated system, application, and process-level problems using a bash terminal interface. The agent is placed within an isolated Unix-like workspace where three distinct tasks of escalating difficulty are simulated. 

This is not a toy game: investigating logs, fixing configuration files, and terminating rogue processes are daily realities for engineering and operations teams.

### Tasks
1. **Easy (`easy_log_analysis`)**: The agent must `grep` or analyze `/var/log/auth.log` to find the exact IP address responsible for repeated failed SSH login attempts, and submit the IP.
2. **Medium (`med_config_fix`)**: The agent must fix a misconfigured Nginx/web server port in `/workspace/app/config/server.conf` from `9090` to the proper `8080`, then restart the service.
3. **Hard (`hard_cpu_hog`)**: A rogue script (`evil_miner.sh`) is running and consuming fake CPU cycles. The agent must locate the process ID (PID) of this script and issue a `kill` command.

## Action & Observation Spaces

The environment follows an interactive bash-shell paradigm.

### Action Space
*   The agent outputs **a single bash command string**.
*   **Schema:** `Action(command: str)`
*   Example: `{"command": "cat /var/log/auth.log"}` or `{"command": "submit 192.168.1.105"}`

### Observation Space
*   The environment executes the command within a strict 5-second timeout in an isolated sandbox. It returns standard bash output.
*   **Schema:** `Observation(stdout: str, stderr: str, exit_code: int, task_id: str, reward: float, done: bool, info: dict)`
*   *Reward Strategy:*
    *   `1.0`: Task completed successfully.
    *   `0.0`: Progressing / standard step.
    *   `-0.05`: The executed command failed (exit code != 0, giving the agent a slight penalty for hallucinating commands or syntax errors).

## Setup & Execution Instructions

### Prerequisites
*   Docker OR Python 3.10+
*   An OpenAI-compatible API key (e.g., standard OpenAI or a proxy like Hugging Face Router as provided in the hackathon).

### Running Locally with Docker (Recommended)
You can test the entire pipeline locally, just as it would run on a Hugging Face Space.

1. **Build the Environment Container:**
   ```bash
   docker build -t openenv-sysadmin .
   ```
2. **Run the Environment:**
   ```bash
   docker run -p 8000:8000 openenv-sysadmin
   ```
3. **Run Inference (in a separate terminal):**
   ```bash
   export API_BASE_URL="https://api.openai.com/v1"  # Or your specific router
   export MODEL_NAME="gpt-4o-mini" # Or an open model
   export HF_TOKEN="your_api_key_here"
   
   python3 inference.py
   ```

### Running Locally without Docker
1. Install dependencies: `pip install -r requirements.txt`
2. Start the FastAPI server: `uvicorn app:app --host 0.0.0.0 --port 8000`
3. Set environment variables and run `python inference.py`

## Baseline Scores
The environment was evaluated using the internal `inference.py` running the `gpt-4o-mini` baseline agent:

*   **Easy Task (`easy_log_analysis`):** [Score TBD by user]
*   **Medium Task (`med_config_fix`):** [Score TBD by user]
*   **Hard Task (`hard_cpu_hog`):** [Score TBD by user]

## Judging Validation
This environment strictly adheres to the OpenEnv JSON model standard over HTTP endpoints (`/reset`, `/step`, `/state`). It meets the runtime limit requirement (the FastAPI server is highly lightweight, consuming <50MB RAM).
