import re
from pathlib import Path

def execute(agent_output: str) -> str:
    write_matches = re.findall(r"\[WRITE_FILE:\s*(.*?)\](.*?)\[END_FILE\]", agent_output, re.DOTALL)
    read_matches = re.findall(r"\[READ_FILE:\s*(.*?)\]", agent_output)
    status = ""

    for filename, content in write_matches:
        filename = filename.strip()
        try:
            Path(filename).write_text(content.strip())
            print(f"💾 [Seed Triggered] Successfully wrote local file: {filename}")
            status += f"\n[System Success: Wrote file '{filename}']"
        except Exception as e:
            status += f"\n[System Failure writing '{filename}': {e}]"

    for filename in read_matches:
        filename = filename.strip()
        try:
            if Path(filename).exists():
                status += f"\n[System File Content '{filename}':\n{Path(filename).read_text()}]"
            else:
                status += f"\n[System Error: '{filename}' does not exist on disk]"
        except Exception as e:
            status += f"\n[System Failure reading '{filename}': {e}]"

    return status
