import unittest
import sys
import os
import random

# Add src to path so we can import modules
sys.path.append(os.path.join(os.getcwd(), 'src'))

from core.table_engine import TableLogicEngine

class TestTableLogicEngine(unittest.TestCase):
    def setUp(self):
        self.engine = TableLogicEngine(player_level=4, biome="dungeon")
        # Override table with a simple one for deterministic-ish tests
        self.engine.monster_tables["dungeon"] = [
            {"name": "M1", "cr": 0.5, "hp": 10, "dmg": "1"},
            {"name": "M2", "cr": 1.0, "hp": 20, "dmg": "2"},
            {"name": "M3", "cr": 2.0, "hp": 30, "dmg": "3"}
        ]

    def test_room_generation_structure(self):
        # Force random to ensure monsters are generated
        # roll > 30 means monsters.
        # random.randint(1, 100).
        # We can just loop until we get monsters or just trust luck with seed.
        random.seed(1) # Seed 1: first roll might be > 30?

        room = self.engine.generate_room_content("test_room", "medium")
        self.assertIn("id", room)
        self.assertEqual(room["id"], "test_room")
        self.assertIn("entities", room)
        self.assertIn("loot", room)
        self.assertIsInstance(room["entities"], list)

    def test_budget_adherence(self):
        # Difficulty deadly => budget = 4 * 2.5 = 10.0
        random.seed(42)

        # Run multiple times to catch edge cases
        for i in range(20):
            room = self.engine.generate_room_content(f"test_room_{i}", "deadly")

            # If no monsters, skip check
            if not room["entities"]:
                continue

            # Calculate total CR of entities
            total_cr = 0
            for entity in room["entities"]:
                name = entity["name"]
                # Find CR from table
                found_cr = 0
                for m in self.engine.monster_tables["dungeon"]:
                    if m["name"] == name:
                        found_cr = m["cr"]
                        break
                total_cr += found_cr

            initial_budget = 4 * 2.5
            self.assertLessEqual(total_cr, initial_budget, f"Total CR {total_cr} exceeded budget {initial_budget}")

if __name__ == '__main__':
    unittest.main()
