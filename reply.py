 #!/usr/bin/env python3
import os
import sys
import json
import re
import argparse
from pathlib import Path

# Setup the local state directory (~/.reply/)
REPLY_DIR = Path.home() / ".reply"
AGENTS_DIR = REPLY_DIR / "agents"
AGENTS_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_PERSONAS = {
    "@fetcher": "You are @fetcher. Your job is to extract raw data from files, text, or inputs.",
    "@analyst": "You are @analyst. Review the data, find trends, calculate changes, and extract insights.",
    "@writer": "You are @writer. Convert insights into highly clear, beautifully formatted Markdown summaries."
}

def load_agent_prompt(handle: str) -> str:
    """Loads an agent's system prompt from disk, or bootstraps it if missing."""
    if not handle.startswith("@"):
        handle = f"@{handle}"
        
    agent_file = AGENTS_DIR / f"{handle[1:]}.json"
    
    if agent_file.exists():
        with open(agent_file, "r") as f:
            return json.load(f).get("system_prompt", "")
            
    # Fallback to default or bootstrap a dynamic new persona
    if handle in DEFAULT_PERSONAS:
        prompt = DEFAULT_PERSONAS[handle]
    else:
        print(f"✨ {handle} doesn't exist. Dynamically bootstrapping new persona...")
        prompt = f"You are {handle}. You are an expert assistant specialized in tasks related to your name. Be direct."
        
    # Save it so it persists locally
    save_agent_prompt(handle, prompt)
    return prompt

def save_agent_prompt(handle: str, prompt: str):
    """Saves an agent's system prompt to the local storage."""
    if not handle.startswith("@"):
        handle = f"@{handle}"
    agent_file = AGENTS_DIR / f"{handle[1:]}.json"
    with open(agent_file, "w") as f:
        json.dump({"handle": handle, "system_prompt": prompt}, f, indent=4)

# ==========================================
# COMMAND HANDLERS
# ==========================================

def handle_create(args):
    """Handles: reply create @name 'system prompt'"""
    handle = args.name if args.name.startswith("@") else f"@{args.name}"
    save_agent_prompt(handle, args.instruction)
    print(f"✅ Persona {handle} saved to {AGENTS_DIR / f'{handle[1:]}.json'!")

def handle_list(args):
    """Handles: reply list"""
    print("🤖 Active Local Agents:")
    print("-" * 30)
    # Check default keys plus anything written to the directory
    all_handles = set(DEFAULT_PERSONAS.keys())
    for f in AGENTS_DIR.glob("*.json"):
        all_handles.add(f"@{f.stem}")
        
    for handle in sorted(all_handles):
        agent_file = AGENTS_DIR / f"{handle[1:]}.json"
        status = "📂 Saved Local" if agent_file.exists() else "⚙️ Core Built-in"
        print(f" {handle:<15} [{status}]")

def handle_thread(args):
    """Handles: reply thread '@agent1: task @agent2: task'"""
    thread_string = args.pipeline
    # Regex splits matching '@handle: instruction' blocks sequentially
    pattern = r"(@\w+):\s*(.*?)(?=\s*@\w+:|\$)"
    matches = re.findall(pattern, thread_string)
    
    if not matches:
        print("❌ Invalid thread format. Syntax: reply thread \"@fetcher: do x @writer: do y\"")
        return
        
    current_payload = ""
    print("🚀 Running `reply` execution stream...")
    print("=" * 50)
    
    for idx, (handle, instruction) in enumerate(matches):
        system_prompt = load_agent_prompt(handle)
        print(f"\n💬 [Step {idx+1}] {handle} is executing...")
        print(f"👉 Task: {instruction.strip()}")
        
        # Integration point for your LLM SDK (OpenAI, Anthropic, or Ollama)
        # -------------------------------------------------------------
        # response = client.chat.completions.create(
        #     model="gpt-4o-mini",
        #     messages=[
        #         {"role": "system", "content": system_prompt},
        #         {"role": "user", "content": f"Task: {instruction}\nInput Data: {current_payload}"}
        #     ]
        # )
        # current_payload = response.choices[0].message.content
        # -------------------------------------------------------------
        
        # Mock payload passing forward for validation
        current_payload = f"Processed by {handle} -> ({instruction.strip()}) \n[Inherited Context: {current_payload[:40]}...]"
        print(f"✅ Context passed down the thread.")

    print("\n" + "=" * 50)
    print("🏁 Thread Complete! Final Output stream state generated.")

# ==========================================
# CLI ROUTER ENTRYPOINT
# ==========================================

def main():
    parser = argparse.ArgumentParser(description="reply: Ultra-lightweight X-style agent thread CLI.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # reply create
    parser_create = subparsers.add_parser("create", help="Create or overwrite an agent persona.")
    parser_create.add_argument("name", type=str, help="The @handle of the agent (e.g., @coder)")
    parser_create.add_argument("instruction", type=str, help="The system prompt/rules for this agent")
    
    # reply list
    subparsers.add_parser("list", help="List all available agent personas.")
    
    # reply thread
    parser_thread = subparsers.add_parser("thread", help="Run a multi-agent text thread pipeline.")
    parser_thread.add_argument("pipeline", type=str, help="The complete X-style thread string")
    
    args = parser.parse_args()
    
    if args.command == "create":
        handle_create(args)
    elif args.command == "list":
        handle_list(args)
    elif args.command == "thread":
        handle_thread(args)

if __name__ == "__main__":
    main()

