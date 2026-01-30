import hashlib
import json
import os
import aiofiles
import shutil
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

    async def get_scene_image(self, room_id: str, prompt: str, generator_func) -> str:
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
        # image_url = await generator_func(prompt)
        # For this example, we simulate a downloaded file path
        filename = f"{room_id}_{prompt_hash[:8]}.png"
        filepath = os.path.join(self.cache_dir, "images", filename)

        # Simulate saving the image bytes to disk
        async with aiofiles.open(filepath, 'wb') as f:
            # await f.write(image_bytes)
            pass

        # Update Index
        self.assets["images"][room_id] = filepath
        self._save_index()

        return filepath
        generated_content = generator_func(prompt)

        filename = f"{room_id}_{prompt_hash[:8]}.png"
        filepath = os.path.join(self.cache_dir, "images", filename)

        # Save the image bytes to disk
        try:
            if isinstance(generated_content, bytes):
                with open(filepath, 'wb') as f:
                    f.write(generated_content)
            elif isinstance(generated_content, str):
                # Assume it's a URL
                # Use a proper User-Agent to avoid 403s from some servers
                req = urllib.request.Request(
                    generated_content,
                    headers={'User-Agent': 'Mozilla/5.0'}
                )
                with urllib.request.urlopen(req) as response, open(filepath, 'wb') as out_file:
                    shutil.copyfileobj(response, out_file)
            else:
                raise ValueError(f"Unexpected return type from generator_func: {type(generated_content)}")
        except Exception as e:
            print(f"[ERROR] Failed to save image: {e}")
            raise e
        try:
            # Call the expensive API
            image_url = generator_func(prompt)

            # For this example, we simulate a downloaded file path
            filename = f"{room_id}_{prompt_hash[:8]}.png"
            filepath = os.path.join(self.cache_dir, "images", filename)

            # Download the image
            with urllib.request.urlopen(image_url, timeout=30) as response:
                image_bytes = response.read()

            # Save the image bytes to disk
            with open(filepath, 'wb') as f:
                f.write(image_bytes)

            # Update Index
            self.assets["images"][room_id] = filepath
            self._save_index()

            return filepath

        except Exception as e:
            print(f"Error generating or saving image: {e}")
            raise e

    # --- NPC HANDLING (The Consistency Engine) ---

    async def get_npc_assets(self, npc_id: str, description: str) -> Dict:
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
