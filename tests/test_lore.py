import unittest
import sys
import os

# Add src to sys.path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from modules.lore import WorldBible, LoreFragment

class TestWorldBible(unittest.TestCase):
    def setUp(self):
        self.fragments = [
            LoreFragment(id="1", category="cat1", content="c1 content about tag1 and tag2", tags=["tag1", "tag2"]),
            LoreFragment(id="2", category="cat2", content="c2 content about tag2 and tag3", tags=["tag2", "tag3"]),
            LoreFragment(id="3", category="cat3", content="c3 content about tag3 and tag4", tags=["tag3", "tag4"]),
            LoreFragment(id="4", category="cat4", content="c4 content about tag5", tags=["tag5"]),
            LoreFragment(id="5", category="cat5", content="c5 content with no specific tags", tags=[])
        ]
        # Use in-memory DB for tests to ensure clean state and isolation
        self.world_db = WorldBible(
            world_name="Test World",
            global_lore=self.fragments,
            factions={},
            db_path=None
        )

    def test_query_lore_basic_relevance(self):
        # tag2 matches fragment 1 and 2
        result = self.world_db.query_lore(["tag2"])

        # We expect results. Since semantic search returns top 5, we expect 5 results total
        # (unless we add thresholding).
        # But we verify that 1 and 2 are present and preferably at the top.
        ids = [f.id for f in result]
        self.assertIn("1", ids)
        self.assertIn("2", ids)

        # Verify that content is correct
        f1 = next(f for f in result if f.id == "1")
        self.assertEqual(f1.content, "c1 content about tag1 and tag2")

    def test_query_lore_multiple_tags(self):
        # tag1 (frag 1) and tag5 (frag 4)
        result = self.world_db.query_lore(["tag1", "tag5"])
        ids = [f.id for f in result]
        self.assertIn("1", ids)
        self.assertIn("4", ids)

    def test_lore_ingestion_clears_list(self):
        # Verify global_lore is cleared after first query triggers ingestion
        self.assertEqual(len(self.world_db.global_lore), 5)
        self.world_db.query_lore(["test"])
        self.assertEqual(len(self.world_db.global_lore), 0)

        # Verify subsequent query works
        result = self.world_db.query_lore(["tag5"])
        ids = [f.id for f in result]
        self.assertIn("4", ids)

if __name__ == '__main__':
    unittest.main()
