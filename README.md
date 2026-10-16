# 🦖 reply — Build Local Agents via Plain English

> Stop building agents the *hardcore* way. No massive frameworks. No heavy setups. Just type your intent and deploy an autonomous workspace workforce.

---

## ⚡ The Shift: Why `reply` Rules
The agent world is broken. Heavy enterprise pipelines force you into writing endless boilerplates or uploading your local folders into expensive cloud dashboards. **`reply` changes the game.** You talk to it like a friend on X, and it drives your computer natively under a resilient, lightweight local wrapper.

```bash
# Forge a custom agent instantly using plain English
reply build

# Launch an X-style multi-agent group chat execution thread
reply thread "@fetcher: read log.txt @maker: patch the bugs @writer: summarize the diff $"
```

---

## 🧠 Core Architecture Pillars

### 1. The Pocket Suite
* **`PocketContext`**: Holds a live, high-signal state snapshot. It automatically prunes raw chatter so context windows never bloat or drain your wallet.
* **`PocketMemory`**: A searchable, chronological log checkpoint system. Agents look backward to remember how they solved a similar task yesterday.
* **`PocketDB`**: A light, native JSON structured storage matrix that handles data storage right on your device disk.

### 2. Capability Seeds (Not "Skills")
Forget mapping rigid API schemas or typing out complex JSON templates. **Capability Seeds** are small, plain-English "DNA packets" injected into an agent profile. Agents invoke them organically mid-conversation using simple token cues:
* `[Seed: WriteFile]` 💾
* `[Seed: FetchURL]` 🌐
* `[Seed: RunCommand]` 🛠️

---

## 🛠️ Instant Installation
```bash
git clone https://github.com
cd reply
chmod +x reply.py
./reply.py setup
```
