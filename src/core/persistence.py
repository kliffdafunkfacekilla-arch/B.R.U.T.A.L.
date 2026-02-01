import aiofiles
import json
import os
import asyncio
from typing import Dict, Optional
from src.models.dungeon import SessionModule

# Global lock for simple concurrency safety
_io_lock = asyncio.Lock()

async def save_json(filepath: str, data: Dict):
    """Saves a dictionary to a JSON file asynchronously."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    async with _io_lock:
        async with aiofiles.open(filepath, 'w') as f:
            await f.write(json.dumps(data, indent=2))

async def load_json(filepath: str) -> Dict:
    """Loads a JSON file asynchronously."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    async with aiofiles.open(filepath, 'r') as f:
        content = await f.read()
        return json.loads(content)

async def save_session(session: SessionModule, data_dir: str = "./data/sessions"):
    """Saves a SessionModule to disk."""
    filepath = os.path.join(data_dir, f"{session.session_id}.json")
    # Convert Pydantic model to dict
    data = session.model_dump() # Use model_dump for Pydantic v2
    await save_json(filepath, data)

async def load_session(session_id: str, data_dir: str = "./data/sessions") -> SessionModule:
    """Loads a SessionModule from disk."""
    filepath = os.path.join(data_dir, f"{session_id}.json")
    data = await load_json(filepath)
    return SessionModule(**data)
