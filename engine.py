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
    "@fetcher": "You are @fetcher. Your job is to extract raw data from files, text, or inputs.",
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
    """Saves a custom agent's system prompt to the local storage."""
    if not handle.startswith("@"):
        handle = f"@{handle}"
    agent_file = AGENTS_DIR / f"{handle[1:]}.json"
    with open(agent_file, "w") as f:
        json.dump({"handle": handle, "system_prompt": prompt}, f, indent=4)

def make_request_with_retries(req, max_retries=5, backoff=2):
    """Executes a network request and retries if a temporary network drop happens."""
    for attempt in range(max_retries):
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                return json.loads(response.read().decode("utf-8"))
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"⚠️ Network check encountered ({e}). Retrying in {backoff} seconds... (Attempt {attempt + 1}/{max_retries})")
                time.sleep(backoff)
                backoff *= 2
            else:
                raise Exception(f"Network call failed after max attempts: {e}")

def call_native_api(config, system_prompt, user_content):
    provider = config["provider"]
    api_key = config["api_key"]
    model = config["model"]
    
    if not api_key:
        raise Exception("API key missing. Please set up your configuration first.")

    payload = {
        "contents": [{
            "parts": [{
                "text": f"System Instructions: {system_prompt}\n\nUser Request: {user_content}"
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
        
        res_data = make_request_with_retries(req)
        
        try:
            return res_data["candidates"]["content"]["parts"]["text"]
        except (KeyError, IndexError):
            raise Exception(f"Unexpected response payload structure from Gemini backend: {json.dumps(res_data)}")
            
    elif provider == "groq":
        url = "https://groq.com"
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
        groq_payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ]
        }
        
        req = urllib.request.Request(url, data=json.dumps(groq_payload).encode("utf-8"), headers=headers, method="POST")
        res_data = make_request_with_retries(req)
        return res_data["choices"]["message"]["content"]
