import uuid
from typing import Dict, List
from src.models.dungeon import SessionModule, RoomNode, RoomType, Difficulty
from src.core.table_engine import TableLogicEngine

class MacroGenerator:
    """
    Generates the initial session structure (The 'Macro' layer).
    """

    def __init__(self):
        # In the future, this could use LLM to parse the prompt
        # for biome, difficulty, etc.
        pass

    async def generate_session(self, campaign_id: str, prompt: str) -> SessionModule:
        """
        Creates a new session based on a prompt.
        """
        session_id = f"sess_{uuid.uuid4().hex[:8]}"

        # Simple Logic: Determine biome from prompt
        biome = "crypt" # Default
        if "forest" in prompt.lower():
            biome = "forest" # Note: TableEngine only supports 'dungeon' and 'crypt' for now, checking fallback
        elif "dungeon" in prompt.lower():
            biome = "dungeon"

        # Determine Difficulty
        difficulty = "medium"

        logic_engine = TableLogicEngine(player_level=1, biome=biome)

        # Create Skeleton (Simple Linear Layout: Entry -> Hall -> Chamber)
        rooms: Dict[str, RoomNode] = {}

        # Room 1: Entry
        room_1_id = "room_01"
        room_1_content = logic_engine.generate_room_content(room_1_id, difficulty="easy")
        room_1 = RoomNode(
            id=room_1_id,
            title="Entrance",
            type=RoomType.SAFE_HAVEN,
            description_initial="You stand at the entrance.",
            description_cleared="The entrance is quiet.",
            exits={"north": "room_02"},
            entities=room_1_content["entities"],
            loot=room_1_content["loot"]
        )
        rooms[room_1_id] = room_1

        # Room 2: Hallway
        room_2_id = "room_02"
        room_2_content = logic_engine.generate_room_content(room_2_id, difficulty)
        room_2 = RoomNode(
            id=room_2_id,
            title="Dark Hallway",
            type=RoomType.CORRIDOR,
            description_initial="A long, dark hallway stretches ahead.",
            description_cleared="The hallway is empty.",
            exits={"south": "room_01", "north": "room_03"},
            entities=room_2_content["entities"],
            loot=room_2_content["loot"]
        )
        rooms[room_2_id] = room_2

        # Room 3: Chamber
        room_3_id = "room_03"
        room_3_content = logic_engine.generate_room_content(room_3_id, difficulty="hard")
        room_3 = RoomNode(
            id=room_3_id,
            title="Main Chamber",
            type=RoomType.CHAMBER,
            description_initial="A large chamber with high ceilings.",
            description_cleared="The chamber is silent, dust settling.",
            exits={"south": "room_02"},
            entities=room_3_content["entities"],
            loot=room_3_content["loot"]
        )
        rooms[room_3_id] = room_3

        # Assemble Session
        session = SessionModule(
            session_id=session_id,
            location_name=f"Generated {biome.capitalize()}",
            dungeon_level=1,
            rooms=rooms
        )

        return session
