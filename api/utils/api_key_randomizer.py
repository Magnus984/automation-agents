import random

class APIKeyManager:
    def __init__(self, api_keys):
        if not api_keys:
            raise ValueError("API keys list cannot be empty")
        self.api_keys = api_keys
        self.remaining_keys = []
        self._shuffle_keys()
    
    def _shuffle_keys(self):
        """Shuffle and reset the remaining keys."""
        self.remaining_keys = self.api_keys[:]
        random.shuffle(self.remaining_keys)

    def get_key(self):
        """Get a random key without repetition until all are used."""
        if not self.remaining_keys:
            self._shuffle_keys()  # Reshuffle when all keys are used
        return self.remaining_keys.pop()
