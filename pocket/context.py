class PocketContext:
    def __init__(self):
        self.state_turns = []

    def update_state(self, user_in: str, agent_out: str):
        self.state_turns.append({"user": user_in, "assistant": agent_out})
        # Keep only the last 3 turns to compress space and maximize token efficiency
        if len(self.state_turns) > 3:
            self.state_turns.pop(0)

    def get_pruned_snapshot(self, latest_input: str) -> str:
        snapshot = ""
        for turn in self.state_turns:
            snapshot += f"User: {turn['user']}\nAssistant: {turn['assistant']}\n"
        snapshot += f"User: {latest_input}"
        return snapshot.strip()
