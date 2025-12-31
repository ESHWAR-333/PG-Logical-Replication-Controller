import json
from pathlib import Path

class StateStore:
    def __init__(self, path):
        self.path = Path(path)
        self.state = self._load()

    def _load(self):
        if self.path.exists():
            return json.loads(self.path.read_text())
        return {}

    def get(self, key):
        return self.state.get(key, {})

    def update(self, key, value):
        self.state[key] = value
        self.path.write_text(json.dumps(self.state, indent=2))
