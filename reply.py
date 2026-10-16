#!/usr/bin/env python3
import re
import argparse
import engine

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
    print("-" * 30)
    all_handles = set(engine.DEFAULT_PERSONAS.keys())
    for f in engine.AGENTS_DIR.glob("*.json"):
        all_handles.add(f"@{f.stem}")
    for handle in sorted(all_handles):
        print(f" {handle}")

def main():
    parser = argparse.ArgumentParser(description="reply: Plug-and-play agent thread CLI.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    subparsers.add_parser("setup", help="Configure provider and API keys interactively.")
    subparsers.add_parser("list", help="List all available agent personas.")
    
    parser_thread = subparsers.add_parser("thread", help="Run multi-agent text thread.")
    parser_thread.add_argument("pipeline", type=str, help="The thread string")
    
    args = parser.parse_args()
    
    if args.command == "setup":
        handle_setup(args)
    elif args.command == "list":
        handle_list(args)
    elif args.command == "thread":
        handle_thread(args)

if __name__ == "__main__":
    main()
