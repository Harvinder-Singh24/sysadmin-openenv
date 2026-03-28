import os
import subprocess
import shutil
from models import Action as SysAction, Observation as SysObservation, State as SysState
from tasks import get_task, BaseTask

class SysAdminEnvironment:
    def __init__(self):
        self.current_task: BaseTask = None
        self.step_count = 0
        self.workspace = os.path.abspath(os.path.join(os.path.dirname(__file__), "workspace"))
        os.makedirs(self.workspace, exist_ok=True)
    
    def reset(self) -> SysObservation:
        if self.current_task is not None and hasattr(self.current_task, "cleanup"):
            self.current_task.cleanup()
            
        self.current_task = get_task()
        self.step_count = 0
        
        # Cleanup workspace
        if os.path.exists(self.workspace):
            try:
                shutil.rmtree(self.workspace)
            except OSError:
                subprocess.run(["rm", "-rf", self.workspace])
        os.makedirs(self.workspace, exist_ok=True)
        self.current_task.setup(self.workspace)
        
        return SysObservation(
            stdout=f"Welcome to the SysAdmin Simulator.\\nTask: {self.current_task.description}\\nWorkspace: {self.workspace}",
            stderr="",
            exit_code=0,
            task_id=self.current_task.task_id,
            reward=0.0,
            done=False,
            info={}
        )

    def step(self, action: SysAction) -> SysObservation:
        self.step_count += 1
        command = action.command
        
        # Mock "systemctl restart webserver" command success explicitly if we don't want to rely solely on eval
        # However, it's evaluated in the task, so we just run bash
        
        try:
            # We enforce running in workspace
            process = subprocess.run(
                command,
                shell=True,
                cwd=self.workspace,
                capture_output=True,
                text=True,
                timeout=5
            )
            stdout = process.stdout
            stderr = process.stderr
            exit_code = process.returncode
        except subprocess.TimeoutExpired:
            stdout = ""
            stderr = "Command timed out (5s limit)."
            exit_code = 124
        except Exception as e:
            stdout = ""
            stderr = f"Execution error: {str(e)}"
            exit_code = 1
            
        reward, done = self.current_task.evaluate(command, stdout, stderr, self.workspace)
        
        # Provide small negative feedback if command failed and no task reward, to discourage bad actions
        if exit_code != 0 and reward == 0.0 and not done:
             reward = -0.05

        return SysObservation(
            stdout=stdout[:2000], # truncating to save context length
            stderr=stderr[:2000],
            exit_code=exit_code,
            task_id=self.current_task.task_id,
            reward=reward,
            done=done,
            info={}
        )

    def state_dict(self) -> SysState:
        return SysState(
            task_id=self.current_task.task_id if self.current_task else "",
            step_count=self.step_count,
            done=False
        )
