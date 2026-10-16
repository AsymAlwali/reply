import re
import subprocess

def execute(agent_output: str) -> str:
    cmd_matches = re.findall(r"\[RUN_CMD:\s*(.*?)\]", agent_output)
    status = ""

    for cmd in cmd_matches:
        cmd = cmd.strip()
        print(f"🛠️  [Seed Triggered] Executing system runtime request: {cmd}")
        try:
            # Run terminal instruction cleanly and grab stdout logs safely
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
            status += f"\n[System Executed '{cmd}':\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}]"
        except Exception as e:
            status += f"\n[System Terminal Execution Failure for '{cmd}': {e}]"

    return status
