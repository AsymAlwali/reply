#!/usr/bin/env python3
import re
import argparse
import engine
import json

def handle_setup(args):
    print("🛠️  REPLY PLUG-AND-PLAY SETUP")
    print("=" * 40)
    print("Choose your AI Provider:")
    print("1. Google Gemini (Studio Key)")
    print("2. Groq")
    print("3. OpenAI")
    
    choice = input("Select number (1-3): ").strip()
    api_key = input("Paste your API Key: ").strip()
    
    if choice == "1":
        provider = "gemini"
        model = "gemini-1.5-flash"
    elif choice == "2":
        provider = "groq"
        model = "llama-3.3-70b-versatile"
    else:
        provider = "openai"
        model = "gpt-4o-mini"
        
    engine.save_config(provider, api_key, model)
    print(f"\n✅ Saved! Using provider [{provider}] with model [{model}].")

def handle_build(args):
    print("🦖 REPLY LOCAL AGENT BUILDER")
    print("=" * 40)
    
    name = input("Give your agent a @handle (e.g., @coder): ").strip()
    if not name.startswith("@"):
        name = f"@{name}"
        
    print(f"\n🧠 What is the main purpose/role of {name}?")
    role = input("Describe role (e.g., Expert Python engineer who writes bug-free scripts): ").strip()
    
    print(f"\n📝 Add specific rules or operational constraints for {name}:")
    constraints = input("Constraints (e.g., Only return clean code blocks without conversational text): ").strip()
    
    # Compile the final system instructions cleanly
    system_prompt = f"You are {name}. Role: {role}. Instructions: {constraints} Be direct and efficient."
    
    engine.save_agent_prompt(name, system_prompt)
    print(f"\n✨ SUCCESS! {name} has been forged and saved to your local agent database.")
    print("Type `./reply.py list` to view your team.")

def handle_thread(args):
    config = engine.get_config()
    thread_string = args.pipeline
    pattern = r"(@\w+):\s*(.*?)(?=\s*@\w+:|\$)"
    matches = re.findall(pattern, thread_string)
    
    if not matches:
        print("❌ Invalid format. Use: reply thread \"@fetcher: do x @writer: do y\"")
        return
        
    current_payload = ""
    print(f"🚀 Running `reply` stream via explicit provider [{config['provider']}]...")
    print("=" * 50)
    
    for idx, (handle, instruction) in enumerate(matches):
        system_prompt = engine.load_agent_prompt(handle)
        print(f"\n💬 [Step {idx+1}] {handle} executing...")
        
        try:
            user_content = f"Task: {instruction.strip()}\n\nInput Context: {current_payload}"
            current_payload = engine.call_native_api(config, system_prompt, user_content)
            print(f"✅ {handle} complete.")
        except Exception as e:
            print(f"❌ API Error: {e}")
            return

    print("\n" + "=" * 50)
    print("🏁 Thread Complete! Final Output:")
    print(current_payload)

def handle_list(args):
    print("🤖 Active Local Agents:")
    print("-" * 40)
    
    # List core default agents
    for handle, prompt in engine.DEFAULT_PERSONAS.items():
        print(f" ⚙️  {handle:<15} [Core Built-in]")
        
    # Read custom forged agents from your disk directory
    for f in engine.AGENTS_DIR.glob("*.json"):
        handle = f"@{f.stem}"
        if handle not in engine.DEFAULT_PERSONAS:
            print(f" 🦖 {handle:<15} [Forged Custom Local]")

def main():
    parser = argparse.ArgumentParser(description="reply: Plug-and-play agent creation CLI.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    subparsers.add_parser("setup", help="Configure provider and API keys interactively.")
    subparsers.add_parser("build", help="Launch the interactive local agent builder wizard.")
    subparsers.add_parser("list", help="List all available agent personas.")
    
    parser_thread = subparsers.add_parser("thread", help="Run multi-agent text thread pipeline.")
    parser_thread.add_argument("pipeline", type=str, help="The complete X-style thread string")
    
    args = parser.parse_args()
    
    if args.command == "setup":
        handle_setup(args)
    elif args.command == "build":
        handle_build(args)
    elif args.command == "list":
        handle_list(args)
    elif args.command == "thread":
        handle_thread(args)

if __name__ == "__main__":
    main()
