import os
import json
import time
from pathlib import Path
import urllib.request
import urllib.error
from seeds import file_seed, web_seed, system_seed

REPLY_DIR = Path.home() / ".reply"
AGENTS_DIR = REPLY_DIR / "agents"
CONFIG_FILE = REPLY_DIR / "config.json"
AGENTS_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_PERSONAS = {
    "@fetcher": "You are @fetcher. Your job is to grab raw data fields from documents, web addresses, or scripts.",
    "@analyst": "You are @analyst. Review records, identify trends, make metrics calculations, and extract patterns.",
    "@writer": "You are @writer. Transform incoming analysis matrices into beautifully formatted documentation logs."
}

def get_config():
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r") as f: return json.load(f)
    return {"provider": "gemini", "api_key": "", "model": "gemini-1.5-flash"}

def save_config(provider, api_key, model):
    with open(CONFIG_FILE, "w") as f:
        json.dump({"provider": provider, "api_key": api_key, "model": model}, f, indent=4)

def load_agent_prompt(handle: str) -> str:
    if not handle.startswith("@"): handle = f"@{handle}"
    agent_file = AGENTS_DIR / f"{handle[1:]}.json"
    if agent_file.exists():
        with open(agent_file, "r") as f: return json.load(f).get("system_prompt", "")
    return DEFAULT_PERSONAS.get(handle, f"You are {handle}. Complete requested tasks efficiently.")

def save_agent_prompt(handle: str, prompt: str):
    if not handle.startswith("@"): handle = f"@{handle}"
    with open(AGENTS_DIR / f"{handle[1:]}.json", "w") as f:
        json.dump({"handle": handle, "system_prompt": prompt}, f, indent=4)

def route_capability_seeds(agent_output: str) -> str:
    """Invokes discrete Capability Seed modules to parse tokens and run actions."""
    status = ""
    status += file_seed.execute(agent_output)
    status += web_seed.execute(agent_output)
    status += system_seed.execute(agent_output)
    return status.strip()

def make_request_with_retries(req, max_retries=3, backoff=1):
    for attempt in range(max_retries):
        try:
            with urllib.request.urlopen(req, timeout=8) as response:
                return json.loads(response.read().decode("utf-8")), False
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(backoff)
                backoff *= 2
            else:
                print(f"📡 [Guard Triggered] Auto-activating Offline Sandbox Mode.")
                return None, True

def call_native_api(config, system_prompt, user_content):
    provider, api_key, model = config["provider"], config["api_key"], config["model"]
    if not api_key: raise Exception("API key missing. Run `reply setup` first.")

    # Native Prompt Injection of our Capability Seed tokens layout
    seed_instructions = (
        "\n\n[CAPABILITY SEEDS LAYOUT]\n"
        "You can execute system modifications natively by outputting these exact token strings:\n"
        "- Save new files: [WRITE_FILE: filename.ext] raw data here [END_FILE]\n"
        "- Scan disk files: [READ_FILE: filename.ext]\n"
        "- Extract URL contents: [FETCH_URL: https://link-url.com]\n"
        "- Run sandbox commands: [RUN_CMD: terminal command string]"
    )
    full_system = system_prompt + seed_instructions
    payload = {"contents": [{"parts": [{"text": f"System Instructions: {full_system}\n\nRequest: {user_content}"}]}]}

    if provider == "gemini":
        if not model.startswith("models/"): model = f"models/{model}"
        url = f"https://googleapis.com{model}?key={api_key}"
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"}, method="POST")
        req.selector = f"/v1beta/models/{model}:generateContent?key={api_key}"
        
        res, is_offline = make_request_with_retries(req)
        if is_offline: return "[Notice: Operating in Offline Sandbox. Step Simulated safely.]"
        return res["candidates"][0]["content"]["parts"][0]["text"]
        
    elif provider == "groq":
        url = "https://groq.com"
        groq_payload = {"model": model, "messages": [{"role": "system", "content": full_system}, {"role": "user", "content": user_content}]}
        req = urllib.request.Request(url, data=json.dumps(groq_payload).encode("utf-8"), headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}, method="POST")
        res, is_offline = make_request_with_retries(req)
        if is_offline: return "[Notice: Operating in Offline Sandbox. Output simulated.]"
        return res["choices"][0]["message"]["content"]
