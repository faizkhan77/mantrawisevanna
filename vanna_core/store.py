# vanna_core/store.py

class PreferenceStore:
    def __init__(self):
        # Dictionary to hold prefs: {'user_id': {'key': 'value'}}
        self._store = {}

    def get_prefs(self, user_id: str) -> dict:
        return self._store.get(user_id, {})

    def update_prefs(self, user_id: str, prefs: dict):
        self._store[user_id] = prefs

# Global Singleton Instance
preference_store = PreferenceStore()