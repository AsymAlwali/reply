import argparse
import re
import os
import sys
from pathlib import Path

# Fix relative imports for child sub-folders
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core import engine
from pocket import context, memory, db

def handle_setup(args):
    print("🛠️  REPLY PLUG-AND-PLAY SETUP")
    print("=" * 40)
    print("Choose your AI Provider:\n1. Google Gemini (Studio Key)\n2. Groq\n3. OpenAI")
    choice = input("Select number (1-3): ").strip()
    api_key = input("Paste your API Key: ").strip()
    
    if choice == "1":
        provider, model = "gemini", "gemini-1.5-flash"
    elif choice == "2":
        provider, model = "groq", "llama-3.3-70b-versatile"
    else:
        provider, model = "openai", "gpt-4o-mini"
        
    engine.save_config(provider, api_key, model)
    print(f"\n✅ Saved! Using provider [{provider}] with model [{model}].")

def handle_build(args):
    print("🦖 REPLY LOCAL AGENT BUILDER")
    print("=" * 40)
    name = input("Give your agent a @handle (e.g., @coder): ").strip()
    if not name.startswith("@"):
        name = f"@{name}"
        
    role = input(f"🧠 What is the main purpose/role of {name}?: ").strip()
    constraints = input(f"📝 Add specific operational constraints for {name}: ").strip()
    
    system_prompt = f"You are {name}. Role: {role}. Instructions: {constraints} Be direct and efficient."
    engine.save_agent_prompt(name, system_prompt)
    print(f"\n✨ SUCCESS! {name} has been forged and saved to your local agent database.")

def handle_chat(args):
    handle = args.name if args.name.startswith("@") else f"@{args.name}"
    config = engine.get_config()
    system_prompt = engine.load_agent_prompt(handle)
    
    print(f"💬 Opening live session with {handle} [{config['provider']}]")
    print("Type 'exit' or 'quit' to close the room.\n" + "=" * 50)
    
    session_ctx = context.PocketContext()
    session_mem = memory.PocketMemory()
    
    while True:
        try:
            user_input = input(f"\n✨ You: ").strip()
            if not user_input: continue
            if user_input.lower() in ["exit", "quit"]: break
                
            print(f"🤖 {handle} is thinking...")
            packed_context = session_ctx.get_pruned_snapshot(user_input)
            response = engine.call_native_api(config, system_prompt, packed_context)
            
            # Auto-run capability seeds hooks if any are returned
            tool_feedback = engine.route_capability_seeds(response)
            if tool_feedback:
                response += f"\n\n{tool_feedback}"
                
            print(f"\n🤖 {handle}:\n{response}")
            session_ctx.update_state(user_input, response)
            session_mem.log_transaction(handle, user_input, response)
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def handle_thread(args):
    config = engine.get_config()
    thread_string = args.pipeline
    pattern = r"(@\w+):\s*(.*?)(?=\s*@\w+:|\$)"
    matches = re.findall(pattern, thread_string)
    
    if not matches:
        print("❌ Invalid format. Use: reply thread \"@fetcher: do x @writer: do y\"")
        return
        
    current_payload = ""
    print(f"🚀 Running `reply` stream via explicit provider [{config['provider']}]...\n" + "=" * 50)
    
    for idx, (handle, instruction) in enumerate(matches):
        system_prompt = engine.load_agent_prompt(handle)
        print(f"\n💬 [Step {idx+1}] {handle} executing...")
        
        try:
            user_content = f"Task: {instruction.strip()}\n\nInput Context: {current_payload}"
            raw_response = engine.call_native_api(config, system_prompt, user_content)
            
            tool_feedback = engine.route_capability_seeds(raw_response)
            current_payload = raw_response + (f"\n\n{tool_feedback}" if tool_feedback else "")
            print(f"✅ {handle} complete.")
        except Exception as e:
            print(f"❌ API Error: {e}")
            return

    print("\n" + "=" * 50 + "\n🏁 Thread Complete! Final Output Stream State:")
    print(current_payload)

def handle_list(args):
    print("🤖 Active Local Agents:\n" + "-" * 40)
    all_handles = set(engine.DEFAULT_PERSONAS.keys())
    for f in engine.AGENTS_DIR.glob("*.json"):
        all_handles.add(f"@{f.stem}")
    for handle in sorted(all_handles):
        status = "Custom Local" if (engine.AGENTS_DIR / f"{handle[1:]}.json").exists() else "Core Built-in"
        print(f" 🦖 {handle:<15} [{status}]")

def main():
    parser = argparse.ArgumentParser(description="reply: Zero-setup natural language local agent CLI.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("setup")
    subparsers.add_parser("build")
    subparsers.add_parser("list")
    
    parser_chat = subparsers.add_parser("chat")
    parser_chat.add_argument("name", type=str)
    
    parser_thread = subparsers.add_parser("thread")
    parser_thread.add_argument("pipeline", type=str)
    
    args = parser.parse_args()
    if args.command == "setup": handle_setup(args)
    elif args.command == "build": handle_build(args)
    elif args.command == "list": handle_list(args)
    elif args.command == "chat": handle_chat(args)
    elif args.command == "thread": handle_thread(args)
