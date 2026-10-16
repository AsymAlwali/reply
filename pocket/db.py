import json
from pathlib import Path

class PocketDB:
    def __init__(self, table_name="default_store"):
        self.db_path = Path.home() / ".reply" / f"db_{table_name}.json"
        if not self.db_path.exists():
            self.db_path.write_text(json.dumps({}))

    def write_record(self, key: str, value):
        data = json.loads(self.db_path.read_text())
        data[key] = value
        self.db_path.write_text(json.dumps(data, indent=4))

    def read_record(self, key: str):
        data = json.loads(self.db_path.read_text())
        return data.get(key, None)
