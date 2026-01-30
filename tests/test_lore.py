import unittest
import sys
import os

# Add src to sys.path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from modules.lore import WorldBible, LoreFragment

class TestWorldBible(unittest.TestCase):
    def setUp(self):
        self.fragments = [
            LoreFragment(id="1", category="cat1", content="c1", tags=["tag1", "tag2"]),
            LoreFragment(id="2", category="cat2", content="c2", tags=["tag2", "tag3"]),
            LoreFragment(id="3", category="cat3", content="c3", tags=["tag3", "tag4"]),
            LoreFragment(id="4", category="cat4", content="c4", tags=["tag5"]),
            LoreFragment(id="5", category="cat5", content="c5", tags=[])
        ]
        self.world_db = WorldBible(
            world_name="Test World",
            global_lore=self.fragments,
            factions={}
        )

    def test_query_lore_intersection(self):
        # tag2 matches fragment 1 and 2
        result = self.world_db.query_lore(["tag2"])
        self.assertEqual(len(result), 2)
        ids = [f.id for f in result]
        self.assertIn("1", ids)
        self.assertIn("2", ids)

    def test_query_lore_multiple_tags(self):
        # tag1 (frag 1) and tag5 (frag 4)
        result = self.world_db.query_lore(["tag1", "tag5"])
        self.assertEqual(len(result), 2)
        ids = [f.id for f in result]
        self.assertIn("1", ids)
        self.assertIn("4", ids)

    def test_query_lore_no_intersection(self):
        result = self.world_db.query_lore(["non_existent_tag"])
        self.assertEqual(len(result), 0)

    def test_query_lore_empty_query(self):
        result = self.world_db.query_lore([])
        self.assertEqual(len(result), 0)

    def test_query_lore_fragment_no_tags(self):
        # Fragment 5 has no tags, so it should never match unless we logic changes
        result = self.world_db.query_lore(["tag1", "tag2", "tag3", "tag4", "tag5"])
        ids = [f.id for f in result]
        self.assertNotIn("5", ids)

if __name__ == '__main__':
    unittest.main()
