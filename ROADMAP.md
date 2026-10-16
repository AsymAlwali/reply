# 🗺️ reply Product Engineering Roadmap

The strategy to scale `reply` into the ultimate zero-syntax local agent beast.

---

## 🟩 Phase 1: Modular Foundations & Resilient Core (Current Milestone)
- [x] Separate CLI routing layer from backend Engine execution
- [x] Eradicate bloated wrappers (`litellm`) and move to explicit, transparent native APIs
- [x] Implement the **Offline Sandbox Guard** to absorb connection drops (`Errno 7`) cleanly
- [x] Launch the interactive, plain-English `./reply.py build` wizard

## 🟨 Phase 2: The Pocket Engine & Capability Seed DNA (Next Up)
- [ ] Implement `PocketContext` token pruner to cut execution costs in half
- [ ] Connect `PocketMemory` transaction logs so agents learn from past sessions
- [ ] Inject `Capability Seeds` natively into conversational prompts to allow code writing, patching, and file manipulation

## 🟦 Phase 3: The Complete Desktop & Non-Tech Scaling Matrix
- [ ] Create an Execution Sandbox (`[Seed: RunCommand]`) so agents can test the Python scripts they forge
- [ ] Build a lightweight Electron/Tauri desktop companion app for non-technical users
- [ ] Create a local enterprise security folder isolator to safely run loops on proprietary internal directories
