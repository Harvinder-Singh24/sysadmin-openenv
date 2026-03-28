import os
import random
import subprocess
import signal

class BaseTask:
    def __init__(self, task_id, description, difficulty):
        self.task_id = task_id
        self.description = description
        self.difficulty = difficulty

    def setup(self, workspace: str):
        pass

    def evaluate(self, command: str, stdout: str, stderr: str, workspace: str) -> tuple[float, bool]:
        """Returns (reward, done)"""
        return 0.0, False

class EasyTask(BaseTask):
    def __init__(self):
        super().__init__(
            "easy_log_analysis", 
            "Parse auth.log to find the IP address of a user who failed to login. Use exactly 'submit <IP>' to answer.", 
            "easy"
        )
        self.target_ip = "192.168.1.105"

    def setup(self, workspace: str):
        os.makedirs(os.path.join(workspace, "var", "log"), exist_ok=True)
        log_path = os.path.join(workspace, "var", "log", "auth.log")
        with open(log_path, "w") as f:
            f.write("Mar 28 10:00:01 server sshd[1234]: Accepted publickey for user\\n")
            f.write(f"Mar 28 10:05:22 server sshd[1235]: Failed password for invalid user admin from {self.target_ip} port 54322 ssh2\\n")
            f.write(f"Mar 28 10:05:25 server sshd[1235]: Failed password for invalid user admin from {self.target_ip} port 54322 ssh2\\n")
            f.write(f"Mar 28 10:05:28 server sshd[1235]: Failed password for invalid user admin from {self.target_ip} port 54322 ssh2\\n")
            f.write(f"Mar 28 10:06:01 server sshd[1236]: Disconnected from {self.target_ip}\\n")

    def evaluate(self, command: str, stdout: str, stderr: str, workspace: str) -> tuple[float, bool]:
        if command.startswith("submit "):
            ip = command.split(" ")[1].strip()
            if ip == self.target_ip:
                return 1.0, True
            else:
                return 0.0, True # Done, but failed
                
        parts = command.split()
        if len(parts) > 0 and parts[0] in ["cat", "grep", "less", "tail", "head"]:
            if "auth.log" in command:
                return 0.2, False
                
        return 0.0, False

class MediumTask(BaseTask):
    def __init__(self):
        super().__init__(
            "med_config_fix", 
            "Identify the misconfigured web server port in ./app/config/server.conf. It should be 8080. Fix it in the file and run 'systemctl restart webserver'.", 
            "medium"
        )
        
    def setup(self, workspace: str):
        os.makedirs(os.path.join(workspace, "app", "config"), exist_ok=True)
        conf_path = os.path.join(workspace, "app", "config", "server.conf")
        with open(conf_path, "w") as f:
            f.write("server {\\n")
            f.write("    listen 9090;\\n")
            f.write("    server_name localhost;\\n")
            f.write("}\\n")
            
    def evaluate(self, command: str, stdout: str, stderr: str, workspace: str) -> tuple[float, bool]:
        if "systemctl restart webserver" in command:
            conf_path = os.path.join(workspace, "app", "config", "server.conf")
            try:
                with open(conf_path, "r") as f:
                    content = f.read()
                    if "listen 8080;" in content:
                        return 1.0, True
            except:
                pass
            return 0.0, True
            
        parts = command.split()
        if len(parts) > 0 and parts[0] in ["cat", "nano", "vim", "vi", "less"]:
            if "server.conf" in command:
                return 0.2, False
                
        return 0.0, False

class HardTask(BaseTask):
    def __init__(self):
        super().__init__(
            "hard_cpu_hog", 
            "There is an unauthorized process named 'evil_miner.sh' running in the background. Find its PID and kill it. Then run 'submit done'. Note: The process is mocked with sleep.", 
            "hard"
        )
        self.pid = None

    def setup(self, workspace: str):
        hog_script = os.path.join(workspace, "evil_miner.sh")
        with open(hog_script, "w") as f:
            f.write("#!/bin/bash\\nsleep 3600\\n")
        os.chmod(hog_script, 0o777)
        # Start the script
        p = subprocess.Popen(["bash", hog_script])
        self.pid = p.pid

    def evaluate(self, command: str, stdout: str, stderr: str, workspace: str) -> tuple[float, bool]:
        if command.strip() == "submit done":
            if self.pid is None:
                return 0.0, True
            try:
                # If kill 0 succeeds, the process is still running
                os.kill(self.pid, 0)
                # Cleanup manually
                os.kill(self.pid, signal.SIGKILL)
                return 0.0, True
            except OSError:
                # Process is not running anymore
                return 1.0, True
                
        parts = command.split()
        if len(parts) > 0 and parts[0] in ["ps", "top", "htop", "pgrep"]:
            return 0.2, False
            
        return 0.0, False

TASK_CLASSES = [EasyTask, MediumTask, HardTask]

def get_task():
    return random.choice(TASK_CLASSES)()
