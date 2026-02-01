import json
import os
from src.models.dungeon import SessionModule, RoomNode, RoomType, EntityStats

class SessionManager:
    def __init__(self, session_dir: str = "data/sessions"):
        self.session_dir = session_dir
        os.makedirs(self.session_dir, exist_ok=True)

    def load_session(self, session_id: str) -> SessionModule:
        file_path = os.path.join(self.session_dir, f"{session_id}.json")
        if os.path.exists(file_path):
            try:
                with open(file_path, "r") as f:
                    data = json.load(f)
                return SessionModule(**data)
            except (json.JSONDecodeError, ValueError) as e:
                print(f"Error loading session {session_id}: {e}")
                return self.create_default_session(session_id)
        else:
            return self.create_default_session(session_id)

    def save_session(self, session: SessionModule):
        file_path = os.path.join(self.session_dir, f"{session.session_id}.json")
        with open(file_path, "w") as f:
            f.write(session.model_dump_json(indent=2))

    def create_default_session(self, session_id: str) -> SessionModule:
        # Create the hardcoded room from game_loop.py, but using proper models
        room_01 = RoomNode(
            id="room_01",
            title="Damp Crypt",
            type=RoomType.CHAMBER,
            description_initial="A cold, damp crypt.",
            description_cleared="A cold, damp crypt, now silent.",
            exits={"north": "room_02"},
            entities=[
                EntityStats(
                    name="goblin_01",
                    hp_current=10,
                    hp_max=10,
                    ac=12,
                    attacks=[{"name": "Scimitar", "dmg": "1d6+2"}]
                )
            ]
        )

        session = SessionModule(
            session_id=session_id,
            location_name="Starter Dungeon",
            dungeon_level=1,
            rooms={"room_01": room_01}
        )

        self.save_session(session)
        return session
