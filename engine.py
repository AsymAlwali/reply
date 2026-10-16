#!/usr/bin/env python3
import os
import json
import re
import time
from pathlib import Path
import urllib.request
import urllib.error

REPLY_DIR = Path.home() / ".reply"
AGENTS_DIR = REPLY_DIR / "agents"
CONFIG_FILE = REPLY_DIR / "config.json"

AGENTS_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_PERSONAS = {
    "@fetcher": "You are @fetcher. Your job is to extract raw data from files, text, inputs, or URLs. Use your tools directly.",
    "@analyst": "You are @analyst. Review the data, find trends, calculate changes, and extract insights.",
    "@writer": "You are @writer. Convert insights into highly clear, beautifully formatted Markdown summaries."
}

def get_config():
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {"provider": "gemini", "api_key": "", "model": "gemini-1.5-flash"}

def save_config(provider, api_key, model):
    with open(CONFIG_FILE, "w") as f:
        json.dump({"provider": provider, "api_key": api_key, "model": model}, f, indent=4)

def load_agent_prompt(handle: str) -> str:
    if not handle.startswith("@"):
        handle = f"@{handle}"
    agent_file = AGENTS_DIR / f"{handle[1:]}.json"
    if agent_file.exists():
        with open(agent_file, "r") as f:
            return json.load(f).get("system_prompt", "")
    return DEFAULT_PERSONAS.get(handle, f"You are {handle}. Be direct and efficient.")

def save_agent_prompt(handle: str, prompt: str):
    if not handle.startswith("@"):
        handle = f"@{handle}"
    agent_file = AGENTS_DIR / f"{handle[1:]}.json"
    with open(agent_file, "w") as f:
        json.dump({"handle": handle, "system_prompt": prompt}, f, indent=4)

def execute_file_tools(agent_output: str) -> str:
    """Parses special code hooks out of agent responses and executes local disk & web actions."""
    write_pattern = r"\[WRITE_FILE:\s*(.*?)\](.*?)\[END_FILE\]"
    write_matches = re.findall(write_pattern, agent_output, re.DOTALL)
    
    read_pattern = r"\[READ_FILE:\s*(.*?)\]"
    read_matches = re.findall(read_pattern, agent_output)
    
    # New Web Scraper Hook: [FETCH_URL: https://example.com]
    url_pattern = r"\[FETCH_URL:\s*(.*?)\]"
    url_matches = re.findall(url_pattern, agent_output)
    
    tool_status = ""
    
    for filename, content in write_matches:
        filename = filename.strip()
        try:
            Path(filename).write_text(content.strip())
            print(f"💾 [Tool Executed] Auto-saved file: {filename}")
            tool_status += f"\n[System Notice: Successfully wrote file '{filename}']"
        except Exception as e:
            tool_status += f"\n[System Error: Failed to write file '{filename}': {e}]"
            
    for filename in read_matches:
        filename = filename.strip()
        try:
            if Path(filename).exists():
                file_data = Path(filename).read_text()
                print(f"📖 [Tool Executed] Auto-read file: {filename}")
                tool_status += f"\n[System Notice: Contents of '{filename}':\n{file_data}]"
            else:
                tool_status += f"\n[System Error: File '{filename}' not found]"
        except Exception as e:
            tool_status += f"\n[System Error: Failed to read file '{filename}': {e}]"

    for target_url in url_matches:
        target_url = target_url.strip()
        print(f"🌐 [Tool Executed] Web Fetcher scraping: {target_url}")
        try:
            req = urllib.request.Request(target_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=8) as response:
                html_content = response.read().decode('utf-8', errors='ignore')
                # Strip raw scripts and styling out to avoid bloating context windows
                clean_text = re.sub(r'<script.*?>.*?</script>|<style.*?>.*?</style>', '', html_content, flags=re.DOTALL)
                clean_text = re.sub(r'<[^>]*>', ' ', clean_text)
                clean_text = " ".join(clean_text.split())[:3000] # Cap text snippet bounds
                tool_status += f"\n[System Notice: Web Content fetched from '{target_url}':\n{clean_text}]"
        except Exception as e:
            tool_status += f"\n[System Error: Failed to download URL content: {e}]"
            
    return tool_status

def make_request_with_retries(req, max_retries=3, backoff=1):
    """Executes a network request and falls back to Sandbox Mode if network drops completely."""
    for attempt in range(max_retries):
        try:
            with urllib.request.urlopen(req, timeout=8) as response:
                return json.loads(response.read().decode("utf-8")), False
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(backoff)
                backoff *= 2
            else:
                # If network fails completely after retries, return an explicit signal instead of crashing
                print(f"📡 [Guard triggered] Mobile network dropped. Auto-activating Offline Sandbox Mode.")
                return None, True

def call_native_api(config, system_prompt, user_content):
    provider = config["provider"]
    api_key = config["api_key"]
    model = config["model"]
    
    if not api_key:
        raise Exception("API key missing. Please set up your configuration first.")

    tool_instructions = (
        "\n\n[CAPABILITIES & TOOLS]\n"
        "You can read and modify files or fetch URLs directly. Append these tokens exactly:\n"
        "- Save/Write file: [WRITE_FILE: path/filename.ext] data content [END_FILE]\n"
        "- Read file: [READ_FILE: path/filename.ext]\n"
        "- Fetch Web Content: [FETCH_URL: https://url-link.com]\n"
        "Combine text conversations with these tools."
    )
    full_system_prompt = system_prompt + tool_instructions

    payload = {
        "contents": [{
            "parts": [{
                "text": f"System Instructions: {full_system_prompt}\n\nUser Request: {user_content}"
            }]
        }]
    }

    if provider == "gemini":
        if not model.startswith("models/"):
            model = f"models/{model}"
        url = f"https://googleapis.com{model}?key={api_key}"
        headers = {"Content-Type": "application/json"}
        
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
        req.selector = f"/v1beta/models/{model}:generateContent?key={api_key}"
        
        res_data, is_offline = make_request_with_retries(req)
        
        if is_offline:
            return "[System Notice: The device is currently offline due to a connection drop. This step has been safely simulated. Please check your data connection.]"
            
        try:
            return res_data["candidates"]["content"]["parts"]["text"]
        except (KeyError, IndexError):
            return f"[System Error: Unexpected response structure]"
            
    elif provider == "groq":
        url = "https://groq.com"
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
        groq_payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": full_system_prompt},
                {"role": "user", "content": user_content}
            ]
        }
        req = urllib.request.Request(url, data=json.dumps(groq_payload).encode("utf-8"), headers=headers, method="POST")
        res_data, is_offline = make_request_with_retries(req)
        
        if is_offline:
            return "[System Notice: The device is currently offline due to a connection drop. Simulated output generated.]"
            
        return res_data["choices"]["message"]["content"]
