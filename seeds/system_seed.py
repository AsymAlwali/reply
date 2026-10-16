#!/usr/bin/env python3
import re
import subprocess
import shlex

def execute(agent_output: str) -> str:
    """Parses [RUN_CMD: command] and executes it inside the local terminal workspace."""
    cmd_matches = re.findall(r"\[RUN_CMD:\s*(.*?)\]", agent_output)
    status = ""

    for cmd in cmd_matches:
        cmd = cmd.strip()
        print(f"🛠️  [Seed Triggered] Executing runtime command: {cmd}")
        
        # Security Guardrail: Prevent empty commands or accidental terminal freezes
        if not cmd:
            continue
            
        try:
            # Execute terminal instruction cleanly with a hard 10-second timeout limit
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # Format logs explicitly so the next agent downstream knows exactly what happened
            status += f"\n[System Execution Logs for '{cmd}']:\n"
            if result.stdout:
                status += f"STDOUT:\n{result.stdout.strip()}\n"
            if result.stderr:
                status += f"STDERR/ERROR LOG:\n{result.stderr.strip()}\n"
            if not result.stdout and not result.stderr:
                status += "STATUS: Command completed successfully with empty output.\n"
                
        except subprocess.TimeoutExpired:
            print(f"❌ [Seed Error] Command '{cmd}' timed out after 10 seconds.")
            status += f"\n[System Timeout Error: Command '{cmd}' exceeded the safe execution limit of 10 seconds.]"
        except Exception as e:
            print(f"❌ [Seed Error] Execution failed: {e}")
            status += f"\n[System Terminal Execution Failure for '{cmd}': {e}]"

    return status
