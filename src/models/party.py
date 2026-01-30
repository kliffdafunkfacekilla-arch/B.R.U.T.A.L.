from typing import List, Dict
from pydantic import BaseModel

class PlayerCharacter(BaseModel):
    id: str
    name: str
    player_name: str # The real human's name
    hp: int
    max_hp: int
    ac: int
    initiative_bonus: int
    inventory: List[Dict] = []
    conditions: List[str] = [] # "Blinded", "Prone"

class PartyState(BaseModel):
    campaign_id: str
    members: Dict[str, PlayerCharacter] # Keyed by Player ID
    current_turn_index: int = 0
    is_in_combat: bool = False

    def get_active_player(self) -> PlayerCharacter:
        member_ids = list(self.members.keys())
        active_id = member_ids[self.current_turn_index % len(member_ids)]
        return self.members[active_id]
