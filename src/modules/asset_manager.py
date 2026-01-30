import hashlib
import json
import os
import urllib.request
from typing import Optional, Dict

class AssetCacheManager:
    """
    The Librarian for your media files.
    Ensures we never generate the same thing twice.
    """

    def __init__(self, cache_dir: str = "./data/game_assets"):
        self.cache_dir = cache_dir
        self.index_file = os.path.join(cache_dir, "asset_index.json")
        self.assets = self._load_index()

        # Ensure directories exist
        os.makedirs(os.path.join(cache_dir, "images"), exist_ok=True)
        os.makedirs(os.path.join(cache_dir, "audio"), exist_ok=True)

    def _load_index(self) -> Dict:
        if os.path.exists(self.index_file):
            with open(self.index_file, 'r') as f:
                return json.load(f)
        return {"images": {}, "audio": {}, "npcs": {}}

    def _save_index(self):
        with open(self.index_file, 'w') as f:
            json.dump(self.assets, f, indent=2)

    def _generate_hash(self, text_prompt: str) -> str:
        """Creates a unique ID based on the prompt text."""
        return hashlib.md5(text_prompt.encode('utf-8')).hexdigest()

    # --- IMAGE HANDLING ---

    def get_scene_image(self, room_id: str, prompt: str, generator_func) -> str:
        """
        1. Check if Room ID has a saved image.
        2. If yes, return filepath.
        3. If no, call the AI (generator_func), save file, update index.
        """
        # Strategy A: Cache by Room ID (Persistent Location)
        if room_id in self.assets["images"]:
            print(f"[CACHE HIT] Loading existing image for {room_id}")
            return self.assets["images"][room_id]

        # Strategy B: Cache by Prompt Hash (Deduplication)
        # Useful if two rooms have identical descriptions
        prompt_hash = self._generate_hash(prompt)
        # (Optional logic to check hash could go here)

        print(f"[CACHE MISS] Generating new image for {room_id}...")

        # Call the expensive API
        image_data = generator_func(prompt)

        filename = f"{room_id}_{prompt_hash[:8]}.png"
        filepath = os.path.join(self.cache_dir, "images", filename)

        if isinstance(image_data, bytes):
            with open(filepath, 'wb') as f:
                f.write(image_data)
        elif isinstance(image_data, str):
            # Assume it's a URL
            urllib.request.urlretrieve(image_data, filepath)
        else:
            # Fallback or error handling
            print(f"[ERROR] Generator returned unknown type: {type(image_data)}")
            return ""

        # Update Index
        self.assets["images"][room_id] = filepath
        self._save_index()

        return filepath

    # --- NPC HANDLING (The Consistency Engine) ---

    def get_npc_assets(self, npc_id: str, description: str) -> Dict:
        """
        Ensures an NPC keeps their face and voice forever.
        """
        if npc_id in self.assets["npcs"]:
            return self.assets["npcs"][npc_id]

        print(f"[NEW NPC] Casting actors for {npc_id}...")

        # 1. Assign Voice (Deterministic Mapping or Random Selection)
        voice_id = "voice_en_male_deep_01" # In real app, pick based on tags

        # 2. Generate Portrait
        portrait_path = f"images/npc_{npc_id}.png"

        asset_record = {
            "voice_id": voice_id,
            "portrait_path": portrait_path,
            "description_hash": self._generate_hash(description)
        }

        self.assets["npcs"][npc_id] = asset_record
        self._save_index()

        return asset_record
