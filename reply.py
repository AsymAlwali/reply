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
    role = input("Describe role: ").strip()
    
    print(f"\n📝 Add specific rules or operational constraints for {name}:")
    constraints = input("Constraints: ").strip()
    
    system_prompt = f"You are {name}. Role: {role}. Instructions: {constraints} Be direct and efficient."
    
    engine.save_agent_prompt(name, system_prompt)
    print(f"\n✨ SUCCESS! {name} has been forged and saved to your local agent database.")

def handle_chat(args):
    handle = args.name if args.name.startswith("@") else f"@{args.name}"
    config = engine.get_config()
    system_prompt = engine.load_agent_prompt(handle)
    
    print(f"💬 Opening live session with {handle} [{config['provider']}]")
    print("Type 'exit' or 'quit' to close the room.")
    print("=" * 50)
    
    chat_history = ""
    
    while True:
        try:
            user_input = input(f"\n✨ You: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit"]:
                print(f"👋 Closing chat session with {handle}. Room destroyed.")
                break
                
            print(f"🤖 {handle} is thinking...")
            current_context = f"{chat_history}\nUser: {user_input}" if chat_history else f"User: {user_input}"
            
            response = engine.call_native_api(config, system_prompt, current_context)
            
            # Intercept and process local file tools right during your active chat session!
            tool_feedback = engine.execute_file_tools(response)
            if tool_feedback:
                response += f"\n\n{tool_feedback}"
                
            print(f"\n🤖 {handle}:\n{response}")
            chat_history += f"\nUser: {user_input}\nAssistant: {response}"
            
        except KeyboardInterrupt:
            print(f"\n👋 Session interrupted. Goodbye!")
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
    print(f"🚀 Running `reply` stream via explicit provider [{config['provider']}]...")
    print("=" * 50)
    
    for idx, (handle, instruction) in enumerate(matches):
        system_prompt = engine.load_agent_prompt(handle)
        print(f"\n💬 [Step {idx+1}] {handle} executing...")
        
        try:
            user_content = f"Task: {instruction.strip()}\n\nInput Context: {current_payload}"
            raw_response = engine.call_native_api(config, system_prompt, user_content)
            
            # Execute tool checks and pass the tool execution results to the next agent downstream
            tool_feedback = engine.execute_file_tools(raw_response)
            current_payload = raw_response + (f"\n\n{tool_feedback}" if tool_feedback else "")
            
            print(f"✅ {handle} complete.")
        except Exception as e:
            print(f"❌ API Error: {e}")
            return

    print("\n" + "=" * 50)
    print("🏁 Thread Complete! Final Context Pipeline Payload:")
    print(current_payload)

def handle_list(args):
    print("🤖 Active Local Agents:")
    print("-" * 40)
    all_handles = set(engine.DEFAULT_PERSONAS.keys())
    for f in engine.AGENTS_DIR.glob("*.json"):
        all_handles.add(f"@{f.stem}")
    for handle in sorted(all_handles):
        status = "Custom Local" if (engine.AGENTS_DIR / f"{handle[1:]}.json").exists() else "Core Built-in"
        print(f" 🦖 {handle:<15} [{status}]")

def main():
    parser = argparse.ArgumentParser(description="reply: Plug-and-play agent creation CLI.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    subparsers.add_parser("setup", help="Configure provider and API keys interactively.")
    subparsers.add_parser("build", help="Launch the interactive local agent builder wizard.")
    subparsers.add_parser("list", help="List all available agent personas.")
    
    parser_chat = subparsers.add_parser("chat", help="Open a live 1-on-1 dialogue session with an agent.")
    parser_chat.add_argument("name", type=str, help="The @handle of the target agent")
    
    parser_thread = subparsers.add_parser("thread", help="Run multi-agent text thread pipeline.")
    parser_thread.add_argument("pipeline", type=str, help="The complete X-style thread string")
    
    args = parser.parse_args()
    
    if args.command == "setup":
        handle_setup(args)
    elif args.command == "build":
        handle_build(args)
    elif args.command == "list":
        handle_list(args)
    elif args.command == "chat":
        handle_chat(args)
    elif args.command == "thread":
        handle_thread(args)

if __name__ == "__main__":
    main()
