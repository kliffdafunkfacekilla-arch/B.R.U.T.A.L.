import random
from typing import List, Dict

class TableLogicEngine:
    def __init__(self, player_level: int, biome: str):
        self.player_level = player_level
        self.biome = biome

        # --- STATIC DATA TABLES (The "Rulebooks") ---
        self.monster_tables = {
            "dungeon": [
                {"name": "Goblin Scavenger", "cr": 0.25, "hp": 7, "ac": 12, "dmg": "1d6", "attacks": [{"name": "Scimitar", "dmg": "1d6+2"}]},
                {"name": "Skeleton Warrior", "cr": 0.5, "hp": 13, "ac": 13, "dmg": "1d8", "attacks": [{"name": "Shortsword", "dmg": "1d6+2"}]},
                {"name": "Orc Grunt", "cr": 1, "hp": 15, "ac": 13, "dmg": "1d12+2", "attacks": [{"name": "Greataxe", "dmg": "1d12+3"}]}
            ],
            "crypt": [
                {"name": "Zombie", "cr": 0.25, "hp": 22, "ac": 8, "dmg": "1d6+1", "attacks": [{"name": "Slam", "dmg": "1d6+1"}]},
                {"name": "Ghoul", "cr": 1, "hp": 22, "ac": 12, "dmg": "2d4+2", "attacks": [{"name": "Claws", "dmg": "2d4+2"}]}
            ]
        }

        self.loot_table = [
            {"name": "Rusted Dagger", "value_gp": 1, "description": "A worn dagger.", "is_magical": False},
            {"name": "Gold Pouch", "value_gp": 10, "description": "A pouch containing 10gp.", "is_magical": False},
            {"name": "Gemstone", "value_gp": 50, "description": "A shiny ruby.", "is_magical": False},
            {"name": "Potion of Healing", "value_gp": 25, "description": "A red liquid.", "is_magical": True}
        ]

    def _calculate_encounter_budget(self, difficulty: str) -> float:
        """Determines how much 'XP' available to spend on monsters."""
        base_budget = self.player_level * 1.0
        multipliers = {"easy": 0.5, "medium": 1.0, "hard": 1.5, "deadly": 2.5}
        return base_budget * multipliers.get(difficulty, 1.0)

    def generate_room_content(self, room_id: str, difficulty: str = "medium") -> Dict:
        """
        The Core Logic:
        1. Decide if monsters exist (33% chance empty).
        2. If yes, spend 'Budget' to buy monsters from the table.
        3. Roll for loot.
        """
        room_data = {
            "id": room_id,
            "entities": [],
            "loot": [],
            "description_tags": []
        }

        # 1. Encounter Roll (Table Flow)
        roll = random.randint(1, 100)

        if roll > 30: # 70% chance of monsters
            budget = self._calculate_encounter_budget(difficulty)
            available_monsters = self.monster_tables.get(self.biome, [])

            current_cost = 0.0

            # Simple greedy algorithm to fill the room
            while budget > 0.25:
                # Filter monsters we can afford
                affordable = [m for m in available_monsters if m['cr'] <= budget]
                if not affordable:
                    break

                choice = random.choice(affordable)

                # Add to room
                room_data["entities"].append({
                    "name": choice["name"],
                    "hp_current": choice["hp"],
                    "hp_max": choice["hp"],
                    "ac": choice.get("ac", 10),
                    "attacks": choice.get("attacks", [])
                })

                budget -= choice['cr']
                room_data["description_tags"].append(f"contains {choice['name']}")
        else:
            room_data["description_tags"].append("is quiet and empty")

        # 2. Loot Roll (Table Flow)
        if random.random() < 0.5: # 50% chance of loot
            loot_item = random.choice(self.loot_table)
            # Adapt legacy keys if needed, but we updated the table
            room_data["loot"].append(loot_item)
            room_data["description_tags"].append(f"has {loot_item['name']}")

        return room_data

    def process_player_action(self, action_type: str, room_data: Dict) -> str:
        """
        Runtime Logic: Updates the JSON based on player action.
        """
        if action_type == "search":
            if room_data["loot"]:
                found = room_data["loot"].pop(0) # Remove from JSON
                return f"You search the room and find a {found['name']}!"
            else:
                return "You search thoroughly but find nothing of value."

        elif action_type == "attack":
            if room_data["entities"]:
                target = room_data["entities"][0]
                dmg = random.randint(1, 8) # Simulating player roll
                target["hp_current"] -= dmg # Update JSON

                status = "is dead" if target["hp_current"] <= 0 else "is wounded"
                if target["hp_current"] <= 0:
                    room_data["entities"].pop(0) # Remove dead monster

                return f"You hit the {target['name']} for {dmg} damage! It {status}."
            else:
                return "There is nothing here to attack."

        return "I don't understand that action."
