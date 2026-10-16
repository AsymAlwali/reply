import json
import time
from pathlib import Path

class PocketMemory:
    def __init__(self):
        self.memory_file = Path.home() / ".reply" / "memory_log.jsonl"
        self.memory_file.parent.mkdir(parents=True, exist_ok=True)

    def log_transaction(self, agent_name: str, task: str, result: str):
        log_entry = {
            "timestamp": time.time(),
            "agent": agent_name,
            "task": task,
            "result": result[:500] # Truncate bounds for clean local storage check logs
        }
        with open(self.memory_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
