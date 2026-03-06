"""
data/repositories/card_order_repository.py

Saves and loads card display order per pane.
Stored in card_order.json in the data directory.

Format:
{
    "account_balances": ["acc-001", "acc-002", "acc-003"],
    "assets":           ["ast-001", "ast-002"],
    "liabilities":      ["lib-001"],
    "budget":           ["cat-001", "cat-002", "cat-003"],
    "savings_goals":    ["cat-001", "cat-002"]
}
"""
import json
from pathlib import Path


class CardOrderRepository:
    """Repository: Manages card display order persistence."""

    FILE_NAME = "card_order.json"

    def __init__(self, data_dir):
        self.data_dir = Path(data_dir)
        self.file_path = self.data_dir / self.FILE_NAME

    def get_order(self, pane_key: str) -> list:
        """
        Return saved card order for a pane.
        Returns [] if no order saved yet.
        """
        data = self._load()
        return data.get(pane_key, [])

    def save_order(self, pane_key: str, order: list):
        """Persist card order for a pane."""
        data = self._load()
        data[pane_key] = order
        with open(self.file_path, 'w') as f:
            json.dump(data, f, indent=2)

    def clear_pane(self, pane_key: str):
        """Remove saved order for a pane (resets to default)."""
        data = self._load()
        if pane_key in data:
            del data[pane_key]
            with open(self.file_path, 'w') as f:
                json.dump(data, f, indent=2)

    def _load(self) -> dict:
        if self.file_path.exists():
            try:
                with open(self.file_path, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}
